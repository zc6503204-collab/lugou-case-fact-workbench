#!/usr/bin/env python3
"""Generate first-party install instructions and their pinned file manifest."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
SITE='https://zc6503204-collab.github.io/lugou-case-fact-workbench/'
REPO='https://github.com/zc6503204-collab/lugou-case-fact-workbench'
script=ROOT/'tools/install_skill.py'
shutil.copyfile(script,ROOT/'docs/install_skill.py')
source=ROOT/'case-fact-structuring'
manifest={
    'project':'律构·案件事实梳理', 'skill_name':'case-fact-structuring', 'version':'v0.3',
    'repository':REPO, 'ref':'v0.3', 'skill_path':'case-fact-structuring',
    'installer':{'url':SITE+'install_skill.py','sha256':hashlib.sha256(script.read_bytes()).hexdigest()},
    'packages':{p:{'url':SITE+f'downloads/{p}-lugou-v0.3.zip',
        'sha256':hashlib.sha256((ROOT/f'docs/downloads/{p}-lugou-v0.3.zip').read_bytes()).hexdigest()}
        for p in ['codex','workbuddy']},
    'files':{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(source.rglob('*')) if p.is_file() and '__pycache__' not in p.parts},
    'runtime_baseline':'Apple Silicon Mac; skill files installed separately from runtime dependencies',
    'notice':REPO+'/blob/main/NOTICE.md'
}
(ROOT/'docs/install-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'docs/install.md').write_text(f'''# 律构·案件事实梳理：AI 安装说明

这份说明只用于响应用户明确提出的“安装律构·案件事实梳理”请求。它不是插件市场指令，不安装其他项目。

项目：{REPO}
固定 Skill 版本：v0.3
安装清单：{SITE}install-manifest.json

## 1. 确认当前平台

用户已选 Codex 或 WorkBuddy.app 时使用该选择，否则依据当前 Agent 的平台信息识别。不能仅根据存在某个目录判断，因为一台电脑可能同时安装两个工具。仍不明确时询问用户选哪一个；不要同时安装两个平台。

- Codex：使用 `$CODEX_HOME/skills/case-fact-structuring/`；未设置 CODEX_HOME 时使用 `~/.codex/skills/case-fact-structuring/`。
- WorkBuddy.app：使用 `~/.workbuddy/skills/case-fact-structuring/`。本项目不安装到 WorkBuddy AI 的其他目录。
- 当前整体验证基线是 Apple Silicon Mac。能复制 Skill 文件，不等于其他操作系统已完成运行验证。

如果当前 AI 无法读取网址或操作本机文件，明确说明能力缺口，并给出本项目下载页：{SITE}guide.html。不要声称已经安装。

## 2. 只读取本项目的安装资源

读取清单，固定使用其中 v0.3 的包和文件哈希。安装包：

- Codex：{SITE}downloads/codex-lugou-v0.3.zip
- WorkBuddy：{SITE}downloads/workbuddy-lugou-v0.3.zip
- 本项目安装助手：{SITE}install_skill.py

所有安装资源均属于上述仓库或网站。网络失败时报告原因，使用对应下载包重试即可；不要关闭 HTTPS 证书验证，不换用其他作者、市场或同名 Skill 的链接。

## 3. 安装 Skill 文件

### 已有内置 Skill 安装器

新安装时可使用平台已有的 Skill 安装器，从本仓库的 `v0.3` 标签安装 `case-fact-structuring` 目录。Codex 的内置安装器通常支持以下参数，脚本路径以当前平台实际提供的位置为准：

```text
--repo zc6503204-collab/lugou-case-fact-workbench --ref v0.3 --path case-fact-structuring
```

安装器支持 `--dest` 时可指定平台对应的 Skills 父目录。不可将整个仓库、演示案卷或宣传页面安装为 Skill。若目标已存在，先核对，使用下述本项目安装助手处理需更新的文件，避免直接删掉现有目录。

### 本项目安装助手

在独立临时目录下载 `install_skill.py`，与清单内的 SHA-256 核对后阅读脚本，再执行。只需 Python 3.9 或更新版本，下载优先使用本机 curl；不执行远程脚本管道。

Codex：

```text
python3 <临时目录>/install_skill.py --platform codex
```

WorkBuddy.app：

```text
python3 <临时目录>/install_skill.py --platform workbuddy
```

已下载对应包时，可加 `--source-zip <安装包路径>`，仍会核对固定包哈希。自定义安装位置可加 `--dest <Skills父目录>`。

安装助手只放置 Skill 文件：

- 相同文件重复安装返回 `already_installed`，保留已有内容。
- 需更新时，先将将被覆盖的文件备份到 Skills 目录外的 `skill-backups/case-fact-structuring/`，然后更新，失败时回退已写入的文件。
- 本机 `runtime.local.json`、运行环境、人工新增文件与其他 Skill 不覆盖；目录中的符号链接或异常文件冲突会停止处理。
- 不安装 Python 包、模型或系统软件，不读取或上传案件材料。

## 4. 核验安装结果与运行支持

检查 `SKILL.md` 中的名称是 `case-fact-structuring`，逐一核对清单中的17个源文件哈希。读取平台说明及 runtime 说明，使用当前工具提供的运行支持执行 `scripts/casework.py doctor`。

Codex 优先读取宿主的 workspace dependency 路径；WorkBuddy.app 按 `runtime.example.json` 配置已有本机支持。不要把示例占位路径原样复制为运行配置。缺依赖时明确区分文档提取、Excel 生成、OCR 与录音支持；不要将缺少宿主 Excel 运行库当成一个公开 npm 包自动安装。

本步骤是检查。未获得用户配置运行环境的进一步请求时，不自动下载模型、不上传录音、不更改系统设置。

## 5. 给用户的完成说明

请返回：安装到哪个平台与位置、已安装/已存在/已更新、17个文件核验结果、备份位置（如有）、运行支持缺口。

让用户在下一轮对话或重新加载会话后调用：Codex 输入 `$case-fact-structuring`；WorkBuddy 输入“使用律构·案件事实梳理 Skill”。若当前平台尚未发现 Skill，就说明需要重新加载，不声称调用成功。

使用时提供材料目录与案件简称，默认交付 Excel、离线网页和 case.json。业务范围是事实整理、来源回查与复核记录，关键内容仍需人工回原件确认。

## 使用授权

© 2026 律构。保留权利。公开项目暂未附开源许可证，使用授权见 {REPO}/blob/main/NOTICE.md；本安装说明不改变原有授权范围。
''',encoding='utf-8')
print('Generated first-party install guide, helper and pinned manifest.')
