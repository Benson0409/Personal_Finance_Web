# 個人理財網站 (Personal Finance Web Application)

## 專案概覽

這是一個基於 Flask 框架和 HTML 開發的個人理財網站應用程式，旨在幫助使用者輕鬆管理他們的現金和股票資產。透過自動化的 API 整合和直觀的視覺化圖表，使用者可以一目瞭然地掌握自己的財務狀況。

## 主要功能

* **現金管理**：使用者可以自行輸入台幣和美金金額。網站會自動抓取最新的匯率 API 進行外幣換算，並計算現金總額。
* **股票管理**：使用者可以輸入持有的股票代號、股數、成交單價、手續費和交易稅。網站會自動查詢股票的即時價值，並計算持有市值、平均成本及報酬率。
* **數據儲存**：所有使用者輸入的現金與股票交易記錄都會被安全地儲存在本地 SQLite 資料庫中，方便追蹤與管理。
* **資產視覺化**：
    * **現金更動紀錄**：清晰列出現金的每筆收入與支出。
    * **股票庫存總覽**：詳細展示持有的股票資訊，包括目前股價、市值、成本與報酬率。
    * **資產比例圖**：透過圓餅圖直觀地呈現現金與股票資產的比例分佈。
    * **股票庫存占比圖**：以圓餅圖顯示各股票在整個股票投資組合中的市值佔比。
* **資料刪除功能**：使用者可以輕鬆刪除歷史的現金更動紀錄。

## 使用的技術

* **後端框架**：Python Flask
* **資料庫**：SQLite (透過 `sqlite3` 模組)
* **前端**：HTML5, Bootstrap 5 (用於響應式設計和美觀的 UI 組件)
* **資料視覺化**：Matplotlib (Python 繪圖庫，用於生成圓餅圖)
* **外部 API 整合**：
    * 全球即時匯率 API (tw.rter.info)
    * 台灣證券交易所 (TWSE) 股票日線查詢 API

## 專案結構
Personal_fiance_web/
├── .idea/                 # IDE (PyCharm 等) 配置文件
├── static/                # 靜態檔案，包含生成的圖表 (piechart.jpg, piechart2.jpg)
│   ├── piechart.jpg       # 股票庫存占比圖
│   └── piechart2.jpg      # 資產比例圖 (現金、股票)
├── templates/             # HTML 模板檔案
│   ├── base.html          # 基礎佈局，包含導覽列和 Bootstrap 引用
│   ├── cash.html          # 現金輸入表單頁面
│   ├── index.html         # 首頁，顯示總覽、記錄和圖表
│   └── stock.html         # 股票輸入表單頁面
├── datafile.db            # SQLite 資料庫檔案 (存放使用者數據)
├── db_setting.py          # 資料庫初始化腳本 (用於創建表格等)
└── index.py               # 主要 Flask 應用程式邏輯

## 如何運行 (假設您已安裝 Python 和 pip)

1.  **克隆儲存庫**：
    ```bash
    git clone [https://github.com/Benson0409/Personal_fiance_web.git](https://github.com/Benson0409/Personal_fiance_web.git)
    cd Personal_fiance_web
    ```

2.  **建立虛擬環境 (推薦)**：
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **安裝依賴套件**：
    ```bash
    pip install Flask requests matplotlib
    ```

4.  **初始化資料庫**：
    運行 `db_setting.py` 來創建資料庫檔案和必要的表格。
    ```bash
    python db_setting.py
    ```
    (請確保 `db_setting.py` 內容是您用於建立 `cash` 和 `stock` 表格的代碼)

5.  **運行 Flask 應用程式**：
    ```bash
    python index.py
    ```

6.  **開啟瀏覽器**：
    在您的瀏覽器中訪問 `http://127.0.0.1:5000/`。
