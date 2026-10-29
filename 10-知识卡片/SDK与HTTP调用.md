---
created: 2026-10-23
status: "待学习"
source: "https://github.com/datawhalechina/llm-universe"
tags: [知识卡片, API入门]
type: "知识卡片"
stage: "02 模型API"
---

# SDK 与 HTTP 调用

[知识卡片目录](README.md) · [第二阶段课程](../20-课程笔记/第二阶段-模型API课程与实践顺序.md)

## 一句话解释

**直接 HTTP 调用需要自己组织请求并解析响应；SDK 是将常用接口操作封装成代码函数的工具包。**两种方式都需要遵守服务商当前接口约定。

## 用生活里的事理解

直接调用像按表单逐项填写；SDK 像提供了填表助手。助手能省步骤，仍需知道要交哪些材料、怎样辨认结果。

## 为什么本项目先用标准库

Python 的 `urllib.request` 已提供 HTTP 请求能力。[标准库参考](https://docs.python.org/zh-cn/3.13/library/urllib.request.html)

当前练习先看清地址、认证、消息、返回 JSON，使用已有 Python 即可运行预览和模拟。熟悉这些环节后，再按教程选择 SDK，记录安装版本和实际参数。

## 怎样配合成熟教程学习

Datawhale 的大模型应用课程包括模型调用、提示词及应用开发。先学习它的 API 章节，再用当前服务商文档核对代码中的模型名、依赖和调用字段。[课程入口](https://github.com/datawhalechina/llm-universe)

看到与本项目不同的示例时，先对照“输入、请求、返回、保存”四个环节理解。

## 容易误解的地方

- 安装了 SDK，不等于已经有可用的模型账户或密钥。
- SDK 的方法名不一定等于 HTTP 字段名。
- SDK 版本与模型服务文档需要一起记录，旧示例可能需要调整。

## 我的理解与验证

- [ ] 在项目代码中找到 HTTP 请求与响应解析的位置。
- [ ] 在教程中找一段 SDK 示例，指出对应输入和返回结果。

## 自测与参考答案

**问题：**从 HTTP 改为 SDK 后，是否可以省略对生成内容的检查？

**参考要点：**仍需要检查。SDK 方便调用，不能替代格式、依据与事实核对。

## 来源

- [Datawhale：llm-universe](https://github.com/datawhalechina/llm-universe)。
- [Python 3.13：urllib.request](https://docs.python.org/zh-cn/3.13/library/urllib.request.html)。
- 核查日期：2026-10-23。类比和练习为自拟。

## 相关笔记

[HTTP请求与响应](HTTP请求与响应.md) · [API](API.md) · [虚拟环境与依赖](虚拟环境与依赖.md)
