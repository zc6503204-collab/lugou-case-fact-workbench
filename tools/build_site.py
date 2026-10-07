#!/usr/bin/env python3
"""Build the original public introduction pages, independently of the case renderer."""
from pathlib import Path
from html import escape

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
REPO = 'https://github.com/zc6503204-collab/lugou-case-fact-workbench'
SITE = 'https://zc6503204-collab.github.io/lugou-case-fact-workbench/'

def ai_install(identifier):
    destinations = {'auto':'当前 AI 工具的个人 Skill 目录（Codex 或 WorkBuddy.app）',
                    'codex':'Codex 的个人 Skill 目录', 'workbuddy':'WorkBuddy.app 的个人 Skill 目录'}
    def instruction(platform):
        return (f'请阅读 {SITE}install.md，按其中的安装流程，将“律构·案件事实梳理”安装到{destinations[platform]}。'
                '只使用该项目的安装资源并核验文件；已有版本先比较，更新前备份并保留本机配置。'
                '完成后检查 Skill 入口和运行支持，告诉我安装结果及还缺哪些依赖。')
    alternatives=''.join(f'<span hidden id="{identifier}-{key}">{escape(instruction(key))}</span>' for key in destinations)
    return f'''<section class="section" id="ai-install"><div class="ai-install panel"><div class="install-intro"><p class="eyebrow">交给 AI 安装</p><h2>复制一次，<br>让 AI 帮你装好。</h2><p class="muted">选择你使用的工具，复制右侧指令，发给能读取网址、操作本机文件的 AI。</p><ol class="install-steps"><li>复制安装指令</li><li>粘贴到 AI 对话</li><li>查看安装核验结果</li></ol><a href="install.md">查看本项目安装说明 →</a></div><div class="install-content"><div class="install-choice"><label for="{identifier}-platform">安装到</label><select id="{identifier}-platform" data-install-select="{identifier}"><option value="auto">当前工具 · 自动识别</option><option value="codex">Codex</option><option value="workbuddy">WorkBuddy.app</option></select><span class="pill">本项目官方资源</span></div><pre class="code install-command" id="{identifier}">{escape(instruction('auto'))}</pre>{alternatives}<div class="install-actions"><button class="button primary" type="button" data-copy="{identifier}">复制给 AI 安装</button><span class="copy-status" role="status" aria-live="polite"></span></div><p class="hero-note">安装文件后会检查运行支持。缺少依赖时，AI 应列出需要配置的项目。</p></div></div></section>'''

def page(filename, title, description, content):
    nav = [('index.html', '项目介绍'), ('demo.html', '虚构演示'), ('guide.html', '获取与使用')]
    links = ''.join(f'<a href="{href}"'+(' aria-current="page"' if filename == href else '')+f'>{label}</a>' for href,label in nav)
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · 律构</title><meta name="description" content="{escape(description, quote=True)}">
<meta name="theme-color" content="#f3f2ee"><meta property="og:type" content="website">
<meta property="og:title" content="{escape(title, quote=True)} · 律构"><meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:image" content="{SITE}assets/cover.png"><meta property="og:image:alt" content="律构案件事实工作台：虚构案卷的金额口径与来源示意">
<meta property="og:url" content="{SITE}{'' if filename == 'index.html' else filename}"><meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE}{'' if filename == 'index.html' else filename}"><link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<link rel="stylesheet" href="assets/site.css"><script src="assets/site.js" defer></script></head><body>
<a class="skip" href="#main">跳到正文</a><header class="header"><div class="wrap head"><a class="logo" href="index.html" aria-label="律构项目首页">律构<small>案件事实工作台</small></a><nav class="nav" aria-label="主导航">{links}<a href="{REPO}">GitHub ↗</a></nav></div></header>
<main id="main">{content}</main>
<footer class="footer"><div class="wrap foot"><div>© 2026 律构 · 保留权利<br>公开展示使用虚构案卷，真实案件试用仍需验证。</div><div><a href="{REPO}/blob/main/NOTICE.md">使用授权</a> · <a href="{REPO}/blob/main/TESTING.md">测试记录</a> · <a href="{REPO}/issues">反馈与联系 ↗</a><br>v0.3 · Codex / WorkBuddy · Apple Silicon Mac 基线</div></div></footer></body></html>'''
    (DOCS / filename).write_text(html, encoding='utf-8')

page('index.html', '把案卷整理成有出处的事实底稿',
     '律构·案件事实梳理：供 Codex 与 WorkBuddy 使用的事实整理 Skill。Excel 人工复核、网页回查来源、增量更新，公开提供虚构案卷演示。', '''
