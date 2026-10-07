import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const [input,out]=process.argv.slice(2),d=JSON.parse(await fs.readFile(input,'utf8'));
d.facts.sort((a,b)=>(a.date.iso||'9999').localeCompare(b.date.iso||'9999')||a.id.localeCompare(b.id));
const wb=Workbook.create();
const names=['案件速览','材料目录','主体表','事实大事记','原文与来源','冲突与待核','更新记录'];
for(const n of names)wb.worksheets.add(n);
const font='STFangsong'; // 华文仿宋：当前 Mac 已安装的仿宋字族，标题与正文统一。
const ink='#0D0C0B',gold='#79603E',paper='#F2EFE8',line='#E4E0D7';
const M=Object.fromEntries(d.materials.map(x=>[x.id,x])),S=Object.fromEntries(d.subjects.map(x=>[x.id,x])),R=Object.fromEntries(d.citations.map(x=>[x.id,x]));
const source=id=>R[id]?R[id].material_id+' '+R[id].filename+' / '+R[id].location:id;
const literal=v=>typeof v==='string'&&v.startsWith('=')?"'"+v:v;
const hasAudio=d.materials.some(m=>m.method==='本地 MLX Whisper');
const textWidth=s=>[...s].reduce((n,c)=>n+(c.charCodeAt(0)>255?2:1),0);
const idLines=(ids,n=6)=>Array.from({length:Math.ceil(ids.length/n)},(_,i)=>ids.slice(i*n,(i+1)*n).join('、')).join('\n');
const links=[];
function linkCell(sheet,cell,href,label){
 if(!href)return;
 sheet.getRange(cell).values=[[label]];
 sheet.getRange(cell).format.font.color=gold;
 links.push({sheet:sheet.name,cell,target:decodeURIComponent(href)});
}
const styles={};
function setup(name,headers,rows,widths,tableName,reviewStart=null){
  const s=wb.worksheets.getItem(name),count=Math.max(rows.length,1);
  s.showGridLines=false;
  s.getRange('A1').values=[[name]];
  s.getRange('A1').format.font={name:font,size:16,bold:true,color:ink};
  s.getRange('A1').format.rowHeight=29;
  s.getRange('A2').values=[[d.case.name+(d.case.is_demo?'（虚构演示）':'')+'；'+d.case.updated_at.replace('T',' ').slice(0,19)]];
  s.getRange('A2').format.font={name:font,size:12,color:'#706C65'};
  const endCol=String.fromCharCode(64+headers.length),endRow=4+count;
  const area=s.getRange('A4:'+endCol+endRow);
  area.values=[headers,...(rows.length?rows:[headers.map((_,i)=>i===1?'暂无记录':null)])].map(r=>r.map(literal));
  area.format.font={name:font,size:12,color:'#46433E'};
  area.format.fill='#FFFFFF';
  area.format.wrapText=true;area.format.verticalAlignment='top';area.format.rowHeight=46;
  const table=s.tables.add('A4:'+endCol+endRow,true,tableName);table.style='TableStyleLight1';table.showFilterButton=true;
  const head=s.getRange('A4:'+endCol+'4');head.format.fill='#EDEFE7';head.format.font={name:font,size:12,bold:true,color:ink};
  head.format.rowHeight=32;
  widths.forEach((w,i)=>{
    const col=String.fromCharCode(65+i);
    s.getRange(col+'4:'+col+endRow).format.columnWidth=w;
  });
  rows.forEach((row,i)=>{
    const lines=Math.max(...row.map((v,j)=>typeof v==='string'?v.split('\n').reduce((n,l)=>n+Math.max(1,Math.ceil(textWidth(l)/Math.max(widths[j]-2,6))),0):1));
    s.getRange('A'+(5+i)+':'+endCol+(5+i)).format.rowHeight=Math.min(409,Math.max(45,lines*20+14));
  });
  if(reviewStart!==null&&rows.length){
    const col=String.fromCharCode(65+reviewStart);
    s.getRange(col+'5:'+endCol+endRow).format.fill='#F5F0E4';
    s.getRange(col+'5:'+col+endRow).dataValidation={rule:{type:'list',values:['未复核','已核对原件','需补核','存在异议']}};
  }
  s.freezePanes.freezeRows(4);s.freezePanes.freezeColumns(1);
  s.tabColor=gold;styles[name]={sheet:s,endRow,endCol};
  return s;
}

