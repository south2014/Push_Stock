# Git 配置命令快速参考
# 日期: 2026/03/08
# 用户: south2014

================================================
阶段 1: 安装 Git (必须手动操作)
================================================

1. 下载: https://git-scm.com/download/win
2. 选择: Windows 64-bit
3. 安装选项:
   ✓ Use VS Code as Git's default editor
   ✓ 其他全部默认 (Next)
4. 安装后: 重启终端或重启电脑
5. 验证: git --version

================================================
阶段 2: 配置 Git 和创建仓库
================================================

进入项目目录:
   cd F:\OpenCode\Push_Stock

配置用户信息:
   git config --global user.name "south2014"
   git config --global user.email "xbnan@outlook.com"
   git config --global init.defaultBranch main

初始化 Git 仓库:
   git init

添加所有文件并提交:
   git add .
   git commit -m "Initial commit: project setup"

查看状态:
   git status
   git log

================================================
阶段 3: 生成 SSH 密钥
================================================

生成新 SSH 密钥 (在 Git Bash 中运行):
   ssh-keygen -t ed25519 -C "xbnan@outlook.com"
   
按下 Enter 接受默认位置
再次按 Enter 设置空密码（或输入密码）

查看公钥 (复制所有内容):
   type %USERPROFILE%\.ssh\id_ed25519.pub

================================================
阶段 4: 添加到 GitHub
================================================

在 GitHub 添加 SSH 密钥:
1. 登录 https://github.com
2. Settings → SSH and GPG keys → New SSH key
3. Title: My Laptop
4. Key: 粘贴刚才复制的公钥
5. 点击 Add SSH key

验证 SSH 连接:
   ssh -T git@github.com
   （应该看到: Hi south2014! You've successfully authenticated...）

在 GitHub 创建仓库:
1. 访问 https://github.com/new
2. Repository name: Push_Stock
3. 不要勾选 "Initialize with README"
4. 点击 Create repository

连接到 GitHub:
   git remote add origin git@github.com:south2014/Push_Stock.git
   git push -u origin main

================================================
阶段 5: 验证
================================================

验证推送成功:
   git remote -v
   git push

至少应该看到:
   origin  git@github.com:south2014/Push_Stock.git (fetch)
   origin  git@github.com:south2014/Push_Stock.git (push)

在浏览器中访问:
   https://github.com/south2014/Push_Stock
   应该能看到所有文件

测试 Clone:
   cd F:\OpenCode\tmp
   git clone git@github.com:south2014/Push_Stock.git test
   cd test
   dir
   （应该看到所有文件）

================================================
常用 Git 命令
================================================

查看状态:
   git status

查看修改:
   git diff

添加文件:
   git add 文件名
   git add .

提交:
   git commit -m "描述"

推送到 GitHub:
   git push origin main

拉取最新代码:
   git pull origin main

查看提交历史:
   git log
   git log --oneline

撤销修改:
   git checkout -- 文件名

查看分支:
   git branch

================================================
问题排查
================================================

如果 git push 需要密码:
   → SSH 密钥没配置正确，重新配置

如果 ssh -T git@github.com 失败:
   → 检查密钥是否正确添加到 GitHub

如果需要代理:
   git config --global http.proxy http://127.0.0.1:1080
   git config --global https.proxy https://127.0.0.1:1080
