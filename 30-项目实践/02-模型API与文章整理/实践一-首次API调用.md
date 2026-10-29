# 实践一：首次 API 调用

[项目首页](README.md) · [实践二](实践二-文章整理工具.md)

运行前可看[统一运行约定与排错](../../40-工具手册/实践运行约定与排错.md)：首段从仓库根目录开始；新终端需重新设置会话变量，输出使用新名称。

## 第一步：解释请求

在 MindVault 根目录执行：

```powershell
Set-Location 'E:\my-projects\MindVault'
$env:PYTHONUTF8 = '1'
python '.\30-项目实践\02-模型API与文章整理\model_api.py' hello --mode preview
```

找到地址、`model`、两条消息、`max_tokens`、`stream` 和 `thinking`，对照知识卡片解释。此时不需要账户，不会产生模型请求。

## 第二步：运行离线模拟

```powershell
python '.\30-项目实践\02-模型API与文章整理\model_api.py' hello --mode mock --output '.\.local\stage2\hello-mock-01.json'
```

打开输出文件，确认回答明确写着“离线模拟”、`execution_mode` 为 `mock`，且 `usage` 为 `null`。再次使用同一路径会提示换文件名。

## 第三步：准备真实调用

先自行查看 [官方首次调用](https://api-docs.deepseek.com/zh-cn/)和 [当前价格](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)，确认账户可用与当前模型名。

在自己的 PowerShell 会话中设置：

```powershell
$stage2Key = Read-Host '请输入自己的 DeepSeek API Key' -AsSecureString
$env:DEEPSEEK_API_KEY = [System.Net.NetworkCredential]::new('', $stage2Key).Password
$env:DEEPSEEK_MODEL = 'deepseek-flash'
```

密钥通过交互输入，不需要填写到笔记或脚本。这个项目只读取环境变量，不自动加载 `.env`。重新打开终端后可能需要重新设置。

## 第四步：自行发出一次请求

准备好后执行：

```powershell
python '.\30-项目实践\02-模型API与文章整理\model_api.py' hello --mode live --max-output-tokens 300 --output '.\.local\stage2\hello-live-01.json'
```

该命令会发出一次真实请求。输出中检查回答、请求模型、返回模型、请求标识、用量和耗时。返回结构异常或生成未正常结束时，脚本返回失败；不要把模拟记录当作本次结果。

结束后可清理当前会话中的密钥变量：

```powershell
Remove-Item Env:\DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
Remove-Variable stage2Key -ErrorAction SilentlyContinue
```

## 第五步：记录成功和失败

- [ ] 解释预览请求的每个主要字段。
- [ ] 检查模拟结果的模式与用量。
- [ ] 自己完成一次 live 调用，记录实际返回用量。
- [ ] 去掉密钥再运行，观察本地提示，确认没有发送请求。
- [ ] 遇到 HTTP 错误时，按 [错误处理卡片](../../10-知识卡片/超时限流与重试.md)识别原因。

代码提供者未使用你的真实账户调用接口；真实认证、模型响应质量和费用由本次个人实验确认。