const msheet=setup('材料目录',['材料编号','材料名称','材料类别','提交批次','文件形态','读取状态','提取方式','实际页数','重复材料','原版本','读取说明','原件位置'],
 d.materials.map(m=>[m.id,m.filename,m.category||'',m.batch_id||'',m.document_form||'',m.state,m.method,m.page_count??null,m.duplicate_of||'',m.version_of||'',(m.notes||[]).join('\n'),m.source_href?'查看原件 · '+m.id:'原件缺失或内容已变更']),
 [11,34,19,15,15,23,24,10,12,12,56,22],'MaterialIndex');
d.materials.forEach((m,i)=>linkCell(msheet,'L'+(5+i),m.source_href,'查看原件 · '+m.id));
const ssheet=setup('主体表',['主体编号','原始称谓','材料中角色','其它称谓','相关材料','身份关联边界'],
 d.subjects.map(s=>[s.id,s.name,s.role,(s.aliases||[]).join('、'),idLines(s.material_ids||[]),s.identity_note||'未作额外身份推断']),
 [11,28,28,28,46,62],'SubjectIndex');
const factHeaders=['事实编号','原始时间','材料记载','复核状态','复核备注','整理分组','重点事项','主体','金额','币种','记录类型','原文引用','来源回查','可排序日期','日期精度','协议轮次','交易编号','金额角色','人工更正事实','人工更正时间','人工更正金额','人工更正币种','复核人','复核时间','核查引用'];
const fc=name=>String.fromCharCode(65+factHeaders.indexOf(name));
const fsheet=setup('事实大事记',factHeaders,
 d.facts.map(f=>[f.id,f.date.raw,f.description,f.review_status||'未复核',f.review_note||'',
  f.manual?.chronicle_group??null,typeof f.manual?.is_key==='boolean'?(f.manual.is_key?'是':'否'):null,
  (f.subject_ids||[]).map(id=>S[id]?.name||id).join('、'),f.amount??null,f.currency||'',f.kind,
  (f.citation_ids||[]).join('、'),(f.citation_ids||[]).map(id=>id+' / '+R[id]?.material_id).join('\n'),f.date.precision==='day'?new Date(f.date.iso+'T00:00:00Z'):null,f.date.precision,
  f.agreement_round||'',f.transaction_id||'',f.amount_role||'',f.manual?.description??null,f.manual?.date_raw??null,f.manual?.amount??null,f.manual?.currency??null,f.reviewed_by||'',f.reviewed_at||'',(f.checked_citation_ids||[]).join('、')]),
 [11,24,58,17,34,24,12,28,19,9,15,19,20,16,11,16,24,17,45,23,19,15,18,26,22],'FactTimeline');
fsheet.freezePanes.freezeColumns(2);
if(d.facts.length){
 for(const name of ['复核状态','复核备注','整理分组','重点事项','人工更正事实','人工更正时间','人工更正金额','人工更正币种','复核人','复核时间','核查引用']){const col=fc(name);fsheet.getRange(col+'5:'+col+(4+d.facts.length)).format.fill='#F7F3E9';}
 fsheet.getRange('D5:D'+(4+d.facts.length)).dataValidation={rule:{type:'list',values:['未复核','已核对原件','需补核','存在异议']}};
 links.push({sheet:'事实大事记',cell:'G5:G'+(4+d.facts.length),validation_allow_blank:true});
 fsheet.getRange('G5:G'+(4+d.facts.length)).dataValidation={allowBlank:true,rule:{type:'list',values:['是','否']},errorAlert:{style:'stop',title:'重点事项',message:'请选择是或否；留空不新增人工决定。'}};
 fsheet.getRange(fc('可排序日期')+'5:'+fc('可排序日期')+(4+d.facts.length)).setNumberFormat('yyyy-mm-dd');
 for(const name of ['金额','人工更正金额'])fsheet.getRange(fc(name)+'5:'+fc(name)+(4+d.facts.length)).setNumberFormat('#,##0.00');
}
const qr=[];
for(const r of d.citations){
 const chunks=r.quote.match(/[\s\S]{1,500}/g)||[''];
 chunks.forEach((q,i)=>qr.push([r.id,i?('续 '+(i+1)):'',r.material_id,r.filename,r.location,q,r.verification,r.source_href?'查看原件 · '+r.material_id:'原件缺失或内容已变更']));
}
const rsheet=setup('原文与来源',['引用编号','续段','材料编号','材料名称','准确位置','关键原话','识别与核验','原件位置'],
 qr,[11,9,11,30,35,66,30,29],'CitationIndex');
