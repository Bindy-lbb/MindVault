---
created: 2026-10-23
updated: 2026-10-23
status: 待读
source: "https://huggingface.co/docs/transformers/en/tokenizer_summary"
aliases:
  - 词元
tags:
  - 知识卡片
  - 大模型入门
---

# Token

[知识卡片目录](README.md) · [学习地图](../学习地图.md)

## 一句话解释

**Token 是模型处理文本时使用的小单位。它可能对应一个词、词的一部分、字符或字节片段，不能固定按“一个 Token 等于一个字”计算。**[概念依据：Anthropic Tokens 词汇表](https://platform.claude.com/docs/en/about-claude/glossary#tokens)

## 用生活里的事理解

把一篇文章想成一件要装箱的物品，分词器（Tokenizer）负责按规则把它拆成小块。模型实际接收的是这些小块对应的编号。

不同分词器的切法可能不同。同一句话交给不同模型，Token 数量也可能不同。[原理依据：Hugging Face 分词说明](https://huggingface.co/docs/transformers/en/tokenizer_summary)

## 一个具体例子

**自拟教学场景：**两篇文章都是 1000 个字符，一篇中文、一篇英文，不能仅凭字符数断定它们消耗相同的 Token。

同样，“请总结这篇文章”这几个字也会占用输入 Token；输入不只有文章正文。

实际数量要用目标模型对应的分词器或计数接口确认，不把这里的示意当成实测结果。[计数依据：Anthropic Tokens 词汇表](https://platform.claude.com/docs/en/about-claude/glossary#tokens)

## 它为什么重要

| 关注点 | 通俗理解 |
| --- | --- |
| 输入 | 送给模型的要求、资料和消息也需要被处理 |
| 输出 | 模型生成的回答也由 Token 组成 |
| 容量 | [上下文](上下文.md)的容量常用 Token 表示 |
| 费用 | 很多模型 API 按 Token 用量计费，输入、输出等类别可能采用不同规则，以服务商文档为准 |

本卡片只介绍概念，不给所有语言、所有模型套用一个固定换算比例。

## 放到 MindVault 中有什么用

以后给文章生成摘要时，可以先观察文章长度、请求用量和输出长度。资料太多时，再学习分批处理或先检索相关段落。

## 容易误解的地方

- Token 数、字数、词数是不同的计数方式。
- 常见的“一个 Token 大约等于多少字符”只是特定条件下的估算。
- API 中的访问凭据有时也被称为 token；那是另一种用法，不要和文本 Token 混淆。

## 我的理解与验证

- [ ] 用自己的话解释 Token 和汉字数量的区别。
- [ ] 到模型调用阶段，用同一模型的计数工具分别检查两段文本，记下模型名、文本与实际数量。
- [ ] 修改提示词后比较一次输入用量，观察额外的要求是否增加了 Token。

## 自测与参考答案

**问题：**两段文字各有 1000 个字符，它们的 Token 数一定相同吗？

**参考要点：**不一定，数量还取决于文本内容和目标模型的分词方式。实际结果要用对应的分词器或计数接口确认。

## 来源

- [Hugging Face：Tokenization algorithms](https://huggingface.co/docs/transformers/en/tokenizer_summary)，用于分词与切分差异。
- [Anthropic：Glossary — Tokens](https://platform.claude.com/docs/en/about-claude/glossary#tokens)，用于 Token 定义与计数方式。
- 来源核查日期：2026-10-23。装箱类比和对比场景为本卡片自拟，练习尚待执行。

## 相关笔记

[大模型](大模型.md) · [上下文](上下文.md) · [API](API.md)

## 仍有疑问

- [ ] 我准备使用的模型，具体怎样统计和计费？选定模型后再核对。
