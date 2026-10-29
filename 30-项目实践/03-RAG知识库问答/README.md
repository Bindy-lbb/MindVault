---
created: 2026-10-23
status: "待实践"
tags: [项目实践, RAG]
type: "项目实践"
stage: "03 RAG"
title: "项目 03：RAG 知识库问答"
---

# 项目 03：RAG 知识库问答

[项目目录](../README.md) · [第三阶段课程](../../20-课程笔记/第三阶段-RAG课程与实践顺序.md) · [学习地图](../../学习地图.md)

从五篇教学笔记开始：读 Markdown → 按行切分并记录来源 → 建索引 → 按问题检索 → 查看原文 → 按需交给模型回答 → 核对引用。先不用数据库或网页框架。

## 文件与入口

| 文件 | 用途 |
| --- | --- |
| [rag_practice.py](rag_practice.py) | build / search / ask / evaluate 四个教学命令 |
| [实践一](实践一-加载切分与关键词检索.md) | 无密钥、无第三方依赖的真实本地检索 |
| [实践二](实践二-带引用问答与评估.md) | 原文摘录、请求预览、显式 live、来源级评估 |
| [实践三](实践三-语义检索与索引更新.md) | 选修真实 Embedding，对比与索引更新 |
| [示例问题集](examples/questions.json) | 5 条有答案、1 条资料外问题；目标来源手写 |
| [评估记录模板](评估记录模板.md) | 分别记录检索、答案、引用和费用 |
| [运行检查记录](运行检查记录.md) | 本次实际运行范围与尚未实测的部分 |

`examples/notes/` 是五篇自写教学资料。默认不遍历整个 MindVault。索引包含原文和绝对资料路径，只在本地 `.local/` 保存，仓库已忽略该目录。

## 从哪里运行

Windows PowerShell，在仓库根目录打开终端：

```powershell
Set-Location 'E:\my-projects\MindVault'
$env:PYTHONUTF8 = '1'
$ragScript = '.\30-项目实践\03-RAG知识库问答\rag_practice.py'
python $ragScript build --index '.local/rag/keyword-v1.json'
python $ragScript search --index '.local/rag/keyword-v1.json' --question 'API 密钥放哪里？'
```

需要可用 Python，当前离线检查环境为 Python 3.13.5。`python --version` 应能显示版本。所有命令只新建文件，已有文件会拒绝覆盖；重复练习时换输出名称，例如 `v2`。

## 四种问答状态

- `extractive`（默认）：真实检索后保存原文与文件来源；没有模型综合回答。
- `preview`：显示实际会发送的问题、片段与 JSON 要求，不读取密钥、不调用生成 API。
- `live`：显式选择才发送片段至 DeepSeek，复用[项目 02 网络调用](../02-模型API与文章整理/model_api.py)，可能收费。
- `local_abstention`（结果标记）：没找到候选时本地说明依据不足，即使选择 live 也不请求模型。

语义模式的首次运行可能联网下载模型；即使问答是 preview，选择 semantic 索引仍可能触发该本地模型加载。默认 keyword 不下载模型。

## 练习边界

关键词方法是中英文特征重合，不是向量检索、BM25 或模型问答。语义模式使用真实模型编码与点积遍历，未部署向量数据库。最低分和 K 只是实验参数，不是置信度承诺。

脚本限制资料最多 100 篇、合计 200000 字符、单篇 200000 字节；问题最多 2000 字符；问答片段合计最多 12000 字符。这些是教学限制，不是模型 Token 上限。语义编码另检查模型实际输入长度。

查询前会重读资料，检查文件新增、修改、删除和片段来源。当前是小规模全量校验与重建，不面向多人服务。索引请只加载自己建立的可信文件；资料中的命令作为正文处理，不会执行。

在 Obsidian 中按 `Ctrl+O` 打开本项目入口或三篇实践文档。`.local/` 通常不会显示在 Obsidian 文件树中；实验输出先用文本编辑器查看，要保留的问答可直接用新的 `--output '50-学习复盘/我的RAG实验.md'` 生成，来源链接会按保存位置计算，再在 Obsidian 打开。这不是持续运行的聊天窗口。脚本不会自动修改学习笔记或自动提交 GitHub。
