---
created: 2026-10-23
status: 待自己复现
tags:
  - 项目实践
  - 编程基础
---

# 项目 01：Markdown 读取与 JSON 保存

[项目目录](../README.md) · [学习地图](../../学习地图.md) · [配套线上课程](../../20-课程笔记/第一阶段-线上课程与阅读顺序.md)

## 我要做出什么

运行 [read_note.py](read_note.py)，读取一篇 Markdown，显示文件名和正文，并可保存为新的 JSON 文件。需要已有 Python，项目只使用标准库，不调用模型或外部服务。

这是为 MindVault 自编的教学项目，参考 Python 官方文件、路径和 JSON 文档，不是课程作业的标准答案。

## 先运行一次

在 PowerShell 中逐条运行：

```powershell
Set-Location 'E:\my-projects\MindVault'
python --version
python '.\30-项目实践\01-Markdown读取小程序\read_note.py'
```

默认读取配套的 [示例笔记](examples/示例笔记.md)，在终端显示文件名、字符数和完整原文。

`character_count` 是程序读取后的 Python 字符串长度，包含换行等字符；不等于词数或模型 Token 数。该程序按普通文本读取 Markdown，不渲染页面，也不完整解析 Markdown 语法。

## 换一篇真实笔记，并保存 JSON

从根目录运行：

```powershell
python '.\30-项目实践\01-Markdown读取小程序\read_note.py' '.\10-知识卡片\Token.md' --output '.\.local\markdown-reader\Token-01.json'
```

这次指定了输入文件和输出位置。输出文件已存在时，程序会提示换一个新文件名；下一次可以改为 `Token-02.json`。

打开 JSON 检查四个字段：

| 字段 | 内容 |
| --- | --- |
| `file_name` | 原文件名 |
| `title` | 第一个以 `# ` 开头的非空标题；没有时使用文件名去掉扩展名 |
| `content` | 读取到的 Markdown 原文，保留正文中的标记 |
| `character_count` | 读取后字符串的长度 |

标题提取是简化的文本规则；代码块里的 `# ` 也可能被识别为标题。需要准确解析复杂笔记时，再学习 Markdown 解析工具。

## 再把 JSON 读回来

在根目录运行：

```powershell
python -c "import json; from pathlib import Path; note = json.loads(Path('.local/markdown-reader/Token-01.json').read_text(encoding='utf-8')); print(note['title']); print(note['file_name'])"
```

预期显示 `Token` 和 `Token.md`。`.local/` 已被 Git 忽略，实验输出留在本机；脚本、示例和说明会同步到仓库。

## 对照代码理解流程

| 代码位置 | 做什么 | 对应知识 |
| --- | --- | --- |
| `argparse` | 接收输入文件与 `--output` | 运行命令、参数 |
| `read_note` | 读取文件并组成字典 | 路径、字符串、循环、字典、函数 |
| `save_json` | 将字典写成 UTF-8 JSON | 文件模式、JSON |
| `try / except` | 对读取、格式和保存错误给出提示 | 错误与异常 |
| `main` | 把步骤串起来 | 输入、处理和输出 |

输入文本按 UTF-8 读取，也兼容带 UTF-8 BOM 的文件。写入采用新建模式，遇到已有输出会报错；每次实验使用新的输出名称即可。

## 我需要亲自完成的验收

- [ ] 运行默认示例，检查显示的正文。
- [ ] 换成 Token 知识卡片，保存一个新 JSON，再读回标题与文件名。
- [ ] 解释脚本输入、处理、输出各是什么。
- [ ] 故意传一个不存在的文件，观察失败提示；不要把失败记为完成。
- [ ] 再次使用相同输出名，检查原输出没有被覆盖。
- [ ] 用自己的话记录一次成功、一次失败和处理方法。

代码提供者的运行检查，不代替上面的个人学习验收。验证环境与结果见 [运行检查记录](运行检查记录.md)。

## 我的实践记录

- 我使用的 Python 版本：待填写。
- 我输入的文件与命令：待填写。
- 我观察到的结果：待填写。
- 我还没理解的代码：待填写。

## 参考来源

- [Python 3.13：pathlib](https://docs.python.org/zh-cn/3.13/library/pathlib.html)。
- [Python 3.13：输入与输出](https://docs.python.org/zh-cn/3.13/tutorial/inputoutput.html)。
- 来源核查日期：2026-10-23。