<section class="hero wrap"><div class="hero-grid"><div><p class="eyebrow">律构 · 案件事实梳理 SKILL / v0.3</p>
<h1>把零散案卷，整理成<br><span>有出处的事实底稿。</span></h1><p class="lead">从合同、流水到聊天与录音，把时间、主体、金额和关键原话放到同一张工作台。每条事实保留出处，每处分歧留给律师复核。</p>
<div class="buttons"><a class="button primary" href="demo.html">查看虚构演示 →</a><a class="button" href="#ai-install">让 AI 帮我安装</a></div><p class="hero-note">Excel 做复核 · 网页做回查 · 两平台共用一套规则</p></div>
<div class="visual" aria-label="虚构案卷结构示意，非界面截图"><div class="visual-head"><strong>股权投资与回购 · 虚构演示</strong><span class="pill">来源可回查</span></div>
<div class="mini-stats"><div><small>协议约定</small><strong>6,800万</strong><small>两轮投资</small></div><div><small>银行汇入</small><strong>5,600万</strong><small>流水记载</small></div><div><small>一方主张</small><strong>2,680万</strong><small>最新材料版本</small></div></div>
<div class="mini-event"><time datetime="2024-02-05">2024.02</time><div>第一轮投资协议签署<small>F0007 · 正本与草案并列回查</small></div></div>
<div class="mini-event"><time datetime="2025-06-18">2025.06</time><div>200万元回款出现不同性质记载<small>扣减本金 / 股东分配 / 关联往来 · 待核</small></div></div>
<blockquote class="quote">“那50万后面统一处理”<small>F0069 · 保留聊天原话，未推定为确认欠款</small></blockquote>
<p class="hero-note">结构示意 · 实际工作台可在演示页打开</p></div></div></section>
<div class="wrap strip"><div><strong>7 个工作表</strong><span>一套完整事实底稿</span></div><div><strong>2 种交付</strong><span>Excel + 离线网页</span></div><div><strong>稳定编号</strong><span>补材料后继续回查</span></div><div><strong>人工复核</strong><span>保留更正、分组与备注</span></div></div>
<div class="wrap">''' + ai_install('home-ai-command') + '''</div>
<section class="section wrap" id="features"><div class="section-head"><div><h2>整理得清楚，也查得到原文。</h2><p>把办案中反复做的核对，放进一个可以接续使用的流程。</p></div></div><div class="grid3">
<article class="feature"><div class="num">01 / 大事记</div><h3>看全案，也看重点</h3><p>按时间或律师填写的整理分组浏览。搜索主体别称、原话、编号和金额，展开事项即可看准确位置与关联问题。</p></article>
<article class="feature"><div class="num">02 / 来源</div><h3>保留材料说了什么</h3><p>原始记载、当事人陈述和待核推断分别列示。PDF 页码、Word 段落、表格单元格与录音时间各有定位。</p></article>
<article class="feature"><div class="num">03 / 复核</div><h3>让人工判断留得下来</h3><p>在 Excel 保存复核状态、备注、金额更正、分组和重点选择。回导后生成网页快照，补材料时继续保护旧记录。</p></article>
</div></section>
<section class="section wrap"><div class="section-head"><div><h2>先清点，再理解，最后核对。</h2><p>提取与编号交给脚本，材料理解由模型完成，关键姓名、日期、金额和原话由人确认。</p></div><a href="guide.html#workflow">看完整使用流程 →</a></div><div class="steps">
<article class="step"><b>01 / 材料清点</b><h3>把缺口一起记下来</h3><p>重复件、新版本、不可读材料和缺附件仍进入目录，并注明影响范围。</p></article>
<article class="step"><b>02 / 事实整理</b><h3>把事项与来源关联</h3><p>识别主体、时间和行为，连接原话与出处；未知主体和不完整日期保持原状。</p></article>
<article class="step"><b>03 / 双格式交付</b><h3>工作底稿与阅读视图</h3><p>同一份结构化数据生成七表 Excel 和单文件网页，金额、编号与引用对应一致。</p></article>
<article class="step"><b>04 / 复核与更新</b><h3>在上一版上继续工作</h3><p>回导律师的更正，再处理补交材料。材料变化与人工记录冲突时，列为待确认变更。</p></article>
</div></section>
<section class="section wrap"><div class="duo"><article class="panel"><h2>一套底稿，两个使用场景。</h2><ul class="list"><li><strong>内部办案：</strong>从材料目录进入事项、原文和待核问题，保留复核痕迹。</li><li><strong>客户沟通：</strong>用已人工选定的重点事项解释时间与金额口径。</li><li><strong>持续更新：</strong>保存 case.json 与上一版 Excel，接续处理补充材料。</li></ul><p class="muted">对外沟通前，由律师另行确认可披露的材料与范围。</p></article>
<article class="panel"><h2>清爽工作台，三套配色。</h2><p class="muted">白色工作区与墨色正文保持统一。颜色区分栏目、金额口径和工作状态；打印保留文字与来源。</p><div class="themes"><span class="theme"><span class="swatches" aria-hidden="true"><i></i><i></i><i></i></span>沉稳多色</span><span class="theme bright"><span class="swatches" aria-hidden="true"><i></i><i></i><i></i></span>明快彩色</span><span class="theme classic"><span class="swatches" aria-hidden="true"><i></i><i></i><i></i></span>灰金</span></div><p class="hero-note">Excel 延续华文仿宋；网页提供搜索、筛选、详情和打印范围选择。</p></article></div></section>
<section class="section wrap"><div class="banner"><div><h2>先用一套虚构复杂案卷，看它如何工作。</h2><p>60份材料 · 118条事实 · 179条引用 · 21项待核问题</p></div><div class="buttons"><a class="button primary" href="demo.html">进入演示导览 →</a></div></div><p class="license-note">当前公开源代码供查看与评估，暂未附开源许可证。事实整理、来源回查与复核记录为本版范围；真实案件适用效果仍需在办案中验证。</p></section>
''')

page('demo.html', '虚构案卷演示', '用60份虚构材料体验股权投资与回购案事实工作台：118条事实、179条引用，区分协议、流水与一方主张，回查原话和复核记录。', '''
<div class="wrap"><section class="page-intro"><p class="eyebrow">SHOWCASE / 全部材料均为虚构演示</p><h1>一个复杂案卷，<br><span>几条清晰的回查路径。</span></h1><p class="lead">以约30个月的股权投资与回购事项为例，串起协议版本、代付身份、银行记录、财务口径、沟通与通知轨迹。所有公司、人物、交易、材料及合成录音均为虚构。</p></section>
<div class="demo-banner"><div><h3>打开案件事实工作台</h3><p>在线阅读与下载版本使用同一份演示数据。分组和重点是演示编者的人工选择，未表示已核对原件。</p></div><div class="buttons"><a class="button primary" href="workpaper/案件事实底稿.html#overview">在线打开 →</a><a class="button" href="downloads/fictional-demo-v0.3.zip" download>下载完整案卷</a></div></div>
<div class="strip"><div><strong>60</strong><span>材料 · 59已提取 / 1不可读</span></div><div><strong>118</strong><span>事项 · 每条关联原文</span></div><div><strong>179</strong><span>引用 · 保留准确位置</span></div><div><strong>21</strong><span>问题 · 冲突、缺口与疑点</span></div></div>
<section class="section" id="amounts"><div class="section-head"><div><h2>先把三种金额口径分开。</h2><p>不同口径并列展示，每项有来源；主张总额与拆项保持对应。</p></div><a href="workpaper/案件事实底稿.html#amounts">进入金额核对 →</a></div>
<div class="case-money"><article class="money"><span>协议约定总额</span><strong>6,800万元</strong><p>第一轮4,800万 + 第二轮2,000万<br>F0007 / F0011 · R0009 / R0014</p></article><article class="money"><span>银行汇入记录</span><strong>5,600万元</strong><p>六笔汇入记录合计；与协议额分别呈现<br>F0049 · R0071</p></article><article class="money"><span>甲方最新材料主张</span><strong>2,680万元</strong><p>本金2,400万 + 自算收益250万 + 费用30万<br>F0107 · R0162 · 2026-06-30版本</p></article></div>
<p class="muted">以上分别为协议记载、流水记载与一方陈述，不代表应付款认定。200万元回款究竟扣减本金、属于分红还是关联往来，材料中存在不同说法。</p></section>
<section class="section" id="walkthrough"><div class="duo"><div><h2>按这五步，体验完整回查。</h2><p class="lead">可以先看全案，再沿着具体问题返回原材料。</p><ol class="walkthrough">
<li><h3>在概览比较金额与覆盖情况</h3><p>查看已选重点、材料读取状态和待核问题。协议额、流水额与甲方主张分别列示。</p><a href="workpaper/案件事实底稿.html#overview">打开案件概览 →</a></li>
<li><h3>在大事记搜索“那50万”</h3><p>搜索 F0069 或原话，展开详情，查看聊天摘录与出处。保留谈话表达的原有含义。</p><a href="workpaper/案件事实底稿.html#facts">打开大事记 →</a></li>
<li><h3>并列看200万元回款性质</h3><p>对照 F0053 的支付记录、F0061 的财务口径、F0071 的投资方说法及 F0105 的公司说明。</p><a href="workpaper/案件事实底稿.html#issues">打开冲突与待核 →</a></li>
<li><h3>从引用返回材料与录音</h3><p>点击引用编号查看原话、准确位置和原件链接；在带录音的事项详情中点击回听定位。自动转写仍需听核。</p><a href="workpaper/案件事实底稿.html#materials">打开材料目录 →</a></li>
<li><h3>在 Excel 留下人工选择</h3><p>修改复核状态、备注、整理分组和重点事项，保存后回导并重新生成网页。人工选择不会自动改为“已核对原件”。</p><a href="workpaper/案件事实底稿.xlsx" download>下载华文仿宋 Excel →</a> · <a href="guide.html#review">查看回导说明</a></li></ol></div>
<aside class="panel"><span class="pill">材料记载 / 一方陈述 / 待核推断</span><h2 style="margin-top:18px">原话保留，分歧保留。</h2><blockquote class="quote">“那50万后面统一处理”<small>F0069 · 2025-06-20<br>聊天摘录 · R0101</small></blockquote><p class="muted" style="margin-top:20px">这句话保留在原话与来源中，未自动写成“确认欠款”。</p><ul class="list"><li>草案与正本差异分别记录。</li><li>同名主体不擅自合并。</li><li>财务口径变化列为待核问题。</li><li>缺页和缺失附件保留具体缺口。</li><li>同笔交易的多份引用不重复汇总。</li></ul><p class="hero-note">演示含4段合成录音。合成音频的识别结果不代表真实复杂录音准确率。</p></aside></div></section>
<section class="section" id="downloads"><div class="section-head"><div><h2>带走底稿，继续体验。</h2><p>离线使用时，保留整个成果文件夹，以维持原件与回听链接。</p></div></div><div class="grid3"><article class="download"><div class="tag">完整材料与成果</div><h3>虚构演示包</h3><p>含网页、Excel、结构化数据、引用原件，以及基础、复杂、缺损与分次提交批次。</p><a class="button" href="downloads/fictional-demo-v0.3.zip" download>下载演示包</a></article><article class="download"><div class="tag">七表工作底稿</div><h3>华文仿宋 Excel</h3><p>查看材料、主体、大事记、原文、待核及更新记录；复核列支持回导。</p><a class="button" href="workpaper/案件事实底稿.xlsx" download>下载 Excel</a></article><article class="download"><div class="tag">可接续的数据</div><h3>case.json</h3><p>包含稳定编号、关联引用和演示人工记录，供验证与增量更新使用。</p><a class="button" href="workpaper/case.json" download>下载结构化数据</a></article></div></section>
<section class="section"><div class="proof"><strong>测试范围如实公开。</strong><br>已完成数据、来源、增量保护及网页逻辑检查，包括500条事项检索与三套主题。原工作台的桌面、375px手机及A4实际视觉验收仍待本机确认；真实案件试用与独立录音回听仍待开展。<a href="https://github.com/zc6503204-collab/lugou-case-fact-workbench/blob/main/TESTING.md">查看完整测试记录 →</a></div></section></div>
''')

page('guide.html', '获取与使用', '下载 Codex、WorkBuddy 案件事实梳理 Skill，了解 Mac 运行基线、案件材料整理、Excel 复核回导和补充材料更新。', '''
<div class="wrap"><section class="page-intro"><p class="eyebrow">GET STARTED / 从你的材料开始</p><h1>把一套方法，<br><span>放进日常办案流程。</span></h1><p class="lead">分别提供 Codex 与 WorkBuddy 入口，共用事实整理规则与底稿格式。先下载查看，确认使用授权及运行环境，再从一组材料开始整理。</p></section>
''' + ai_install('guide-ai-command') + '''
<section id="install" style="padding-bottom:35px"><div class="duo"><article class="download"><div class="tag">CODEX</div><h2>Codex 安装包</h2><p>解压后，把 case-fact-structuring 文件夹放入个人 Skill 目录，重新加载会话后调用。</p><pre class="code">~/.codex/skills/case-fact-structuring/</pre><div class="buttons"><a class="button primary" href="downloads/codex-lugou-v0.3.zip" download>下载 Codex 包</a><a class="button" href="https://github.com/zc6503204-collab/lugou-case-fact-workbench/tree/main/case-fact-structuring">查看源包</a></div></article><article class="download"><div class="tag">WORKBUDDY.APP</div><h2>WorkBuddy 安装包</h2><p>将包内文件夹放入 WorkBuddy 的 Skill 目录。本包适配 WorkBuddy.app，运行支持需在当前机器配置。</p><pre class="code">~/.workbuddy/skills/case-fact-structuring/</pre><a class="button primary" href="downloads/workbuddy-lugou-v0.3.zip" download>下载 WorkBuddy 包</a></article></div><p class="license-note">© 2026 律构。当前暂未附开源许可证，其他使用授权请通过 <a href="https://github.com/zc6503204-collab/lugou-case-fact-workbench/issues">项目维护者</a>确认。安装包不包含运行库、模型权重或本机配置。</p></section>
<section class="section" id="workflow"><div class="section-head"><div><h2>第一次整理，只需给出材料和范围。</h2><p>以下提示可以复制后替换路径、案件简称与材料范围。</p></div></div><div class="duo"><article class="panel"><h3>Codex 调用示例</h3><pre class="code" id="prompt-codex">$case-fact-structuring
请整理我指定的案件材料目录【填写目录】，案件简称【填写简称】。
先清点并检查读取范围，再逐份阅读提取单元，生成事实、引用、冲突和待核问题。
保留原话与准确出处，区分材料记载、一方陈述和待核推断。
交付七表 Excel、离线网页和 case.json；有无法读取或缺附件的材料，请列具体缺口。</pre><button class="copy" type="button" data-copy="prompt-codex">复制提示</button><span class="copy-status" role="status" aria-live="polite"></span></article>
<article class="panel"><h3>WorkBuddy 调用示例</h3><pre class="code" id="prompt-workbuddy">使用律构·案件事实梳理 Skill。
材料目录：【填写目录】；案件简称：【填写简称】。
请先检查当前机器运行支持，逐份整理指定材料，保留来源、不同版本和待核缺口。
生成 Excel、离线网页和 case.json。关键姓名、日期、金额及原话保留人工复核状态。</pre><button class="copy" type="button" data-copy="prompt-workbuddy">复制提示</button><span class="copy-status" role="status" aria-live="polite"></span></article></div>
<p class="hero-note">材料提取只产生目录与阅读单元。模型还需逐份阅读并整理事实、引用和问题，才能生成有内容的工作底稿。</p></section>
<section class="section" id="review"><div class="section-head"><div><h2>人工复核后，在上一版上接着更新。</h2><p>网页是底稿快照。复核与选择在 Excel 保存，回导后再生成网页。</p></div></div><div class="steps"><article class="step"><b>01 / 保留上一版</b><h3>保存可接续文件</h3><p>保留 case.json、Excel 和原件。使用成果副本做复核，案件材料与成果留在自己的工作目录。</p></article><article class="step"><b>02 / 填写复核列</b><h3>状态、备注与人工更正</h3><p>修改指定人工列，填写整理分组及“是 / 否”重点选择；重点选择本身不等于核对原件。</p></article><article class="step"><b>03 / 回导与校验</b><h3>确认人工记录被保留</h3><p>按列名识别，兼容旧表；明确填写“否”可取消重点，金额更正“0”按有效数值保留。</p></article><article class="step"><b>04 / 加入补充材料</b><h3>核对新增与版本变化</h3><p>继续使用稳定编号，记录新增、修改和失效；与人工修改冲突的材料变化进入待确认清单。</p></article></div>
<pre class="code" id="prompt-update">请使用律构·案件事实梳理 Skill 接续更新。
上一版结构化数据：【case.json 路径】
我已复核的 Excel：【底稿路径】
补充材料：【目录】
先回导指定复核列，保留备注、金额更正、整理分组和重点选择；再逐份整理新增材料。
不要重编号。材料变化影响人工记录时列为待确认变更，完成校验后生成新版底稿。</pre><button class="copy" type="button" data-copy="prompt-update">复制更新提示</button><span class="copy-status" role="status" aria-live="polite"></span><p class="hero-note">普通回导中的空白保留旧值。需要清除分组等人工字段时，应明确要求“清除空值”，使用 --clear-empty，并检查变更记录。</p></section>
<section class="section" id="runtime"><div class="duo"><article class="panel"><h2>运行环境与材料支持</h2><ul class="list"><li>当前运行基线：Apple Silicon Mac；其他环境尚未完成整体验证。</li><li>文档提取：Python、pypdf、python-docx、openpyxl；扫描与图片 OCR 使用 macOS Vision。</li><li>Excel 生成：Node 与 Codex bundled @oai/artifact-tool；由已配置的宿主运行库提供。</li><li>录音：独立 mlx-whisper 环境、本地模型及 ffmpeg；缺支持时列出转写缺口，继续整理其他材料。</li></ul><p class="muted">复制 runtime.example.json 为本机配置前，先让 Agent 检查已有运行支持。doctor 只检查，不下载或修改系统。</p><p class="hero-note"><a href="https://github.com/zc6503204-collab/lugou-case-fact-workbench/blob/main/case-fact-structuring/references/runtime.md">详细运行说明 →</a></p></article><article class="panel"><h2>交付后如何保存和分享</h2><ul class="list"><li>Excel 保持七表，字体为华文仿宋；未安装字体的设备可能回退显示。</li><li>网页为单文件，可本地打开，无需部署网站；原件与录音链接依赖成果文件夹结构。</li><li>需一起移动原件时，要求生成包含来源副本的成果包，保留整个文件夹。</li><li>公开网站与演示包只包含虚构案卷，真实案件成果由你自行保管与决定披露范围。</li></ul><p class="hero-note">离线指网页阅读与本地音频识别；案件文本理解仍由你所选的 Agent 处理。</p></article></div></section>
<section class="section" id="faq"><h2>使用前常见问题</h2><details><summary>能直接给出法律定性或诉讼策略吗？</summary><p>本版范围是事实整理、来源回查与人工复核记录。证据采信、法律定性、诉讼策略和文书起草应另行开展。</p></details><details><summary>OCR 或转写失败，是否还能交付？</summary><p>可以生成明确标注范围的阶段底稿。不可读材料仍进入目录，缺页、缺附件与转写失败列具体缺口，不将材料缺失解释为某一事实不存在。</p></details><details><summary>网页里可以直接修改重点与分组吗？</summary><p>网页是快照，用于搜索、筛选、回查与打印。重点和分组在 Excel 中保存，经回导与重新生成后呈现。</p></details><details><summary>这些示例是否证明真实办案准确率？</summary><p>示例用于验证工作流程与边界。真实案件试用、复杂录音回听和原工作台的完整视觉验收仍待开展，测试完成情况见项目测试记录。</p></details><details><summary>如何反馈问题或联系维护者？</summary><p>可以在 GitHub Issues 提交使用场景、环境与错误信息。请使用虚构或去标识化示例，避免将真实案卷提交到公开仓库。</p></details></section>
<section class="section"><div class="banner"><div><h2>先看演示，再准备你的第一组材料。</h2><p>了解回查方式与复核边界后，从明确范围的小批次开始。</p></div><div class="buttons"><a class="button primary" href="demo.html">查看演示 →</a><a class="button" href="https://github.com/zc6503204-collab/lugou-case-fact-workbench/releases">版本与下载 ↗</a></div></div></section></div>
''')

(DOCS / 'assets/favicon.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#35618a"/><path d="M19 17v30M28 21h18M28 31h18M28 41h12" fill="none" stroke="#fff" stroke-width="4"/><path d="M19 17v30" stroke="#d8bd80" stroke-width="4"/></svg>''', encoding='utf-8')

