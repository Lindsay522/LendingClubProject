# 推到 GitHub / 交作业 — 你需要做的

下面这些需要你在自己电脑上或网页上操作（账号、密码、仓库名只有你有）。

---

## 一、推到 GitHub（可选，用于备份/作品集）

### 1. 在 GitHub 上建仓库

1. 打开 https://github.com/new
2. **Repository name** 填：`LendingClubProject`（或任意英文名）
3. 选 **Public**
4. **不要**勾选 "Add a README"（本地已有）
5. 点 **Create repository**

### 2. 在本地连上仓库并推送

在 **PowerShell** 里进入项目目录，执行（把 `你的用户名` 换成你的 GitHub 用户名）：

```powershell
cd e:\LendingClubProject

git remote add origin https://github.com/你的用户名/LendingClubProject.git
git branch -M main
git push -u origin main
```

- 第一次 `git push` 会提示登录 GitHub（浏览器或 token）。
- 如果 GitHub 让你用 **Personal Access Token** 当密码：去 GitHub → Settings → Developer settings → Personal access tokens 新建一个，用 token 代替密码。

---

## 二、交作业（二选一）

### 方式 A：交 ZIP

1. 在资源管理器里进到 `e:\LendingClubProject`
2. 选中除了 `archive\loan.csv` 以外的所有东西（或直接选整个文件夹）
3. 右键 → **发送到 → 压缩(zipped)文件夹**
4. 把生成的 ZIP 交上去，并在作业里写一句：
   - “数据在 `archive\raw_data` 下，大文件 `loan.csv` 未包含；运行步骤见 README.md”

### 方式 B：交 GitHub 链接

1. 先完成上面「一、推到 GitHub」
2. 打开你的仓库页面，复制地址，例如：`https://github.com/你的用户名/LendingClubProject`
3. 交这个链接，并写一句：
   - “README 里有数据说明和运行步骤，大文件已用 .gitignore 排除”

---

## 三、别人/老师要跑你的项目

让对方：

1. 解压 ZIP 或 `git clone` 你的仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 若没有 `archive\raw_data` 下的 CSV：先运行 `python archive/step1_split.py`（需把 `loan.csv` 放到 `archive` 下）
4. 再按顺序运行：
   - `python data_loader.py`
   - `python feature_engineering.py`
   - `python analysis.py`

详细步骤在 **README.md** 里也有。
