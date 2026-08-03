import streamlit as st
import pandas as pd
from pypdf import PdfReader
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="FinBrief · 財略摘要器", layout="wide")
st.title("📊 FinBrief · 財略摘要器")

# --- 側邊欄：API Key 設定與模型選擇 ---
with st.sidebar:
    st.header("⚙️ 模型與 API 設定")
    
    # 選擇服務商（預設以 OpenAI / DeepSeek 等在港可運行的 API 為主）
    provider = st.selectbox(
        "選擇 AI 服務商 (Provider)",
        ["OpenAI (GPT-4o / GPT-4o-mini)", "DeepSeek / 自訂 Compatible API"]
    )
    
    # 讀取環境變數或允許使用者手動輸入 Key
    env_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    user_api_key = st.text_input(
        "🔑 輸入你的 API Key", 
        value=env_key,
        type="password",
        help="你的 API Key 只會存放在當前 Session 記憶體中，用於呼叫模型，絕不會被紀錄或儲存於伺服器。"
    )
    
    if provider == "OpenAI (GPT-4o / GPT-4o-mini)":
        selected_model = st.selectbox("選擇模型", ["gpt-4o-mini", "gpt-4o"])
        base_url = None
    else:
        selected_model = st.text_input("輸入模型名稱", value="deepseek-chat")
        base_url = st.text_input("Base URL", value="https://api.deepseek.com")

    st.markdown("---")
    st.markdown("### 🔒 數據隱私與安全聲明")
    st.caption(
        """
        1. **金鑰安全**：你輸入的 API Key 僅用於當次連線，系統絕不留存、不轉售、不出售。
        2. **數據隱私**：上傳之財務報表數據將直接透過加密連線 (TLS) 傳送至你選擇的 AI 服務商進行分析，本平台伺服器不會保存你的任何檔案。
        3. **免責聲明**：本系統生成之分析僅供商業決策與研究參考，不構成任何投資或會計審計建議。
        """
    )

# --- 主畫面：上傳與分析 ---
uploaded_file = st.file_uploader(
    "上傳財務數據或報表 (PDF / Excel / CSV)", 
    type=['pdf', 'xlsx', 'csv']
)

template = st.text_area(
    "貼上你的標準分析模板或指令", 
    height=150,
    placeholder="例如：請針對這份年報分析：1. 核心營收與毛利趨勢 2. 現金流健康度 3. 三大潛在風險與建議。"
)

# 輔助函數：解析 PDF
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

if st.button("生成報告"):
    if not user_api_key:
        st.error("⚠️ 請先於左側邊欄輸入你的 API Key！")
    elif not uploaded_file:
        st.warning("⚠️ 請上傳財務檔案！")
    elif not template.strip():
        st.warning("⚠️ 請輸入分析模板！")
    else:
        file_type = uploaded_file.name.split('.')[-1].lower()
        extracted_content = ""

        # 讀取檔案數據
        with st.spinner("正在讀取檔案內容..."):
            if file_type == 'pdf':
                extracted_content = extract_text_from_pdf(uploaded_file)
            elif file_type in ['xlsx', 'csv']:
                df = pd.read_excel(uploaded_file) if file_type == 'xlsx' else pd.read_csv(uploaded_file)
                extracted_content = df.to_string()

        # 呼叫 LLM 分析
        with st.spinner("🤖 AI 財務專家正在分析報表並生成摘要..."):
            try:
                # 初始化 OpenAI Client (若為 DeepSeek 則帶入自訂 base_url)
                client = OpenAI(
                    api_key=user_api_key,
                    base_url=base_url if base_url else None
                )

                system_prompt = "你是一位資深的企業 C-Level 財務顧問與投資分析師，擅長解讀上市公司的財務報表與資本策略。"
                user_prompt = f"""
                請根據以下提供的財務報表內容，嚴格按照【分析模板與要求】輸出專業分析報告。

                【分析模板與要求】：
                {template}

                【財務報表內容】：
                {extracted_content[:100000]}
                """

                response = client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2 # 財務分析保持低隨機性，確保精確
                )

                report_text = response.choices[0].message.content

                # 展示結果
                st.markdown("---")
                st.markdown("## 📈 FinBrief 財略分析報告")
                st.markdown(report_text)
                
                # 下載報告按鈕
                st.download_button(
                    label="📥 下載報告 (Markdown 格式)",
                    data=report_text,
                    file_name="FinBrief_Report.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"❌ AI 生成失敗，請檢查 API Key 是否正確或網路連線：{str(e)}")