(DOCS / 'assets/cover.svg').write_text('''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-labelledby="title desc"><title id="title">律构 · 案件事实工作台</title><desc id="desc">虚构案卷结构示意：协议6800万、银行汇入5600万、一方主张2680万，各自保留来源与复核状态。</desc><defs><style>text{font-family:"PingFang SC","Heiti SC",sans-serif}.serif{font-family:"Songti SC",serif}.muted{fill:#626d68}</style></defs><rect width="1280" height="720" fill="#f3f2ee"/><path d="M68 58h4v35h-4" fill="#86662a"/><text x="89" y="84" font-size="30" font-weight="600" fill="#252d2c" class="serif">律构</text><text x="192" y="84" font-size="17" class="muted">案件事实梳理 / v0.3</text><text x="68" y="183" font-size="50" class="serif" font-weight="600" fill="#252d2c">让每条事实，</text><text x="68" y="252" font-size="50" class="serif" font-weight="600" fill="#35618a">都有可回查的出处。</text><text x="70" y="312" font-size="21" class="muted">材料 · 大事记 · 原话 · 冲突 · 人工复核</text><path d="M70 350h450" stroke="#dbe1d6"/><text x="70" y="398" font-size="20" fill="#26776f">Excel 工作底稿 ＋ 离线网页</text><text x="70" y="438" font-size="19" class="muted">适配 Codex 与 WorkBuddy</text><text x="70" y="478" font-size="18" class="muted">稳定编号 / 增量更新 / 复核记录保护</text><rect x="600" y="130" width="610" height="450" rx="18" fill="#fff" stroke="#dfe4da"/><text x="632" y="173" font-size="19" fill="#252d2c">股权投资与回购 · 虚构演示</text><text x="632" y="205" font-size="16" class="muted">60份材料 / 118条事实 / 179条引用</text><path d="M632 225h546" stroke="#e1e5dc"/><rect x="632" y="245" width="174" height="110" rx="7" fill="#eff2f6"/><rect x="818" y="245" width="174" height="110" rx="7" fill="#eef4f3"/><rect x="1004" y="245" width="174" height="110" rx="7" fill="#f4f2f5"/><text x="651" y="278" font-size="17" fill="#35618a">协议约定</text><text x="651" y="326" font-size="31" fill="#35618a">6,800万</text><text x="837" y="278" font-size="17" fill="#26776f">银行汇入</text><text x="837" y="326" font-size="31" fill="#26776f">5,600万</text><text x="1023" y="278" font-size="17" fill="#746085">一方主张</text><text x="1023" y="326" font-size="31" fill="#746085">2,680万</text><text x="632" y="404" font-size="19" fill="#252d2c">200万元回款 · 性质分歧并列保留</text><text x="632" y="437" font-size="16" class="muted">不同说法与各自来源对应，不自动选择成立版本</text><rect x="632" y="466" width="546" height="80" rx="6" fill="#f7f7f2"/><path d="M633 466v80" stroke="#b4a176" stroke-width="3"/><text x="650" y="497" font-size="19" fill="#252d2c">“那50万后面统一处理”</text><text x="650" y="526" font-size="16" class="muted">保留原话与出处，未自动写成确认欠款</text><path d="M70 626h1140" stroke="#dbe1d6"/><text x="70" y="665" font-size="17" class="muted">公开演示均为虚构 · 界面结构示意 · 真实案件试用待验证</text><text x="1042" y="665" font-size="17" fill="#86662a">© 2026 律构</text></svg>''', encoding='utf-8')

print('Built 3 public pages, original cover SVG and favicon.')
