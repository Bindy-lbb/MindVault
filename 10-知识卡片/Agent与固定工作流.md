---
created: 2026-10-23
status: 待读
tags: [知识卡片, Agent]
---

# Agent 与固定工作流

[卡片目录](README.md) · [第四阶段课程](../20-课程笔记/第四阶段-工具调用与Agent课程及实践顺序.md)

## 一句话解释

**固定工作流按程序预先安排的步骤执行；Agent 让模型根据任务和反馈选择下一步。**像复习时按固定清单学习，或根据答题情况临时决定查哪本书。

## 在 MindVault 中有什么不同

- 固定流程：搜索“API” → 读取第一条结果 → 展示原文。顺序由代码决定。
- Agent：模型发现材料不够，换关键词搜索，再读取另一篇，最后生成有依据的复习题。模型能选择行动，但工具权限和停止预算仍由程序控制。

这是[LangGraph 官方教程](https://docs.langchain.com/oss/python/langgraph/workflows-agents)采用的区分方式；不同资料对 Agent 一词的范围略有差别，先观察谁决定流程。

## 为什么先做简单流程

任务明确时，固定步骤更容易检查；动态决策增加了出错位置，也可能增加延迟与调用成本。先验证两个工具有用，再决定是否需要模型安排步骤。[设计参考](https://www.anthropic.com/research/building-effective-agents)

项目的 `workflow` 真正执行本地工具；`scripted` 用预写响应演示循环；只有 `live` 才由真实模型决定调用。不能把脚本演示当成 Agent 效果实测。

## 小练习与自测

- [ ] 在运行轨迹中指出哪一步由代码安排、哪一步由模型选择。
- [ ] 写出一个固定流程就能解决的学习任务。

**问题：**代码里有 while 循环，就一定是 Agent 吗？

**参考要点：**不一定。循环可以只是固定重试；关键看模型是否参与决定行动和继续方式。

## 来源与相关笔记

以上 LangGraph 与 Anthropic 官方文章；[HF：什么是智能体](https://huggingface.co/learn/agents-course/zh-CN/unit1/what-are-agents)。核查：2026-10-23。生活类比与本库例子为自写。

[RAG检索增强生成](RAG检索增强生成.md) · [工具调用与FunctionCalling](工具调用与FunctionCalling.md)
