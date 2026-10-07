# 当前 Mac 的运行支持

doctor 检查依赖，不下载或修改系统。优先读 CASEWORK_CONFIG 指定的 JSON，否则读 Skill 的 runtime.local.json。配置项：python、node、node_modules、asr_python、asr_model、ffmpeg。运行配置不进入分享包。

文档提取用 pypdf、python-docx、openpyxl（仅读取）。图片和无文字 PDF 用 macOS Vision/PDFKit，Swift 编译缓存置于临时目录；OCR 不可用时列具体缺口。

当前 Mac 的受限执行环境可能无法访问图形设备。Vision 崩溃或 MLX 报 No Metal device 时，Codex 可将同一条仅处理用户指定本地材料的命令提交权限审查后重试；不扩大目录范围或联网。权限不可用时保留失败材料及具体缺口，继续其它材料。WorkBuddy 也须具备本机图形设备访问能力。

Excel 用 Codex bundled @oai/artifact-tool。渲染器把入口和 node_modules 链接放在成果的 _support 内，不复制运行库。WorkBuddy 在当前 Mac 使用同一套运行支持；其它机器先检查环境。

录音使用独立 Python 3.12 环境中的 mlx-whisper、本地 MLX 模型和本地 ffmpeg，HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE 保持开启。缺依赖或模型立即报错，不自动下载模型或上传录音。

`casework.py transcribe <录音> --out <目录>` 保留逐段时间、机器文本、识别指标、待听核状态及 SRT，同时保存引擎原始分段。默认中文，支持 language 参数。转换为 16kHz 单声道，按引擎内部窗口处理，再按词时间和标点生成短句回听单元，保持原录音绝对时间。静音返回空段；说话人身份需人工确认，不实现声纹认定。

合成语音不能代表嘈杂真实录音准确率；重要原话仍需听核。这里的离线仅指音频识别环节，案卷文本由当前选择的 Agent 处理。
