# Luna · Outfit & Self-Care (English)

Wardrobe manager, daily plan, focus spaces — all in one app. Data is stored in your browser (localStorage).

## 所有人都能打开的网页链接（公开链接）

当前只是本地文件，**还没有**公网链接。要得到一个谁都能打开的链接，任选其一：

| 方式 | 时间 | 得到的链接 |
|------|------|------------|
| **Netlify Drop** | 约 1 分钟 | `https://xxx.netlify.app`（可自定义子域名） |
| **GitHub Pages** | 约 5 分钟 | `https://<用户名>.github.io/<仓库名>/` |

- **最快：** 打开 [Netlify Drop](https://app.netlify.com/drop) → 把本文件夹（或打成 zip）拖进去 → 会得到一个公开链接，发给任何人都能打开。
- **用 GitHub：** 把本文件夹推到一个 GitHub 仓库 → 仓库里 **Settings → Pages** → 选择分支 `main`、根目录 → 保存后等 1～2 分钟，用 `https://<用户名>.github.io/<仓库名>/` 即可。

部署后就是**成熟的网页链接**，任何人用浏览器打开即可使用（数据存在各自浏览器里）。

---

## Run locally

- **Option A:** Open `index.html` in your browser (double-click or drag into Chrome/Edge/Firefox).
- **Option B:** Serve the folder with a local server (e.g. `npx serve .` or VS Code Live Server) and open the URL.

No build step or backend required.

## How others can see it

To share so **others can open and use it**:

### 1. GitHub Pages (free, good for portfolios)

1. Create a new repo on GitHub (e.g. `luna-app`).
2. Upload this folder’s contents (all files inside the repo root: `index.html`, `styles.css`, `app.js`).
3. In the repo: **Settings → Pages** → Source: **Deploy from a branch** → Branch: `main` (or `master`) → root → Save.
4. After a minute, the site will be at: `https://<your-username>.github.io/luna-app/`

Share that link; anyone can open it and use the app (their data stays in their own browser).

### 2. Netlify Drop

1. Go to [https://app.netlify.com/drop](https://app.netlify.com/drop).
2. Drag and drop this folder (or a zip of it).
3. Netlify gives you a public URL. Share that link.

### 3. Send the folder

Zip the folder and send it. Others can unzip and open `index.html` in a browser. Data will be stored in their browser.

---

## What’s included

- **Dashboard:** Greeting, last sleep, this week’s movement, today’s mood, first thing tomorrow.
- **Closet:** Add items (name, brand, category, season, tags, price, link), filter, delete.
- **Outfits:** Create outfits from closet items, “how do I style one piece?” suggestions.
- **Plan:** Calendar, add events per day, daily reflection, movement log, sleep log.
- **Spaces:** Reset, Study, Sleep, Yoga (full-screen focus scenes).

All copy is in English. Data keys use a separate localStorage prefix (`luna_*_en`) so it does not conflict with a Chinese version.
