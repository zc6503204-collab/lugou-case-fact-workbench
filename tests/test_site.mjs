// Test the install instruction selector and clipboard behavior without browser navigation.
import fs from 'node:fs/promises';import vm from 'node:vm';import assert from 'node:assert/strict';
import path from 'node:path';import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const script=await fs.readFile(path.join(root,'docs/assets/site.js'),'utf8');
let passed=0;const check=(message,value)=>{assert.ok(value,message);passed++};
for(const [page,id] of [['index.html','home-ai-command'],['guide.html','guide-ai-command']]){
 const html=await fs.readFile(path.join(root,'docs',page),'utf8');const nodes=new Map();
 for(const match of html.matchAll(/<(?:pre|span)[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/(?:pre|span)>/g))nodes.set(match[1],{textContent:match[2]});
 const status={textContent:''},button={dataset:{copy:id},nextElementSibling:status,events:{},addEventListener(key,fn){this.events[key]=fn}},select={dataset:{installSelect:id},value:'auto',events:{},addEventListener(key,fn){this.events[key]=fn}};
 let clipboard='',failure=false;
 const context=vm.createContext({document:{getElementById:key=>nodes.get(key),querySelector:()=>button,querySelectorAll:selector=>selector==='[data-install-select]'?[select]:[button]},navigator:{clipboard:{async writeText(text){if(failure)throw Error('not available');clipboard=text}}}});
 vm.runInContext(script,context);
 check(page+' 首页默认自动识别',nodes.get(id).textContent.includes('当前 AI 工具'));
 for(const [platform,label] of [['codex','Codex 的个人'],['workbuddy','WorkBuddy.app 的个人'],['auto','当前 AI 工具']]){
  select.value=platform;select.events.change();await button.events.click();
  check(page+' '+platform+' 平台指令正确',clipboard.includes(label));
  check(page+' '+platform+' 自有安装链接',clipboard.includes('https://zc6503204-collab.github.io/lugou-case-fact-workbench/install.md')&&(clipboard.match(/https:\/\//g)||[]).length===1);
  check(page+' '+platform+' 安装步骤完整',clipboard.includes('核验')&&clipboard.includes('备份')&&clipboard.includes('运行支持'));
  check(page+' '+platform+' 复制反馈',status.textContent==='已复制，可粘贴到对话中。');
 }
 status.textContent='上一次已复制';select.value='codex';select.events.change();check(page+' 切换清除旧复制状态',status.textContent==='');
 failure=true;await button.events.click();check(page+' 复制失败可手动复制',status.textContent==='请选中上方文字后复制。');
 select.value='invalid';select.events.change();check(page+' 无效平台回退',nodes.get(id).textContent.includes('当前 AI 工具'));
}
console.log(JSON.stringify({passed,scope:'Installation instruction selector and clipboard, both public pages'}));
