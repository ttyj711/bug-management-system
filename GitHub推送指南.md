# GitHub推送指南

本指南将帮助您将BUG管理系统项目推送到GitHub仓库。

## 准备工作

### 1. 在GitHub上创建仓库

1. 登录您的GitHub账号
2. 点击右上角的 `+` 号，选择 `New repository`
3. 填写仓库信息：
   - **Repository name**: 输入仓库名称，例如 `bug-management-system`
   - **Description**: 可选，输入项目描述
   - **Visibility**: 选择 `Public` 或 `Private`
   - 不要勾选 `Add a README file`（因为本地已有）
   - 不要勾选 `Add .gitignore`（后续手动创建）
   - 不要勾选 `Choose a license`（后续手动添加）
4. 点击 `Create repository`
5. 复制仓库的URL（HTTPS或SSH），例如：
   - HTTPS: `https://github.com/your-username/bug-management-system.git`
   - SSH: `git@github.com:your-username/bug-management-system.git`

### 2. 创建.gitignore文件

在项目根目录创建 `.gitignore` 文件，添加不需要提交到GitHub的文件和目录：

```gitignore
# Python/后端
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Django
.env
.env.local
.env.*.local
*.log
db.sqlite3
media/
staticfiles/

# Node.js/前端
node_modules/
dist/
dist-ssr/
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# 其他
.cache/
*.log
```

## 推送步骤

### 1. 初始化Git仓库（如果尚未初始化）

在项目根目录打开终端，执行：

```bash
git init
```

### 2. 配置用户信息

首次使用Git时，需要配置用户名和邮箱：

```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### 3. 添加文件到暂存区

```bash
git add .
```

### 4. 提交更改

```bash
git commit -m "Initial commit"
```

### 5. 关联远程仓库

使用之前复制的GitHub仓库URL：

```bash
git remote add origin https://github.com/your-username/bug-management-system.git
```

### 6. 推送代码到GitHub

#### 如果是第一次推送

```bash
git push -u origin master
```

**注意**：如果GitHub默认分支是 `main`，请使用：

```bash
git push -u origin main
```

#### 后续推送

```bash
git push
```

## 常见问题与解决方案

### 1. 推送失败 - 权限问题

**HTTPS方式**：输入GitHub用户名和密码时，密码需要使用个人访问令牌（PAT），而不是登录密码。

**生成PAT**：
- 登录GitHub，进入 `Settings` > `Developer settings` > `Personal access tokens` > `Tokens (classic)`
- 点击 `Generate new token`
- 选择 `repo` 权限
- 生成后复制令牌，保存好
- 推送时使用此令牌作为密码

**SSH方式**：需要配置SSH密钥

### 2. 分支名称不匹配

如果GitHub默认分支是 `main`，而本地是 `master`：

```bash
git branch -M main
```

然后推送：

```bash
git push -u origin main
```

### 3. 推送失败 - 非快进更新

如果远程仓库有本地没有的更改，需要先拉取：

```bash
git pull origin master --rebase
```

解决冲突后再推送。

## 验证推送

推送成功后，返回GitHub仓库页面，刷新页面，您应该能看到项目文件已经成功推送。

## 后续维护

### 提交新更改

```bash
git add .
git commit -m "描述更改内容"
git push
```

### 查看状态

```bash
git status
```

### 查看提交历史

```bash
git log
```

## 总结

通过以上步骤，您已经成功将BUG管理系统项目推送到GitHub仓库。现在您可以在GitHub上管理项目，邀请团队成员协作，或者作为开源项目分享给社区。

---

**注意**：
- 定期备份重要数据
- 不要将敏感信息（如数据库密码、密钥）提交到GitHub
- 遵循Git最佳实践，使用有意义的提交信息
