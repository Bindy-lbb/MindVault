---
created: 2026-10-23
status: 待读
source: "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview"
tags: [知识卡片, API入门]
---

# HTTP 请求与响应

[知识卡片目录](README.md) · [第二阶段课程](../20-课程笔记/第二阶段-模型API课程与实践顺序.md)

## 一句话解释

**HTTP 是客户端和服务端交换消息的一套规则。程序发出请求，服务端返回响应。**调用网络模型 API 时，先把任务按接口约定发过去，再处理返回结果。[依据：MDN HTTP 概述](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)

## 用生活里的事理解

像寄一份带地址、说明和正文的信，再收到回信。地址决定发到哪里，说明决定如何理解内容，正文承载具体任务。

## 一次调用看哪些部分

| 部分 | 本次练习中的例子 |
| --- | --- |
| 地址 | `https://api.deepseek.com/chat/completions` |
| 方法 | `POST`，向接口提交任务 |
| 请求头 | `Content-Type: application/json`；认证信息另放在认证头 |
| 请求体 | 模型名称、消息列表等 JSON 数据 |
| 响应状态 | HTTP 状态码，先判断请求处理情况 |
| 响应内容 | 再从返回 JSON 中提取回答、结束原因和用量 |

地址和具体字段以 [DeepSeek 首次调用](https://api-docs.deepseek.com/zh-cn/)为本项目的接口实例，其他服务可能不同。

## 容易误解的地方

- 收到 HTTP 响应，还要检查状态码和返回结构。
- 网络请求成功，不代表模型生成的观点正确；还要对照原文检查。
- `POST` 是发送请求的方法，不等于已经把笔记保存到 GitHub。

## 我的理解与验证

- [ ] 在项目 02 的预览中找到地址、方法、请求体。
- [ ] 画出“本地文件 → 请求 → 模型响应 → 草稿”的流程。

## 自测与参考答案

**问题：**收到正常响应后，可以直接把摘要视为可信原文吗？

**参考要点：**还要验证回答是否完整、格式是否正确、内容是否有依据。

## 来源

- [MDN：Overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)。
- [DeepSeek：首次调用 API](https://api-docs.deepseek.com/zh-cn/)。
- 核查日期：2026-10-23。类比和学习场景为自拟。

## 相关笔记

[API](API.md) · [JSON](JSON.md) · [API密钥与环境变量](API密钥与环境变量.md)
