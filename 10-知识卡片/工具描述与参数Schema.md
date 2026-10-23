---
created: 2026-10-23
status: 待读
tags: [知识卡片, Agent]
---

# 工具描述与参数 Schema

[卡片目录](README.md) · [第四阶段课程](../20-课程笔记/第四阶段-工具调用与Agent课程及实践顺序.md)

## 一句话解释

**工具描述告诉模型何时使用；参数 Schema 告诉模型应该填写哪些字段和类型。**像表单的用途说明与填写规则。

## 本项目的约定

`search_notes(query, top_k)` 搜索当前允许的资料；`read_note(note_id, start_line, end_line)` 读取指定笔记行。note_id 必须来自本次资料清单，例如 `01-API配置.md`，不是任意磁盘路径。

```json
{"type":"object","properties":{"query":{"type":"string"},"top_k":{"type":"integer","minimum":1,"maximum":3}},"required":["query","top_k"],"additionalProperties":false}
```

这是本库搜索参数的简化示例。名称要具体，描述交代适用场景、限制和返回内容。[工具设计参考](https://huggingface.co/learn/agents-course/zh-CN/unit1/tools)

## 声明之后仍要检查

服务端支持哪些 Schema 字段要按接口核对；本项目没有开启厂商严格模式，而是在本地再验证字段、类型与范围。字符串 `"3"` 不是整数 3，额外字段也会拒绝。

DeepSeek API 文档提醒模型可能生成无效 JSON 或 Schema 之外的参数。[接口依据](https://api-docs.deepseek.com/api/create-chat-completion/)

## 小练习与自测

- [ ] 找到脚本中的工具描述，改写成更明确的一句话再比较结果。
- [ ] 在脚本模拟中观察参数不合法时有没有执行工具。

**问题：**参数是合法 JSON，就可以执行了吗？

**参考要点：**还要符合字段、类型、数值范围、资料范围与当前权限。

## 来源与相关笔记

以上 HF 与 DeepSeek 官方文档。核查：2026-10-23。字段和本地限制为本项目设计。

[JSON](JSON.md) · [结构化输出与校验](结构化输出与校验.md) · [Agent权限与提示注入](Agent权限与提示注入.md)
