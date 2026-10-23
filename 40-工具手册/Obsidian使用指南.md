# Obsidian 使用指南

[返回首页](../README.md)

## 第一次打开

1. 打开 Obsidian，进入“管理仓库 / Manage vaults”。已经打开其他仓库时，可以从左下角的仓库切换入口进入。
2. 选择“打开文件夹作为仓库 / Open folder as vault”。
3. 选择 `E:\my-projects\MindVault`，点击打开。
4. 在左侧文件列表中打开根目录的 `README.md`，它就是首页。

这里已经是完整的知识库文件夹，直接打开这一层即可。

## 按导航继续学习

1. 按 `Ctrl+O`，输入“学习总导航”，打开 [AI 学习总导航](../学习总导航.md)。首页也有同一入口。
2. 按阶段表进入当前阶段，依次打开知识卡片和配套实践；阅读模式下点击链接即可打开对应笔记。
3. 在终端执行实践文档中的 Python 命令，把自己的理解、运行结果和下一步写成笔记。
4. 到[学习地图](../学习地图.md)勾选自己实际完成的任务。资料已准备的勾选用于记录资料建设情况。
5. 学习结束后对我说“帮我提交 MindVault”，由我检查改动并提交、推送。Obsidian 保存文件后仍需这一步才能同步到 GitHub。

## 模板设置

1. 打开“设置 → 核心插件”，启用“模板 / Templates”。
2. 打开“设置 → 模板”，确认“模板文件夹位置”为 `80-模板`。该位置已写入随库设置。
3. 在目标文件夹中新建一篇笔记，并先给笔记命名。
4. 把光标放到正文，按 `Ctrl+P`，搜索“插入模板 / Templates: Insert template”，选择需要的模板。

模板中的标题和日期会在插入时替换。新笔记不要直接写在模板文件本身；编辑模板会影响以后插入的内容。

## 每天如何记录

1. 开始前先按 [GitHub 同步指南](GitHub同步指南.md) 检查远端更新。
2. 来不及整理的内容先放到 `00-收集箱`。
3. 概念放到 `10-知识卡片`，阅读记录放到 `20-课程笔记`，动手结果放到 `30-项目实践`。
4. 写清来源、自己的理解和疑问。
5. 学习结束后提交并推送到 GitHub。

Obsidian 会自动保存本地文件；GitHub 上传是单独一步。

## 链接、图片和搜索

- 建立关联：输入两个左方括号，搜索并选择已有笔记。当前设置会使用通用 Markdown 链接，便于在 GitHub 阅读。
- 插入截图：直接粘贴或拖入笔记，新附件默认放到 `90-附件`。
- 快速打开笔记：`Ctrl+O`。
- 搜索整个知识库：`Ctrl+Shift+F`。
- 命令面板：`Ctrl+P`。

已配置：使用 Markdown 链接、自动更新内部链接、附件集中存放、删除文件时移入 Obsidian 的本地回收目录。

## 参考

- [Obsidian：管理仓库](https://obsidian.md/help/Files%2Band%2Bfolders/Manage%2Bvaults)
- [Obsidian：模板](https://obsidian.md/help/Plugins/Templates)
- [Obsidian：数据保存方式](https://obsidian.md/help/Files%2Band%2Bfolders/How%2BObsidian%2Bstores%2Bdata)
