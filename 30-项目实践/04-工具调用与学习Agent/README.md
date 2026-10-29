---
created: 2026-10-23
status: "待实践"
tags: [项目实践, Agent, 工具调用]
type: "项目实践"
stage: "04 工具与Agent"
title: "项目 04：工具调用与学习 Agent"
---

# 项目 04：工具调用与学习 Agent

[项目目录](../README.md) · [第四阶段课程](../../20-课程笔记/第四阶段-工具调用与Agent课程及实践顺序.md) · [学习地图](../../学习地图.md)

阶段作品：给学习助手一个任务，让它搜索允许的笔记、读取原文，生成带答案与逐字依据的复习题。先验证工具，再看循环，最后按需接入真实模型。

## 文件与入口

| 文件 | 用途 |
| --- | --- |
| [study_agent.py](study_agent.py) | 两个工具、固定流程、预写响应循环、预览与真实模型调用 |
| [预写响应](examples/scripted_responses.json) | 成功、参数修正、无命中、重复调用四种演示情节 |
| [实践一](实践一-两个工具与固定工作流.md) | 不用 API 的真实工具执行 |
| [实践二](实践二-Agent循环与真实工具调用.md) | 消息回传、循环预算、结果校验、显式 live |
| [实践三](实践三-LangGraph与MCP接入设计.md) | 选修 LangGraph 固定流程与 MCP 接入设计 |
| [langgraph_workflow.py](langgraph_workflow.py) | 选修两节点图示例；需 langgraph，无模型请求 |
| [评估记录模板](评估记录模板.md) | 对照任务结果、工具行为、引文与预算 |
| [运行检查记录](运行检查记录.md) | 区分本次实际运行、替身检查与未实测部分 |

默认复用[第三阶段五篇自写笔记](../03-RAG知识库问答/README.md)所在的 `examples/notes/`；项目 02 和 03 保持原位置。核心练习只需 Python 标准库，当前检查环境为 Python 3.13.5。不要求 GPU 或安装 Agent 框架。

## 五种运行方式

| 模式 | 谁安排步骤 | 是否调用模型 |
| --- | --- | --- |
| tool | 你直接选择一个本地工具 | 否 |
| workflow（默认） | 代码固定“搜索第一条 → 读取” | 否，不生成复习题 |
| scripted | 预写响应安排动作，工具真实执行 | 否，最终题目也是预写教学内容 |
| preview | 只显示初始请求和工具定义 | 否，不执行工具 |
| live | DeepSeek 返回工具调用，程序校验执行，再把结果交回 | 是，可能多次请求并收费 |

preview 只显示第一轮请求，不预测之后会调用什么。scripted 只配套默认资料与默认任务，不是离线大模型。

## 最快开始

在 PowerShell 中从仓库根目录运行：

```powershell
Set-Location 'E:\my-projects\MindVault'
$env:PYTHONUTF8 = '1'
$agentScript = '.\30-项目实践\04-工具调用与学习Agent\study_agent.py'
python $agentScript --mode workflow --output '.local/agent/workflow-v1'
python $agentScript --mode scripted --scenario success --output '.local/agent/scripted-v1'
```

输出目录必须是新目录，每次换名。每次产生 `result.md`、`trace.json`、`messages.json`；内容含原文，先保存在被 Git 忽略的 `.local/`。Obsidian 通常不显示隐藏目录；要在其中阅读，可重新运行并指定新的 `--output '50-学习复盘/Agent实验一'`，再打开生成的 result.md，原文链接会按保存位置计算。

## 工具和预算

- `search_notes`：本地关键词检索，最多返回 3 个片段；不是语义检索或联网搜索。
- `read_note`：仅允许清单中的 note_id；首尾行包含，最多 60 行、6000 字符。
- 真实循环默认最多 6 次模型请求尝试、6 次工具尝试；本地参数错误也占工具次数。一轮可有多个调用，本项目逐个执行。
- 模型消息与工具定义合计最多 24000 字符；字符预算不是 Token 或金额限制。每次 API 等待最多 60 秒，不自动重试。
- 最终 JSON 检查字段、类型和逐字引文；只允许引用成功读取的原文，语义是否支持答案仍需人工判断。

最终内容格式为 `status/items`；status 可为 ok 或 insufficient_evidence。每条 items 含 question、answer、note_id、quote。正常结束不代表已满足所有用户要求，题目数量、覆盖和准确性仍要自己核对。

## 数据边界与后续扩展

只读工具没有写文件或发送消息的能力；结果由程序保存到你指定的新目录。live 会把任务、工具结果与会话历史发给 DeepSeek，密钥只从环境变量读取，不写入请求预览与记录。资料变化时返回错误，重新启动形成新快照。

每次启动为新会话，不自动恢复旧记录。不部署常驻聊天界面，也不替你定时运行。以后需要真实写入、外部服务、MCP 或更复杂 Agent 时，在当前可验证流程上逐项扩展。