qr.forEach((row,i)=>linkCell(rsheet,'H'+(5+i),R[row[0]]?.source_href,'查看原件 · '+row[2]));
const isheet=setup('冲突与待核',['问题编号','问题类型','问题标题','复核状态','复核备注','材料记载与缺口','关联事实','关联材料','原文引用','下一步核实','办理状态','核查结果','复核人','复核时间','收补材料'],
 d.issues.map(q=>[q.id,q.kind,q.title,q.review_status||'未复核',q.review_note||'',q.detail,idLines(q.fact_ids||[]),idLines(q.material_ids||[]),idLines(q.citation_ids||[]),q.next_step,q.progress||'待补核',q.resolution_note||'',q.reviewed_by||'',q.reviewed_at||'',idLines(q.received_material_ids||[])]),
 [11,18,36,17,38,66,46,46,46,59,20,40,18,26,46],'IssueIndex');
if(d.issues.length)for(const col of ['D','E','K','L','M','N','O'])isheet.getRange(col+'5:'+col+(4+d.issues.length)).format.fill='#F7F3E9';
setup('更新记录',['时间','变更类型','关联对象','变更内容'],
 d.changes.map(c=>[c.at.replace('T',' '),c.type,c.target_id||'',c.detail]),[27,23,18,90],'ChangeLog');

const summary=wb.worksheets.getItem('案件速览');summary.showGridLines=false;
summary.getRange('A1').values=[['案件事实底稿']];summary.getRange('A1').format.font={name:font,size:18,bold:true,color:ink};
summary.getRange('A1').format.rowHeight=33;
summary.getRange('A2:D2').merge();summary.getRange('A2').values=[[d.case.name+(d.case.is_demo?('（虚构演示'+(hasAudio?'，含合成录音':'')+'）'):'')]];
summary.getRange('A2:D2').format.font={name:font,size:12,color:'#575B51'};summary.getRange('A2:D2').format.rowHeight=30;
const sr=[['项目','数值 / 状态','口径与说明','来源'],
 ['案件标识',d.case.case_id||'旧版未设置','',''],['底稿版本',d.case.revision||1,'用于复核回导身份与版本校验',''],
 ['材料数量',d.materials.length,'提取状态与原件核对分开记录',''],
 ['完整提取材料',d.materials.filter(m=>m.state==='已提取').length,'部分提取及失败材料须继续补核',''],
 ['事实记录',d.facts.length,'含有利、不利与各方不同表述',''],
 ['核对原件事实',d.facts.filter(f=>f.review_status==='已核对原件').length,'仅统计留有复核状态的事实',''],
 ['未关闭问题',d.issues.filter(q=>q.progress!=='已核实关闭').length,'收到补材料后须核查，不能自动关闭',''],
 ...(d.case.amount_summaries||[]).map(a=>[a.label,a.amount,(a.party||a.role||'')+' '+(a.version||'')+'；'+(a.detail||''),idLines(a.citation_ids||[],3)]),
 ['已选重点',d.facts.filter(f=>f.manual?.is_key===true).length,'由人工选定，与原件复核状态分别记录',''],
 ['整理分组',new Set(d.facts.map(f=>f.manual?.chronicle_group?.trim()).filter(Boolean)).size,'人工填写主题，空白事项保持未分组',''],
 ['整理边界',d.case.scope_note,'',''],
 ['材料缺口',d.materials.filter(m=>m.state!=='已提取').map(m=>m.id+' '+m.filename+'：'+m.state).join('；')||'已提取材料仍须按出处核对','',''],
 ['本轮关注',d.issues.filter(q=>q.progress!=='已核实关闭').slice(0,5).map(q=>q.id+' '+q.title).join('；'),'',''],
 ['人工复核','填写浅金列；分组与重点留空不新增选择。重点填否可取消；金额更正0有效。','',''],
 ['扫描与录音','自动识别仅供定位；姓名、日期、金额、原话须回原件。','','']];
