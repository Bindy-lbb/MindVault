---
created: 2026-10-23
status: "待实践"
tags: [项目实践, 评估与部署]
type: "项目实践"
stage: "05 评估与部署"
title: "项目 05：评估与本地部署"
---

# 项目 05：评估与本地部署

[项目目录](../README.md) · [第五阶段课程](../../20-课程笔记/第五阶段-评估与部署课程及实践顺序.md) · [学习地图](../../学习地图.md)

从“能跑一次”走到“有评估记录、能重新启动、能回到旧版”。本项目默认标准库、离线评估、回环检索服务，不使用真实模型 API，不部署权重或云服务。

## 文件导航

| 文件 | 用途 |
| --- | --- |
| [evaluate.py](evaluate.py) | run 生成评估，compare 对照同代码改变 K |
| [题集](examples/eval_cases.json) | 5 道 dev、3 道 holdout，含多来源与资料外问题 |
| [local_service.py](local_service.py) | index 建库、serve 启动本机 JSON 检索 API |
| [service.example.json](service.example.json) | 资料、索引、日志、端口与切分配置 |
| [release.py](release.py) | package 新建本地发布目录，verify 核对文件摘要 |
| [实践一](实践一-评估集与基准对比.md) | 题集、指标、逐题结果与人工判断 |
| [实践二](实践二-本地服务与健康检查.md) | 启动、请求、日志、停止、资料变更 |
| [实践三](实践三-发布包重启与回滚.md) | 文件校验、独立运行、重启与恢复 |
| [复盘模板](评估与发布复盘模板.md) | 保存评估、发布、访问与恢复证据 |
| [运行检查](运行检查记录.md) | 本次实际执行范围与限制 |

需要可用 Python；当前检查环境为 3.13.5。评估依赖项目 03/04 保持原位置，默认使用第三阶段五篇自写示例。发布包只带本机服务、检索脚本和选定资料，不需要整座知识库或旧项目目录。

## 从这里开始

从仓库根目录 PowerShell 运行：

```powershell
Set-Location 'E:\my-projects\MindVault'
$env:PYTHONUTF8 = '1'
$stage5 = '.\30-项目实践\05-评估与本地部署'
python "$stage5\evaluate.py" run --top-k 1 --output '.local/eval/k1-v1'
python "$stage5\evaluate.py" run --top-k 3 --output '.local/eval/k3-v1'
```

报告与发布输出必须使用新目录，避免覆盖；已有索引也拒绝覆盖。`.local/` 被 Git 忽略且通常不显示在 Obsidian 文件树中。要在 Obsidian 保留评审，可给评估指定新的 `--output '50-学习复盘/第五阶段评估一'`，打开 review.md；完整运行日志与索引继续放本地忽略目录。

## 怎样理解结果

来源命中、来源覆盖和原句覆盖是自动检索指标；人工答案/引用评分保持 null。四个 Agent 情节使用预写响应，不能当真实模型表现。服务只返回关键词检索片段，`model_api_requests` 为 0。

健康检查区分 health 与 ready；检索失败和索引失效不混作正常无答案。日志只记录 GET 请求元数据，不记录问题原文、笔记正文、认证信息或原始 URL。

## 本阶段的边界

服务固定监听 127.0.0.1，只供本机教学，没有网页界面、认证、HTTPS、生产进程管理或远程访问。运行后按 Ctrl+C 停止；本次自动检查结束后不留常驻服务。

发布是创建本地文件目录，不创建 GitHub Release 或云资源。真实模型费用与质量仍需在项目 03/04 手动验证；若以后做公开服务，再单独处理访问、平台、资源和运维需求。
