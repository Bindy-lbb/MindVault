---
created: 2026-10-23
status: "待学习"
source: "https://api-docs.deepseek.com/zh-cn/"
tags: [知识卡片, API入门]
type: "知识卡片"
stage: "02 模型API"
---

# API 密钥与环境变量

[知识卡片目录](README.md) · [第二阶段课程](../20-课程笔记/第二阶段-模型API课程与实践顺序.md)

## 一句话解释

**API 密钥是某些服务识别调用身份的凭据；环境变量是程序从运行环境中读取配置的一种方式。**本项目从 `DEEPSEEK_API_KEY` 读取密钥，通过认证请求头使用它。[服务依据](https://api-docs.deepseek.com/zh-cn/)、[Python 环境变量说明](https://docs.python.org/zh-cn/3.13/library/os.html#os.environ)

## 用生活里的事理解

密钥像门禁卡；环境变量像运行程序时交给它的配置袋。程序需要使用配置，但学习笔记只需记录配置名称和设置方法。

## 一个具体例子

```python
import os

api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
print("已设置密钥" if api_key else "尚未设置密钥")
```

这段自拟示例只显示是否配置，不显示实际密钥。可先不设置，观察“尚未设置密钥”。

## 本项目怎样使用

- `preview` 和 `mock` 模式不读取密钥、不请求外网。
- `live` 模式才读取密钥；缺失时先报错。
- 在项目实践一中，用当前 PowerShell 会话设置环境变量。
- 脚本不自动读取 `.env` 文件；环境变量和 `.env` 文件不是同一种东西。

## 容易误解的地方

- 环境变量名可以写进代码；真实值放在本地配置中。
- `.gitignore` 可忽略常见配置文件，但不会阻止把密钥误写进普通笔记。
- 认证失败先检查配置和服务文档，不靠反复请求解决。[错误码参考](https://api-docs.deepseek.com/zh-cn/quick_start/error_codes/)

## 我的理解与验证

- [ ] 未配置密钥时运行示例，观察状态。
- [ ] 准备真实调用时，按实践一设置会话变量，再运行脚本。

## 自测与参考答案

**问题：**教程写了 `DEEPSEEK_API_KEY`，是否说明已经包含可用密钥？

**参考要点：**这只是配置名称，真实值需要账户持有人在本地设置。

## 来源

- [DeepSeek：首次调用 API](https://api-docs.deepseek.com/zh-cn/)。
- [Python 3.13：os.environ](https://docs.python.org/zh-cn/3.13/library/os.html#os.environ)。
- 核查日期：2026-10-23。示例为自拟。

## 相关笔记

[HTTP请求与响应](HTTP请求与响应.md) · [虚拟环境与依赖](虚拟环境与依赖.md) · [API](API.md)