summary.getRange('A4:D'+(3+sr.length)).values=sr.map(r=>r.map(literal));
summary.getRange('A4:D'+(3+sr.length)).format.font={name:font,size:12,color:'#464B40'};
summary.getRange('A4:D'+(3+sr.length)).format.wrapText=true;summary.getRange('A4:D'+(3+sr.length)).format.verticalAlignment='top';
summary.getRange('B7:B17').format.horizontalAlignment='left';
summary.getRange('A4:D4').format.fill='#EDEFE7';summary.getRange('A4:D4').format.font.bold=true;
[27,55,55,25].forEach((w,i)=>summary.getRange(String.fromCharCode(65+i)+'4:'+String.fromCharCode(65+i)+(3+sr.length)).format.columnWidth=w);
sr.forEach((r,i)=>{const lines=Math.max(...r.map((v,j)=>Math.ceil(textWidth(String(v??''))/[25,53,53,23][j])));summary.getRange('A'+(4+i)+':D'+(4+i)).format.rowHeight=Math.max(31,lines*20+14)});
(d.case.amount_summaries||[]).forEach((a,i)=>summary.getRange('B'+(12+i)).setNumberFormat('#,##0.00'));
summary.tabColor=gold;
const frows=Object.fromEntries(d.facts.map((f,i)=>[f.id,5+i])),mrows=Object.fromEntries(d.materials.map((m,i)=>[m.id,5+i])),rrows={};qr.forEach((r,i)=>rrows[r[0]]??=5+i);
d.facts.forEach((f,i)=>{if(f.citation_ids.length)linkCell(fsheet,fc('来源回查')+(5+i),"#'原文与来源'!A"+rrows[f.citation_ids[0]],f.citation_ids.map(id=>id+' / '+R[id]?.material_id).join('\n'))});
qr.forEach((r,i)=>{linkCell(rsheet,'C'+(5+i),"#'材料目录'!A"+mrows[r[2]],r[2])});
(d.case.amount_summaries||[]).forEach((a,i)=>{if(a.citation_ids.length)linkCell(summary,'D'+(12+i),"#'原文与来源'!A"+rrows[a.citation_ids[0]],idLines(a.citation_ids,3))});
d.issues.forEach((q,i)=>{if(q.fact_ids?.length)linkCell(isheet,'G'+(5+i),"#'事实大事记'!A"+frows[q.fact_ids[0]],idLines(q.fact_ids))});
d.subjects.forEach((s,i)=>{if(s.material_ids?.length)linkCell(ssheet,'E'+(5+i),"#'材料目录'!A"+mrows[s.material_ids[0]],idLines(s.material_ids))});
await fs.mkdir(out,{recursive:true});
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',
 options:{useRegex:true,maxResults:50},summary:'formula errors'});
await fs.writeFile(path.join(out,'_support/workbook-inspection.txt'),errors.ndjson);
const previews=path.join(out,'_support/previews');await fs.mkdir(previews,{recursive:true});
for(const name of names){
 const spec=styles[name],range=name==='事实大事记'?'A1:H9':spec?'A1:'+spec.endCol+Math.min(spec.endRow,9):'A1:D20';
 const img=await wb.render({sheetName:name,range,scale:1.5,format:'png'});
 await fs.writeFile(path.join(previews,name+'.png'),new Uint8Array(await img.arrayBuffer()));
}
const reviewImg=await wb.render({sheetName:'事实大事记',range:'C4:G9',scale:1.5,format:'png'});
await fs.writeFile(path.join(previews,'事实大事记_复核列.png'),new Uint8Array(await reviewImg.arrayBuffer()));
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,'案件事实底稿.xlsx'));
await fs.writeFile(path.join(out,'_support/xlsx-links.json'),JSON.stringify(links));
console.log(JSON.stringify({xlsx:path.join(out,'案件事实底稿.xlsx'),html:path.join(out,'案件事实底稿.html'),
 facts:d.facts.length,citations:d.citations.length,sheets:names.length}));
