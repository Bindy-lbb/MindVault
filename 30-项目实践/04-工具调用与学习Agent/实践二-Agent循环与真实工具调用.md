# 实践二：Agent 循环与真实工具调用

[项目入口](README.md) · [上一项](实践一-两个工具与固定工作流.md) · [下一项](实践三-LangGraph与MCP接入设计.md)

先按[循环卡片](../../10-知识卡片/Agent循环与停止条件.md)理解次数预算。本页从仓库根目录运行，不要求先安装框架。

## 1. 用预写响应看懂循环

```powershell
$agentScript = '.\30-项目实践\04-工具调用与学习Agent\study_agent.py'
python $agentScript --mode scripted --scenario success --output '.local/agent/scripted-v1'
python $agentScript --mode scripted --scenario bad_arguments --output '.local/agent/recovery-v1'
python $agentScript --mode scripted --scenario no_results --output '.local/agent/no-results-v1'
```

这三份是预写情节，真实执行搜索和读取，未请求模型。预期分别为：

| 情节 | 响应次数 / 工具尝试 | 观察什么 |
| --- | --- | --- |
| success | 3 / 2 | 搜索 → 读取 → 固定教学复习题 |
| bad_arguments | 4 / 3 | top_k 是字符串被拒绝，随后换成整数并读取 |
| no_results | 2 / 1 | 搜索空数组，最终说明依据不足 |

打开 messages.json，配对 assistant 的调用 ID 与 tool_call_id，检查下一次响应前已加入工具反馈。轨迹表明实际执行了什么；演示里修正参数的“决定”也是预先写好的，不能当成模型自己学会了恢复。

## 2. 验证预算能结束循环

```powershell
python $agentScript --mode scripted --scenario loop --max-tool-calls 2 --output '.local/agent/tool-limit-v1'
python $agentScript --mode scripted --scenario loop --max-rounds 2 --output '.local/agent/round-limit-v1'
```

重复搜索是刻意设计的情节。第一条预期 tool_limit：取到第三次响应时不再执行第三个工具；第二条预期 round_limit。停止后写记录，脚本以非零退出码 2 表示任务未正常完成，不是无限运行或成功生成题目。

## 3. 看真实请求的定义

```powershell
python $agentScript --mode preview
```

找到 `tools`、`parameters`、`tool_choice: auto` 和消息；本项目关闭思考模式、使用非流式请求。预览只显示初始任务与工具定义，不执行工具，也不能提前知道后续会读哪篇笔记。

当前使用 DeepSeek [Tool Calls](https://api-docs.deepseek.com/guides/tool_calls/)非思考模式。模型返回 arguments 字符串，本地仍要解析与校验；未开启 beta strict 模式。最终要求 JSON 来自提示词与本地检查，不保证模型每次格式都正确。

## 4. 准备好后自行用真实模型

本次内容整理没有代为发送模型请求。真实 Agent 可能多次请求，每轮会携带已有工具结果，按服务当时规则计费。先用配套自写资料，确认账户与模型支持。

```powershell
$agentKey = Read-Host '请输入自己的 DeepSeek API Key（不回显）' -AsSecureString
$env:DEEPSEEK_API_KEY = [System.Net.NetworkCredential]::new('', $agentKey).Password
$env:DEEPSEEK_MODEL = 'deepseek-flash'
python $agentScript --mode live --max-rounds 6 --max-tool-calls 6 --output '.local/agent/live-v1'
```

默认任务为“根据 API 密钥笔记，生成一条复习题，并给出答案和逐字依据”。以后可明确换任务与资料：

```powershell
python $agentScript --mode live --corpus '.local/agent-notes' --task '根据 RAG 笔记生成五道复习题，每题给出答案和依据。' --output '.local/agent/my-live-v1'
```

该条需先准备自己的资料目录。程序检查 1–5 题的格式与引文，不自动保证数量恰好符合任务、知识点覆盖充分或结论正确。未读到依据就不能通过有答案结果的引文检查。

结束后清理当前终端密钥变量：

```powershell
Remove-Item Env:DEEPSEEK_API_KEY -ErrorAction SilentlyContinue
Remove-Variable agentKey -ErrorAction SilentlyContinue
```

## 5. 读结果、保留失败

查看 result.md 的停止原因、trace.json 的实际工具/参数/结果与每轮 usage，以及 messages.json 的回传顺序。request_error 记录请求失败，invalid_response 记录协议不符，invalid_final 记录最终格式或引文未通过；预算结束也不能标成完成。

usage 为服务实际返回字段；scripted 为 null。不要把轮数当金额，也不要为了凑成功记录反复盲目调用。

- [ ] 核对题目与答案，逐字引用是否真正支持结论。
- [ ] 记录一次成功与一次失败，不把模型自述当成执行证据。
- [ ] 增加无答案但有相似词的问题，观察是否合理拒答。
- [ ] 使用[评估模板](评估记录模板.md)比较一次工具描述或预算改动。
