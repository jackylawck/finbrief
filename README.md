## 🇭🇰 中文版

### 痛點
財務團隊每日耗費大量時間從損益表、現金流量表中提煉重點，卻仍需花 70% 時間將數字「翻譯」成管理層可讀的決策建議。

**FinBrief** 讓你上傳 Excel 數據、選定分析模板，AI 自動計算關鍵指標並以自然語言生成簡報。

### 核心功能
- 數據上傳 — 支援 Excel 及 CSV，即時預覽
- 指標計算 — 收入增長率、成本佔比、現金流健康度
- AI 報告生成 — 根據模板以自然語言填充洞察
- 一鍵匯出 — 可複製或下載完整簡報
- 數據安全 — 不上傳伺服器，即時處理

### 快速開始（本地）
\`\`\`bash
git clone https://github.com/你的用戶名/你的倉庫名.git
cd 你的倉庫名
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
\`\`\`

建立金鑰檔案 `.streamlit/secrets.toml`：
\`\`\`
OPENAI_API_KEY = "你的金鑰"
\`\`\`

執行：
\`\`\`bash
streamlit run app.py
\`\`\`

### 部署（免費）
1. Push 到 GitHub 公開倉庫
2. 到 share.streamlit.io 點擊 New app
3. Advanced settings 加入 OPENAI_API_KEY
4. 點擊 Deploy，2-3 分鐘獲得網址

### 技術棧
- 前端：Streamlit
- AI：OpenAI / DeepSeek API
- 數據：Pandas
- 部署：Streamlit Cloud

### 使用流程
1. 上傳季度財務 Excel/CSV
2. 貼上你的分析模板
3. AI 計算指標並生成報告
4. 獲取文字洞察簡報
## 🇬🇧 English (Simplified)

### Problem
Finance teams spend 70% of their time translating numbers into readable briefs.

**FinBrief** automates this: upload data, choose a template, get AI-generated insights.

### Key Features
- Upload Excel/CSV with preview
- Auto-calculate revenue growth, cost ratio, cash flow health
- AI fills your template with natural language
- One-click export

### Quick Start
\`\`\`bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
pip install -r requirements.txt
streamlit run app.py
\`\`\`

### Deploy
Push to GitHub → share.streamlit.io → New app → Add API key → Deploy

### Tech Stack
Streamlit + OpenAI/DeepSeek + Pandas

---

## 📄 License
MIT License © 2026 

