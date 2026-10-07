# 数据接口 v1

UTF-8 JSON。顶层 `schema_version: "1.0"`；`case`、`materials`、`subjects`、`facts`、`citations`、`issues`、`changes` 必须存在。空数组合法。case 含 name、is_demo、scope_note、updated_at。

- materials：id（M0001）、filename、path、sha256、state、method、notes、duplicate_of、version_of、units。脚本生成。每个 unit 含 id、text、locator、verification。
- subjects：id（S0001）、name、role、aliases（数组）、material_ids、identity_note。
- citations：id（R0001）、material_id、unit_id、quote。定位和识别状态继承 unit，不另造页码；quote 须为文本中连续原话（忽略空白）。识别修订写人工备注，不改机器原話。
- facts：id（F0001）、date、subject_ids、description、amount（数值或 null）、currency、kind、citation_ids、review_status、review_note、manual。
- issues：id（Q0001）、kind（冲突/缺口/识别疑点/待确认变更）、title、detail、fact_ids、material_ids、citation_ids、next_step、review_status、review_note。
- changes：at、type、target_id、detail。

date 为 `{raw, iso, precision}`；day 的 iso=YYYY-MM-DD，month=YYYY-MM，year=YYYY，range/unknown 时 iso=null；raw 保留原话。未知日期单列，不补成 1 月 1 日。

kind 为材料记载/一方陈述/待核推断。复核状态为未复核/已核对原件/需补核/存在异议。已核对原件只在用户已复核或实际回查后填写。

manual 为 `{description: null, date_raw: null, amount: null, currency: null}`。0 是有效金额更正。空 Excel 人工列代表不新增更正；需清除已有更正时显式执行 `import-reviews --clear-empty`。

amount 为币种基本单位，“50万元”对应 500000/CNY，原话保留在引用。性质未明写在事实或问题中，不靠金额字段定性。

```json
{"id":"F0001","date":{"raw":"2025年6月12日","iso":"2025-06-12","precision":"day"},"subject_ids":["S0001"],"description":"聊天中出现‘那50万后面统一处理’的表述，性质待核。","amount":500000,"currency":"CNY","kind":"一方陈述","citation_ids":["R0001"],"review_status":"未复核","review_note":"","manual":{"description":null,"date_raw":null,"amount":null,"currency":null}}
```

## 增量协议

collect --previous 保留旧对象。相同路径/内容复用材料号；同内容新文件列重复关系；同路径变更列新版本，保留旧提取和引用，并显露旧原件缺口。不同文件名的新版本须有明确依据才能填写 version_of。

原路径覆盖时记录旧来源失效，并对已有关联事实新增待确认变更；这里的失效指当前路径不能再代表旧原件，不认定旧事实虚假。空提取失败可用 --retry-unreadable 重试，不改材料号。

模型修改同一事实沿用 F 编号，新对象取同类最大号加 1。merge 保留人工列；已复核事实变化时保留旧记录，新建议保存到 pending_changes 并列待确认问题。旧事实不会因为 candidate 缺项而被删除。

## v0.2 可选扩展（schema_version 仍为 1.0）

- case：case_id（稳定案件身份）、revision（底稿版本）；amount_summaries 为有引用的金额摘要。元素含 id、label、amount（元）、currency、role、party、version、detail、fact_ids、citation_ids；可选 calculation.terms 为 `{fact_id, sign: 1|-1}`，脚本校验计算与重复交易，不对全部事实金额求和。
- materials：category、batch_id、document_form；extraction 含 status、notes、obtained_units、page_count。缺少文本不等于没有事实。
- units.reading：status 为未读/已读，note 说明处理范围或无事实原因。
- collection：input_paths、files_seen、included_files、excluded（路径与理由）、missing_paths、completed。仅表示文件清点完成。
- facts：agreement_round、transaction_id、amount_role。金额角色为协议总额/协议分项/流水发生额/回款记载/一方主张/主张拆项/财务口径/其他金额。新增三字段进入已复核变更保护。
- facts/issues：reviewed_by、reviewed_at；facts.checked_citation_ids 为实际核查引用，不能填不存在的 R 编号。
- issues：progress 为待补核/已收到待核/已核实关闭；received_material_ids、resolution_note。关闭须有核查说明且复核状态为已核对原件。

旧数据新字段缺失仍合法；不补造已读或已复核状态。新的 Excel 在案件速览 A5/B5 记录案件身份、A6/B6 记录版本；回导扫描标签匹配，不依赖列的旧位置。缺案件元信息的旧表须显式迁移，不静默按编号混合。

采纳变更保留 pending_changes.before、decision、decision_note、decided_at；人工更正继续保留，采纳后的事实状态为需补核。

## v0.3 可选人工整理字段（schema_version 仍为 1.0）

`facts.manual.chronicle_group` 为文字；`facts.manual.is_key` 为布尔值。缺少字段表示未作决定。初始不得批量填 false；null、数值0和字符串“是”均不是 JSON 的合法 is_key 值。明确 false 表示人工取消重点，与未作选择不同。分组可为空串表示清除；回导时去除两端空格。重点和分组均不能代表已核对原件或法律判断。

Excel“重点事项”为是/否列表，初始空白。回导按列名识别：空白默认跳过已有选择；否映射 false；`--clear-empty` 允许清空表内所有空白人工列，不只分组。旧表缺少新列时，即使用该选项也不清除已有新字段。回导错误原子失败，不写部分记录。

这些字段随人工更正一起保留；已有分组或明确重点选择（含false）时，材料记载变化触发待确认变更。采纳变更保留人工字段和原始前值；不改变稳定 F/R/M 编号。网页按原始日期排序，人工时间更正单独显示；月份/年份不补造日期。整理分组不自动推定争点。

可选 `case.demo_manual_note` 为演示选择说明，用于首页和打印。真实案不填演示说明。
