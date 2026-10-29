---
created: 2026-10-23
status: "待学习"
source: "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON"
aliases:
  - JavaScript Object Notation
tags:
  - 知识卡片
  - 编程基础
type: "知识卡片"
stage: "01 基础与Python"
updated: 2026-10-29
---

# JSON

[卡片目录](README.md) · [课程入口](../20-课程笔记/第一阶段-线上课程与阅读顺序.md)

## 一句话解释

**JSON 是用文本表达字段化数据的格式，方便程序保存和交换信息。**像有栏目名的信息表；它是数据，不会自己执行读文件或调用模型的动作。

## 为什么需要它

Markdown 适合人读正文，JSON 适合程序按字段取值。第一阶段保存笔记信息，第二阶段组织 API 请求和解析模型输出，都会用到它。

先理解结构、类型与转换，能避免“看着像 JSON”却读不进去，或语法合法但字段含义错误。

## 用 MindVault 走一遍

下面是自写的笔记信息，键和值用冒号对应，成员用逗号分隔：

```json
{
  "title": "Token",
  "tags": ["AI", "入门"],
  "reviewed": false,
  "priority": 1,
  "source": null
}
```

| JSON 写法 | 表示 | 对应 Python 常见值 |
| --- | --- | --- |
| 对象 `{}` | 字段到值 | dict |
| 数组 `[]` | 一组有序值 | list |
| 字符串 | 文本 | str |
| 数字 | 数值 | int 或 float |
| true/false | 布尔值 | True/False |
| null | 空值 | None |

字段名和字符串用英文双引号；末尾成员不留多余逗号；标准 JSON 不写注释。`"false"` 是字符串，false 才是布尔值。

Python 中的字典不是 JSON 文本。可用 `json.dumps(note, ensure_ascii=False)` 变成文本，用 `json.loads(text)` 读回数据。ensure_ascii=False 让中文更易读，不改变字段真假。

项目 01 保存 file_name、title、content、character_count 四个实际字段；上面的 tags 等只是学习示例，别误以为读取器已经解析了 Obsidian 属性。

第二阶段还会遇到两层 JSON：外层是服务响应，message.content 可能是装着另一份 JSON 的字符串，需再解析一次。不要用 eval 执行模型返回文本。

## 每一步的输入输出

| 步骤 | 输入 | 输出 |
| --- | --- | --- |
| 组织数据 | Python 字典和列表 | 内存对象 |
| 序列化 | json.dumps 或 json.dump | JSON 字符串或文件 |
| 读取解析 | json.loads 或 json.load | Python 数据 |
| 校验字段 | 类型、数量、必填规则 | 可接受结构 |
| 核对含义 | 结构与实际材料 | 内容判断 |

dump/load 面向文件对象，dumps/loads 处理字符串；名字里的 s 可先帮助记成字符串版本。

## 常见疑问

**合法 JSON 一定是对象吗？**标准可有其他顶层类型；本项目请求与摘要约定对象，程序会另检查。

**字段正确就代表事实正确吗？**不会，仍需核对原文。

**JSON 文件能自动同步吗？**文件格式不提供同步能力，保存、Git 提交与推送是独立操作。

**模型加代码围栏还能直接 loads 吗？**整个字符串含 Markdown 围栏就不是纯 JSON。当前要求只输出对象，遇到非法内容拒绝，而不是悄悄执行。

**null 是 0 或空字符串吗？**不同，按数据语义区分“没有值”和数值零、空文本。

## 小练习与自测

**题目：**把 false 写成 `"false"` 后结构还可能解析吗？

**参考答案：**能解析，但类型变为字符串，可能违反程序要求。

**练习：**修改标题、加一个标签，再读回数据；故意加尾逗号观察解析错误，只在实验副本修改。

### 动手记录

- [ ] 指出上面示例中的标题、标签和复习状态。
- [ ] 修改标题，在标签数组中加一个标签，再检查逗号和引号。
- [ ] 到文件处理练习时，把这份信息保存为 JSON 文件，读取后取出标题。
- [ ] 怎样在 Python 中读写 JSON，并取出某个字段？留到文件处理小程序实践。

## 本库实现与实践入口

项目 01 的 `save_json()` 用新建模式保存，不覆盖旧文件。项目 02 用 `validate_summary()` 在解析后继续检查字段和引文。

[项目 01：读取 Markdown](../30-项目实践/01-Markdown读取小程序/README.md) · [读取器代码](../30-项目实践/01-Markdown读取小程序/read_note.py) · [第一阶段阅读顺序](../20-课程笔记/第一阶段-线上课程与阅读顺序.md)

[项目 02：文章整理](../30-项目实践/02-模型API与文章整理/README.md) · [配套示例文章](../30-项目实践/02-模型API与文章整理/examples/示例文章.md)

代码块标为 python 时，在 Python 中运行；标为 powershell 的命令在终端运行。Obsidian 用于阅读，不会自动执行代码。

## 来源与延伸阅读

[Python JSON 文档](https://docs.python.org/zh-cn/3.13/library/json.html)：转换和读写。[RFC 8259](https://www.rfc-editor.org/rfc/rfc8259)：标准语法。笔记信息与字段说明为本库自写。

核查日期：2026-10-29。外部资料用于核对规则，核心解释和练习答案已写在本页。生活类比、表格和教学数据为本库整理；固定模拟和数字演算不等于真实模型实测。

## 相关笔记与下一步

[下一张：变量与数据类型](变量与数据类型.md) · [学习总导航](../学习总导航.md) · [本阶段阅读顺序](../20-课程笔记/第一阶段-线上课程与阅读顺序.md)
