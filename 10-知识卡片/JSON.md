---
created: 2026-10-23
updated: 2026-10-23
status: 待读
source: "https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON"
aliases:
  - JavaScript Object Notation
tags:
  - 知识卡片
  - 编程基础
---

# JSON

[知识卡片目录](README.md) · [学习地图](../学习地图.md)

## 一句话解释

**JSON 是一种用文本表达有结构数据的格式，便于不同程序保存和交换信息。**它不是只能在 JavaScript 中使用，很多语言都能读取和生成它。[定义依据：MDN JSON 入门](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON)

## 用生活里的事理解

像填写信息表：每一栏有名称，每一栏填入对应内容。相比一大段自由文字，程序更容易按固定字段取出需要的信息。

## 一个具体例子

下面是一份自拟的学习笔记信息。`reviewed` 表示是否已复习，`priority` 是示意的优先级。

```json
{
  "title": "我的第一篇学习笔记",
  "tags": ["AI", "入门"],
  "reviewed": false,
  "priority": 1,
  "source": null
}
```

| 写法 | 这里表示什么 |
| --- | --- |
| `{}` | 一个对象，里面放名称与对应的值 |
| `"title": "我的第一篇学习笔记"` | 一个字段及其字符串值 |
| `["AI", "入门"]` | 一个数组，用来放多个值 |
| `false` | 布尔值，表示“否” |
| `1` | 数字 |
| `null` | 空值，本例表示尚未提供来源 |

对象、数组、字符串、数字、布尔值和空值是 JSON 的基本组成。[规则依据：RFC 8259](https://www.rfc-editor.org/rfc/rfc8259)

## 先记住这些规则

- 对象字段名和字符串使用英文双引号。
- 多个成员之间用逗号分隔，最后一个成员后面不加逗号。
- 布尔值写作 `true`、`false`，空值写作 `null`，都是小写。
- 标准 JSON 不写注释。[语法依据：MDN](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON)

## 放到 MindVault 中有什么用

阶段 1 可以练习把读取到的笔记信息保存成 JSON，再读取回来。以后调用 [API](API.md)，也经常会接触 JSON 形式的输入和返回结果。

模型生成的 JSON 草稿还需要检查两件事：格式能否被解析，内容是否真实、符合任务要求。两者分别检查。

## 容易误解的地方

- JSON 是数据格式，JSON 文件本身不会执行读取文章或调用模型的任务。
- Markdown 适合写知识正文，JSON 适合表达字段化数据；按用途选择。
- 看起来像 JSON，不一定语法正确，实际读入程序后才能确认格式是否被接受。

## 我的理解与验证

- [ ] 指出上面示例中的标题、标签和复习状态。
- [ ] 修改标题，在标签数组中加一个标签，再检查逗号和引号。
- [ ] 到文件处理练习时，把这份信息保存为 JSON 文件，读取后取出标题。

## 自测与参考答案

**问题：**为什么 `"reviewed": false` 中，字段名有双引号，而 `false` 没有？

**参考要点：**字段名是字符串；这里的 `false` 是布尔值。写成 `"false"` 就变成了一个字符串，数据类型已经不同。

## 来源

- [MDN：Working with JSON](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Scripting/JSON)，用于用途与入门语法。
- [RFC 8259：JSON Data Interchange Format](https://www.rfc-editor.org/rfc/rfc8259)，用于数据类型和标准语法。
- 来源核查日期：2026-10-23。信息表类比和笔记示例为自拟，个人练习仍待完成。

## 相关笔记

[API](API.md) · [提示词](提示词.md) · [幻觉](幻觉.md)

## 仍有疑问

- [ ] 怎样在 Python 中读写 JSON，并取出某个字段？留到文件处理小程序实践。
