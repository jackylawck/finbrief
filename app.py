import streamlit as st
import pandas as pd
from pypdf import PdfReader
from openai import OpenAI
import requests

# --- 1. UI 國際化語言包與預設模板 (i18n & Presets) ---
TRANSLATIONS = {
    "zh": {
        "page_title": "FinBrief · 財略摘要器",
        "title": "📊 FinBrief · 財略摘要器",
        "sidebar_settings": "⚙️ AI 模型與模式設定",
        "mode_select": "🌐 選擇運作模式",
        "mode_free": "🆓 免 Key 模式 (開源 LLM 驅動)",
        "mode_byok": "🔑 BYOK 模式 (自備 API Key)",
        "provider_select": "選擇 AI 服務商 (Provider)",
        "model_select": "選擇 / 輸入模型",
        "api_key_input": "請輸入你的 API Key",
        "security_title": "🔒 數據隱私與技術說明",
        "tech_note_free": "💡 **免 Key 技術說明**：採用公開免 Key LLM 服務，無需申請或輸入任何金鑰即可一鍵分析。適合快速體驗與公開財報摘要。",
        "tech_note_byok": "💡 **BYOK 技術說明**：支援 GPT-4o / DeepSeek / Groq 等商業模型。金鑰僅存於當前 Session 記憶體，關閉分頁即銷毀。",
        "privacy_policy": """
        * **數據隱私**：上傳之財務報表數據僅用於當次 AI 摘要計算，伺服器不保存任何原始檔案。
        * **免責聲明**：本系統生成之分析僅供商業決策參考，不構成任何投資或會計審計建議。
        """,
        "upload_label": "上傳財務數據或報表 (PDF / Excel / CSV)",
        "preset_label": "💡 一鍵選擇標準分析模板：",
        "template_label": "分析模板與指令 (可自由微調)：",
        "presets": {
            "C-Level 核心財略摘要 (推薦)": "請作為 C-Level 財務顧問分析：\n1. 核心營收與毛利趨勢\n2. 現金流健康度與資本支出 (CAPEX)\n3. 三大潛在風險與戰略建議",
            "HKFRS 會計合規與資產負債審查": "請根據香港會計準則 (HKFRS) 視角拆解：\n1. 資產負債表健全度 (流動比率與債務結構)\n2. 損益表營運效率 (毛利率與純利率變化)\n3. 現金流量表經營品質分析",
            "併購與投資盡職調查 (M&A Due Diligence)": "請作為投資分析師進行簡要盡職調查：\n1. 企業核心盈利模式與護城河\n2. 潛在財務黑洞或隱性負債風險\n3. 未來 3 年成長性與估值觀察點"
        },
        "btn_generate": "🚀 生成財略報告",
        "err_no_key": "⚠️ 請輸入有效的 API Key 以啟動 BYOK 模式！",
        "err_no_file": "⚠️ 請先上傳財務檔案！",
        "err_no_template": "⚠️ 請選擇或輸入分析模板！",
        "report_header": "📈 FinBrief 財略分析報告",
        "btn_download": "📥 下載報告 (Markdown 格式)",
        "system_prompt": "你是一位精通香港會計準則 (HKFRS) 與國際財務報告準則 (IFRS) 的資深 C-Level 財務顧問與投資分析師。請用專業繁體中文輸出高品質財略報告。"
    },
    "en": {
        "page_title": "FinBrief · Financial Digest",
        "title": "📊 FinBrief · Financial Digest",
        "sidebar_settings": "⚙️ AI Model & Mode Settings",
        "mode_select": "🌐 Select Operating Mode",
        "mode_free": "🆓 Free Mode (Open-Source LLM)",
        "mode_byok": "🔑 BYOK Mode (Bring Your Own Key)",
        "provider_select": "Select AI Provider",
        "model_select": "Select / Input Model",
        "api_key_input": "Enter your API Key",
        "security_title": "🔒 Privacy & Security Notice",
        "tech_note_free": "💡 **Free Mode Tech Note**: Powered by public no-key LLM services. No registration or API key required. Ideal for quick testing.",
        "tech_note_byok": "💡 **BYOK Tech Note**: Supports commercial models (GPT-4o / DeepSeek / Groq). Keys stored in session memory only.",
        "privacy_policy": """
        * **Data Privacy**: Uploaded documents are processed solely in memory and never stored on disk.
        * **Disclaimer**: Reports generated are for strategic reference only and do not constitute audit or financial advice.
        """,
        "upload_label": "Upload Financial Data or Report (PDF / Excel / CSV)",
        "preset_label": "💡 Quick Select Standard Template:",
        "template_label": "Analysis Template & Instructions (Editable):",
        "presets": {
            "C-Level Strategic Digest (Recommended)": "As a C-Level financial advisor, please analyze:\n1. Core revenue & margin trends\n2. Cash flow health & CAPEX\n3. Top 3 strategic risks and actionable recommendations",
            "HKFRS Compliance & Balance Sheet Audit": "Deconstruct under HKFRS accounting view:\n1. Balance sheet robustness (Liquidity & debt structure)\n2. Income statement efficiency (Gross & net margin shifts)\n3. Operating cash flow quality",
            "M&A Due Diligence Quick Assessment": "As an investment analyst, perform a concise DD:\n1. Core business model & competitive moat\n2. Hidden liability risks or accounting red flags\n3. 3-Year growth potential & valuation drivers"
        },
        "btn_generate": "🚀 Generate Strategic Report",
        "err_no_key": "⚠️ Please enter a valid API Key to enable BYOK mode!",
        "err_no_file": "⚠️ Please upload a financial document first!",
        "err_no_template": "⚠️ Please select or input an analysis template!",
        "report_header": "📈 FinBrief Strategic Financial Report",
        "btn_download": "📥 Download Report (Markdown)",
        "system_prompt": "You are a senior C-Level financial advisor and investment analyst well-versed in HKFRS and IFRS. Please output a professional, high-level financial strategic report in English."
    }
}

