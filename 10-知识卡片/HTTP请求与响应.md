---
created: 2026-10-23
status: "待学习"
source: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview"
tags: [知识卡片, API入门]
type: "知识卡片"
stage: "02 模型API"
updated: 2026-10-29
---

# HTTP 请求与响应

[卡片目录](README.md) · [课程入口](../20-课程笔记/第二阶段-模型API课程与实践顺序.md)

## 一句话解释

**HTTP 是客户端与服务端交换消息的规则：客户端发请求，服务端返回状态、头和内容。**网络模型 API 通过这条通道接收任务并交回生成结果。

## 为什么需要它

遇到调用问题时，先分清请求有没有发出、服务怎样回应、返回内容是否能用。地址、认证、JSON 和模型回答各在不同位置，不能只把整段响应当成摘要。

HTTPS 在 HTTP 之上提供传输保护，仍需正确目标地址与应用层认证。

## 用 MindVault 走一遍

项目 02 的实际请求结构是：

| 部分 | 本库设置 | 用途 |
| --- | --- | --- |
| 地址 | https://api.deepseek.com/chat/completions | 指定服务和接口 |
| 方法 | POST | 提交生成任务 |
| Content-Type 头 | application/json | 说明请求体格式 |
| Authorization 头 | Bearer 后接本地密钥 | 认证，不放进正文示例 |
| 请求体 | model、messages 等 JSON | 任务内容与设置 |

程序先把 Python 字典序列化为 JSON，再编码成 UTF-8 字节发送。preview 会显示方法、地址和 body，但不会读取真实 Key，也不代表请求已发生。

响应分两层看：HTTP 状态告诉你请求处理情况；返回 JSON 的 choices、finish_reason、message 和 usage 告诉你生成结果与用量。即使 HTTP 成功，也可能内容空、生成被截断或字段不合要求。

POST 是一种请求方法，不是“将笔记发布到 GitHub”。当前程序收到结果后仍要校验、写本地草稿、人工核对，之后再单独提交版本。

## 每一步的输入输出

| 步骤 | 输入 | 输出 |
| --- | --- | --- |
| 构造 | 地址、方法、头、JSON 体 | HTTP 请求 |
| 发送 | 请求与网络等待设置 | HTTP 响应或连接错误 |
| 判断状态 | 状态码 | 正常或服务错误 |
| 解析内容 | UTF-8 响应字节 | 服务 JSON |
| 提取回答 | choices 等结构 | 内容字符串与元信息 |
| 校验保存 | 内容与原文 | 草稿或明确拒绝 |

状态码的具体含义按服务文档核对，不能把所有非 200 都归为“模型幻觉”。

## 常见疑问

**请求头和请求体有什么区别？**头传认证与格式等元信息，体传任务数据；当前 Key 不放到 messages。

**200 代表事实全对吗？**只代表相应处理成功，内容准确性另查。

**GET 和 POST 哪个更高级？**它们是不同方法；按接口约定使用，不凭好恶互换。

**返回的 JSON 就是模型写的 JSON 吗？**外层服务响应有固定结构，content 内还可能是另一份模型 JSON，需要分别解析。

**preview 能测认证吗？**不能，没有真实发请求。真实认证需要具备账户后显式 live。

## 小练习与自测

**题目：**HTTP 正常但 finish_reason 表示长度停止，能按完整摘要保存吗？

**参考答案：**当前脚本会拒绝，先检查输出预算与任务，不能把截断当作完成。

**练习：**在 hello preview 找四项：方法、地址、模型名、消息；再在 mock 输出分清 answer 和 metadata。

### 动手记录

- [ ] 在项目 02 的预览中找到地址、方法、请求体。
- [ ] 画出“本地文件 → 请求 → 模型响应 → 草稿”的流程。

## 本库实现与实践入口

看 `model_api.py` 的 `call_api()` 和 `extract_answer()`，对应网络交换与生成结果检查。请求不跟随重定向，不把认证交给意外跳转目标。

[项目 02](../30-项目实践/02-模型API与文章整理/README.md) · [实现代码](../30-项目实践/02-模型API与文章整理/model_api.py) · [实践一：首次调用](../30-项目实践/02-模型API与文章整理/实践一-首次API调用.md) · [实践二：文章整理](../30-项目实践/02-模型API与文章整理/实践二-文章整理工具.md) · [评估模板](../30-项目实践/02-模型API与文章整理/评估记录模板.md)

先 preview，再 mock；live 需自己的账户和凭据，向服务发送任务和所选正文，可能产生费用。本库核心离线练习不需要额外 SDK。

## 来源与延伸阅读

[MDN HTTP 概述](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)、[Python urllib.request](https://docs.python.org/zh-cn/3.13/library/urllib.request.html)和[DeepSeek 首次调用](https://api-docs.deepseek.com/zh-cn/)：协议与本库接口实例。

核查日期：2026-10-29。外部资料用于核对规则，核心解释和练习答案已写在本页。生活类比、表格和教学数据为本库整理；固定模拟和数字演算不等于真实模型实测。

## 相关笔记与下一步

[下一张：SDK与HTTP调用](SDK与HTTP调用.md) · [学习总导航](../学习总导航.md) · [本阶段阅读顺序](../20-课程笔记/第二阶段-模型API课程与实践顺序.md)
