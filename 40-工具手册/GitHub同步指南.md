# GitHub 同步指南

[返回首页](../README.md)

远端仓库：[Bindy-lbb/MindVault](https://github.com/Bindy-lbb/MindVault)（私有，登录有权限的 GitHub 账户后查看）。

本地文件夹：`E:\my-projects\MindVault`。

## 推荐：用 GitHub Desktop 操作

GitHub Desktop 是可选的图形工具，可从 [官网](https://desktop.github.com/) 下载。安装后登录有仓库权限的 GitHub 账户。

### 第一次添加已有仓库

1. 选择 `File → Add local repository`。
2. 选择 `E:\my-projects\MindVault`。
3. 点击 `Add repository`。

这个文件夹已经有 Git 历史和远端地址，添加到 Desktop 后即可继续使用，无需再发布一个同名仓库。

### 每次学习前

1. 选择 MindVault 仓库。
2. 点击 `Fetch origin` 检查更新。
3. 如果出现 `Pull origin`，点击它，将远端更新取到本地。

### 每次学习后

1. 查看 `Changes`，确认这次要上传哪些文件。
2. 在 `Summary` 写一句说明，例如“补充 RAG 学习笔记”。
3. 点击 `Commit to main`，把修改记录到本地版本历史。
4. 点击 `Push origin`，把提交上传 GitHub。

只有 Commit 还没有上传，Push 后才会出现在 GitHub。首次同步已完成，后续新笔记仍需要重复这些步骤。

## 另一台电脑

1. 在另一台电脑安装 Obsidian 和 GitHub Desktop，并登录 GitHub。
2. 在 Desktop 中选择 `File → Clone repository`，选择 MindVault，保存到本地。
3. 在 Obsidian 中把克隆后的文件夹作为仓库打开。
4. 按上一节启用模板，并确认模板目录为 `80-模板`。
5. 每次换电脑前先推送，另一台电脑编辑前先拉取。

如果两台电脑都改了同一段内容，可能发生冲突。先保留双方内容，再选择正确版本；不确定时停在冲突页面处理，避免覆盖笔记。

## 已熟悉终端时

在 MindVault 文件夹中运行：

```powershell
# 学习前，先确认本地是否有未提交修改
git status
# 本地没有未提交修改时再拉取
git pull --ff-only
```

学习后：

```powershell
git status
# 检查文件列表后再暂存、提交
git add .
git commit -m "更新 AI 学习笔记"
git push
```

`git pull --ff-only` 如果失败，先查看提示并处理分歧，不要强制覆盖。

## 哪些设置会同步

- 笔记、已加入仓库的附件，以及基础的链接、附件、模板位置设置会同步。
- 工作区布局、回收目录、社区插件文件、插件凭据和本地 AI 索引不会上传。
- 模板核心插件的启用状态由每台设备设置一次。
- `.env` 等常见本地环境配置已加入忽略列表，但忽略规则不会检查你写进笔记正文的内容。

## 参考

- [GitHub Desktop：添加本地仓库](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-a-repository-from-your-local-computer-to-github-desktop)
- [GitHub Desktop：推送修改](https://docs.github.com/en/desktop/making-changes-in-a-branch/pushing-changes-to-github-from-github-desktop)
