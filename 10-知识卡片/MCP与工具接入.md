---
created: 2026-10-23
status: 待读
tags: [知识卡片, Agent, MCP]
---

# MCP 与工具接入

[卡片目录](README.md) · [第四阶段课程](../20-课程笔记/第四阶段-工具调用与Agent课程及实践顺序.md)

## 一句话解释

**MCP 是让 AI 应用与外部工具、资料等系统按共同规则连接的协议。**像统一接口减少每次接入都重新约定格式的工作。[官方介绍](https://modelcontextprotocol.io/docs/getting-started/intro)

## 谁负责什么

- Host 是用户使用的 AI 应用，协调模型、连接和权限。
- Client 在应用内与某个 MCP Server 通信。
- Server 暴露具体能力，例如笔记搜索工具。

MCP 与 Function Calling 不在同一层：前者用于应用和外部系统连接，后者用于模型提出工具调用；应用可以把 MCP 提供的工具暴露给模型，也可以直接调用本地函数。[架构说明](https://modelcontextprotocol.io/docs/learn/architecture)

## 什么时候再学它

先跑通两个本地函数，不需要 MCP。以后希望同一个笔记工具被多个支持 MCP 的客户端复用，或需要连接已有服务，再学习服务端、传输方式与授权。

本阶段提供接入设计练习，没有安装或启动 MCP Server，不把本地函数命名为“MCP 已接入”。选组件时核对其当前协议版本和权限要求，不随意照抄历史配置。

## 小练习与自测

- [ ] 画出“AI 应用 → MCP Client → 笔记 Server → 选定资料”的关系。
- [ ] 写出哪些资料允许返回、哪些工具只读、发生失败时返回什么。

**问题：**使用 MCP 会自动得到更聪明、更安全的 Agent 吗？

**参考要点：**不会；协议解决连接规则，模型、工具设计、权限与评估仍需应用负责。

## 来源与相关笔记

以上 MCP 官方介绍与架构文档。核查：2026-10-23。MCP 为后续选修方向，非当前脚本依赖。

[工具调用与FunctionCalling](工具调用与FunctionCalling.md) · [Agent权限与提示注入](Agent权限与提示注入.md)