# --- 2. 頁面初始化與語言選擇 ---
st.set_page_config(page_title="FinBrief", layout="wide")

with st.sidebar:
    lang_choice = st.radio("🌐 Language / 語言", options=["繁體中文", "English"], index=0)
    lang_code = "zh" if lang_choice == "繁體中文" else "en"
    t = TRANSLATIONS[lang_code]

    st.header(t["sidebar_settings"])
    
    run_mode = st.radio(
        t["mode_select"],
        options=[t["mode_free"], t["mode_byok"]]
    )
    
    if run_mode == t["mode_free"]:
        st.info(t["tech_note_free"])
        active_api_key = "FREE_MODE"
    else:
        st.info(t["tech_note_byok"])
        provider = st.selectbox(t["provider_select"], ["OpenAI", "DeepSeek", "Groq"])
        active_api_key = st.text_input(t["api_key_input"], type="password")
        
        if provider == "OpenAI":
            selected_model = st.selectbox(t["model_select"], ["gpt-4o-mini", "gpt-4o"])
            base_url = None
        elif provider == "DeepSeek":
            selected_model = st.text_input(t["model_select"], value="deepseek-chat")
            base_url = "https://api.deepseek.com"
        else: # Groq
            selected_model = st.selectbox(t["model_select"], ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"])
            base_url = "https://api.groq.com/openai/v1"

    st.markdown("---")
    st.markdown(f"### {t['security_title']}")
    st.caption(t["privacy_policy"])

# --- 3. 完全免 Key 的公開免認證 LLM 函數 ---
def call_free_open_llm(system_prompt, user_prompt):
    """
    完全免 API Key、免認證的公開大模型 Endpoint
    """
    url = "https://text.pollinations.ai/"
    
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "model": "openai",
        "seed": 42
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Free LLM Endpoint Busy ({response.status_code}). Please try again in a moment.")
    except Exception as e:
        raise Exception(f"Free LLM Connection Error: {str(e)}")

# --- 4. 主畫面 UI 與一鍵模板選單 ---
st.title(t["title"])

uploaded_file = st.file_uploader(t["upload_label"], type=['pdf', 'xlsx', 'csv'])

# 一鍵選擇預設模板
st.write(t["preset_label"])
preset_options = list(t["presets"].keys())
selected_preset = st.selectbox("選擇預設範例 / Select Template", options=preset_options, index=0)

default_template_text = t["presets"][selected_preset]
template = st.text_area(t["template_label"], value=default_template_text, height=150)

def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    extracted_text = ""
    # 擷取前 30 頁關鍵內容，防止過大超時
    max_pages = min(len(pdf_reader.pages), 30)
    for i in range(max_pages):
        text = pdf_reader.pages[i].extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

# --- 5. 報告生成邏輯 ---
if st.button(t["btn_generate"]):
    if run_mode == t["mode_byok"] and not active_api_key:
        st.error(t["err_no_key"])
    elif not uploaded_file:
        st.warning(t["err_no_file"])
    elif not template.strip():
        st.warning(t["err_no_template"])
    else:
        file_type = uploaded_file.name.split('.')[-1].lower()
        extracted_content = ""

        with st.spinner("Processing file / 正在解析檔案關鍵內容..."):
            if file_type == 'pdf':
                extracted_content = extract_text_from_pdf(uploaded_file)
            elif file_type in ['xlsx', 'csv']:
                df = pd.read_excel(uploaded_file) if file_type == 'xlsx' else pd.read_csv(uploaded_file)
                extracted_content = df.to_string()

        with st.spinner("AI Analysis in progress / AI 正在進行財略分析..."):
            try:
                user_prompt = f"""
                【Analysis Requirements / 分析要求】:
                {template}

                【Financial Data / 財務數據】:
                {extracted_content[:40000]}
                """

                if run_mode == t["mode_free"]:
                    report_text = call_free_open_llm(t["system_prompt"], user_prompt)
                else:
                    client = OpenAI(
                        api_key=active_api_key,
                        base_url=base_url if 'base_url' in locals() and base_url else None
                    )
                    response = client.chat.completions.create(
                        model=selected_model,
                        messages=[
                            {"role": "system", "content": t["system_prompt"]},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.2
                    )
                    report_text = response.choices[0].message.content

                st.markdown("---")
                st.markdown(f"## {t['report_header']}")
                st.markdown(report_text)
                
                st.download_button(
                    label=t["btn_download"],
                    data=report_text,
                    file_name=f"FinBrief_Report_{lang_code}.md",
                    mime="text/markdown"
                )

            except Exception as e:
                st.error(f"❌ AI Error: {str(e)}")
