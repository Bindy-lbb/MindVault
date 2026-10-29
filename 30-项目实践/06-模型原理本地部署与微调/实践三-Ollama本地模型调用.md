# 实践三：Ollama 本地模型调用

[项目入口](README.md) · [上一项](实践二-小矩阵LoRA与适配器.md) · [下一项](实践四-数据检查与真实LoRA选修.md)

目标：确认本机真实加载了选定模型，再调用它、核对输出和资源。这项可以先看预览与固定响应，真实模型运行按自己的条件选择。

运行前可看[统一运行约定与排错](../../40-工具手册/实践运行约定与排错.md)：从仓库根目录开始，首次代码块设置会话变量；新终端需重新设置。输出使用新名称，预期失败不记作成功。

## 1. 先预览，不安装模型

```powershell
Set-Location 'E:\my-projects\MindVault'
$env:PYTHONUTF8 = '1'
$advanced = '.\30-项目实践\06-模型原理本地部署与微调'
python "$advanced\ollama_client.py" --mode preview
python "$advanced\ollama_client.py" --mode fixture --output '.local/advanced/ollama-fixture-v1'
```

preview 显示将检查 `/api/tags` 再请求 `/api/chat`；fixture 用固定教学回答检查保存流程，Token 数、模型加载耗时和速度均无实测值。fixture 只配套默认问题。

## 2. 准备环境与本地模型

本次整理未安装 Ollama、未下载或运行真实模型。准备好后按[Windows 文档](https://docs.ollama.com/windows)与[Quickstart](https://docs.ollama.com/quickstart)自行安装；安装后它通常在后台运行，不要再盲目启动重复服务。

本地候选为 [qwen2.5:0.5b](https://ollama.com/library/qwen2.5:0.5b)，核查时是约398MB的 Q4_K_M 分发。文件大小不是运行内存；选择它是为了缩小入门下载与计算规模，不是模型效果最优或本机性能已验证的结论。

如果希望禁用云功能，按[官方 FAQ](https://docs.ollama.com/faq)设置用户目录 `.ollama/server.json` 的 `disable_ollama_cloud: true`，保留其中已有字段，重启 Ollama 并核对日志。环境变量方式也需作用于实际服务进程；只在新终端设置，不会自动改变已运行的桌面服务。

准备后：

```powershell
ollama --version
ollama pull qwen2.5:0.5b
ollama list
ollama run qwen2.5:0.5b
```

pull 会联网下载权重，需要时间与磁盘；本练习不选择 cloud 标签。聊天可输入 `/bye` 退出交互，模型可能仍在内存中。

## 3. 显式发出真实本机请求

```powershell
python "$advanced\ollama_client.py" --mode live --output '.local/advanced/ollama-live-v1'
ollama ps
```

客户端只连接 `127.0.0.1:11434`，不接受外部 URL，不自动拉取模型。若清单中没有该标签会先失败，不发生成请求；若有明确远程标记也会拒绝。

脚本使用非流式、num_ctx=1024、num_predict=128、temperature=0 与固定seed；这是小型教学设置，不是最佳参数承诺。检查 done_reason，长度上限结束时可能回答不完整；不要把截断当作完整答复。

## 4. 记录资源并停止

result.json 保存模型 digest、真实返回计数与纳秒级耗时字段。只有返回了有效计数和时长时才计算 tokens_per_second。用任务管理器与 ollama ps 记录内存、CPU/GPU使用情况，区分首次加载与后续请求，不虚构显存或速度。

```powershell
ollama stop qwen2.5:0.5b
```

stop 卸载该模型，不等于退出整个 Ollama 服务。按应用入口退出服务后再启动，确认模型清单仍在，再做同一题对照。下载缓存留在本机，不提交 GitHub。

## 验收

- [ ] 分清 preview、fixture 与 live，真实运行后再填写速度。
- [ ] 确认模型本地执行，问题与输出有实际记录。
- [ ] 能停止模型、重新启动后复查，并人工判断答案是否正确。
