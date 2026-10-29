---
created: 2026-10-23
status: "待学习"
tags: [知识卡片, RAG]
type: "知识卡片"
stage: "03 RAG"
---

# TopK 与重排序

[知识卡片目录](README.md) · [第三阶段课程](../20-课程笔记/第三阶段-RAG课程与实践顺序.md)

## 一句话解释

**Top K 是最多保留排名靠前的 K 个候选；重排序是用另一种方法重新比较候选与问题。**像先从书架选出十本，再仔细翻看选三本。

## 用本项目理解

`--top-k 3` 最多返回 3 个片段，不保证是 3 篇不同文件。重叠切分可能让同一篇重复占位。`--min-score` 是本次方法的过滤设置，默认只保留正分；它不是可靠性保证。

增加 K 可能提高找到答案的机会，也可能塞进干扰片段、挤占上下文。模型实际能看到哪些片段，还受应用给上下文设定的预算影响。

## 重排序做什么

Sentence Transformers 的教程展示先召回候选，再由 CrossEncoder 对问题与候选成对打分。它能调整已找出的候选顺序，但不能找回第一轮完全漏掉的资料。[官方教程](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)

本练习没有默认安装重排模型。先比较 K=1 与 K=3；有证据表明候选顺序经常不对，再尝试重排，并记录额外时间。

## 小练习与自测

- [ ] 记录同一问题在 K=1、K=3 时是否包含目标来源。
- [ ] 找出重复片段，说明是否影响有效信息量。

**问题：**K=10 一定比 K=3 好吗？

**参考要点：**不一定；要分别比较召回、答案、重复内容、延迟与成本。

## 来源与相关笔记

[Sentence Transformers Retrieve & Re-Rank](https://sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html)，核查：2026-10-23。K 值为本项目实验选择。

[文档切分与重叠](文档切分与重叠.md) · [RAG评估与故障定位](RAG评估与故障定位.md)
