---
created: 2026-10-23
status: "待实践"
tags: [项目实践, 模型进阶]
type: "项目实践"
stage: "06 进阶"
title: "项目 06：模型原理、本地部署与微调"
---

# 项目 06：模型原理、本地部署与微调

[项目目录](../README.md) · [进阶课程](../../20-课程笔记/进阶阶段-模型原理本地部署与微调.md) · [学习地图](../../学习地图.md)

目标：看懂一点内部计算，能验证一次本地模型请求，并在有条件时完成有基准与隔离评估的 LoRA 实验。三条分支按需选，不把 RAG 笔记库自动转为训练集。

## 文件与实践

| 文件 | 用途 |
| --- | --- |
| [实践一](实践一-注意力与损失数值实验.md)、[principles_lab.py](principles_lab.py) | 标准库矩阵、单头因果注意力、交叉熵一步更新 |
| [实践二](实践二-小矩阵LoRA与适配器.md)、[toy_lora.py](toy_lora.py) | 真正优化小矩阵 A/B，保存并重载本库玩具适配器 |
| [实践三](实践三-Ollama本地模型调用.md)、[ollama_client.py](ollama_client.py) | preview/fixture 不调用模型；live 连接明确的本机模型 |
| [实践四](实践四-数据检查与真实LoRA选修.md)、[lora_experiment.py](lora_experiment.py) | plan 默认仅检查数据；train/evaluate 才加载真实模型 |
| [data_tools.py](data_tools.py) | 数据、重复问题、模板前缀、标签屏蔽与运行版本检查 |
| [训练数据](data/train.jsonl)、[验证数据](data/validation.jsonl)、[测试数据](data/test.jsonl) | 20条本库自写单轮示范，12/4/4分组，验证格式适配流程 |
| [实验记录模板](进阶实验记录模板.md)、[运行检查](运行检查记录.md) | 区分数值实验、固定响应、真实模型与未实测部分 |

## 先跑不下载模型的部分

从仓库根目录 PowerShell 执行：

```powershell
Set-Location 'E:\my-projects\MindVault'
$env:PYTHONUTF8 = '1'
$advanced = '.\30-项目实践\06-模型原理本地部署与微调'
python "$advanced\principles_lab.py" --output '.local/advanced/principles-v1.json'
python "$advanced\toy_lora.py" train --output '.local/advanced/toy-v1'
python "$advanced\lora_experiment.py" --mode plan --output '.local/advanced/plan-v1'
```

核心离线部分只用 Python 标准库，当前检查环境为 3.13.5；不需要 Ollama、PyTorch、GPU 或云账户。输出必须是新文件/目录，不覆盖已有结果。

## 四种结果不要混用

- 数值实验实际进行了计算与小矩阵训练，没有训练语言模型。
- Ollama fixture 是固定教学响应，没有本地模型速度或 Token 实测。
- 微调 plan 检查数据与设置，不安装依赖、不验证 Tokenizer、不执行训练。
- Ollama live 与 LoRA train/evaluate 需自行准备条件，才会执行真实模型推理或训练；后者可能从 HF 下载权重。

默认不读取完整 MindVault、不抓网页、不调用付费云 API。真实模型下载、依赖、缓存与实验产物留在本地；不要将权重、.venv 或私人训练数据加入 Git。

Obsidian 通常不显示 `.local/`。在[实验记录模板](进阶实验记录模板.md)复制一份到 `50-学习复盘/`，填写结果与输出路径，避免把大型训练输出搬进笔记目录。
