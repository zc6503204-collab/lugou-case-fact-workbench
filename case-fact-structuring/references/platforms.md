# 平台入口与运行基线

两平台使用相同数据格式、业务规则和脚本；材料中的不同说法不会因平台变化而被合并或定性。当前验证环境为 Apple Silicon Mac。

## Codex

安装到 `~/.codex/skills/case-fact-structuring/`。调用 `$case-fact-structuring`，附材料目录、案件简称和可选的上一版底稿。界面元数据在 agents/openai.yaml。先查看 doctor；bundled 依赖以 load_workspace_dependencies 返回路径为准。

## WorkBuddy

安装到 `~/.workbuddy/skills/case-fact-structuring/`，对应 WorkBuddy.app。可输入“使用律构·案件事实梳理 Skill 整理这些材料”。本机通过 runtime.local.json 复用已验证 Python、Node、独立转写环境和模型。Skill 不自行安装依赖或申请账号权限。

本包不安装到 WorkBuddy AI 的其它技能目录；既有公众号排版、投递和法律写作 Skill 不更改。新 Skill 只在用户需要事实底稿、来源索引或其增量更新时调用。

## 安装和移动

分享包不带本机绝对路径、Python 环境、模型权重或 ffmpeg。新机器先按 runtime.example.json 配置已有运行支持。录音支持缺失时可继续其它材料，必须保留转写缺口；不要自动联网下载模型。

网页可直接打开，不需要服务端；`--bundle-sources` 的成果文件夹包含引用原件与回听副本，移动或分享时整夹保留。普通案卷默认链接本机原件，不复制或上传材料。
