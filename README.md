# 港股籌碼推薦系統（每日自動更新版）

每天港股收市後自動更新評分、入場、止損、目標價與原因。  
你只要打開網頁 Refresh，就係最新資料。

---

## 一次設定（只需做一次）

### 1. 開 GitHub 帳號
去 https://github.com 註冊（免費）

### 2. 新建 Repository
1. 點右上角 **+** → **New repository**
2. Repository name 填：`hk-stock-chips`（或其他名字）
3. 選 **Public**
4. **不要**勾選 Add a README
5. 點 **Create repository**

### 3. 上傳所有檔案
方法 A（網頁上傳，最簡單）：
1. 進入你剛建立的 repo
2. 點 **uploading an existing file**
3. 把本資料夾**所有檔案和資料夾**（包括 `.github` 資料夾）拖進去
4. 點 **Commit changes**

方法 B（用 Git）：
```bash
git clone https://github.com/你的帳號/hk-stock-chips.git
# 把本資料夾內容複製進去
git add .
git commit -m "init"
git push
```

### 4. 開啟 GitHub Pages
1. 進入 repo → **Settings** → 左側 **Pages**
2. Source 選 **Deploy from a branch**
3. Branch 選 **main**，資料夾選 **/ (root)**
4. 點 **Save**
5. 等 1–2 分鐘，會出現網址：
   `https://你的帳號.github.io/hk-stock-chips/`

### 5. 允許 Actions 寫入（重要）
1. Settings → **Actions** → **General**
2. 拉到 **Workflow permissions**
3. 選 **Read and write permissions**
4. 勾選 **Allow GitHub Actions to create and approve pull requests**
5. Save

### 6. 測試手動更新一次
1. 進入 repo → 上方 **Actions** 分頁
2. 左邊選 **Daily HK Stock Chips Update**
3. 右邊點 **Run workflow** → **Run workflow**
4. 等它跑完（約 2–5 分鐘）
5. 重新整理你的 Pages 網址，就會看到最新資料

---

## 之後每天怎麼用

- 直接打開你的 Pages 網址
- 按 Refresh 就是最新結果
- 系統會在每個工作日 **17:30 左右（香港時間）** 自動更新
- 完全不用你做任何事

---

## 檔案說明

| 檔案/資料夾 | 用途 |
|-------------|------|
| `index.html` | 主頁面 |
| `style.css` | 樣式 |
| `app.js` | 前端邏輯 |
| `data.js` | 每日更新的資料（Actions 會改這個檔） |
| `scripts/update.py` | 抓數據 + 計算評分/進出場的腳本 |
| `.github/workflows/daily_update.yml` | 每日自動執行的設定 |

---

## 注意

- 僅供研究參考，不構成投資建議
- 資料來源為公開價量，港股沒有台股式三大法人日報
- 如某天 Actions 失敗（Yahoo 限流），可手動再 Run workflow 一次
- 想加股票：改 `scripts/update.py` 裡的 `NAME_MAP` 後 push 即可

有問題可以再問我。
