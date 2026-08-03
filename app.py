import streamlit as st
import pandas as pd
from pypdf import PdfReader
import io

st.set_page_config(page_title="FinBrief · 財略摘要器", layout="wide")
st.title("📊 FinBrief · 財略摘要器")

# 1. 允許上傳 PDF, Excel, CSV
uploaded_file = st.file_uploader(
    "上傳財務數據或報表 (PDF / Excel / CSV)", 
    type=['pdf', 'xlsx', 'csv']
)

template = st.text_area("貼上你的標準分析模板", height=150)

# 輔助函數：解析 PDF 文字
def extract_text_from_pdf(file):
    pdf_reader = PdfReader(file)
    extracted_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            extracted_text += text + "\n"
    return extracted_text

if uploaded_file and st.button("生成報告"):
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    with st.spinner("正在讀取並解析文件內容..."):
        if file_type == 'pdf':
            # 處理 PDF 檔案
            extracted_text = extract_text_from_pdf(uploaded_file)
            st.write("### PDF 報表內容預覽 (前 1,000 字)")
            st.text_area("擷取到的文字", value=extracted_text[:1000] + "...", height=200)
            
            # TODO: 將 extracted_text 與 template 一起帶入 AI LLM 分析
            st.success("PDF 解析成功！報告生成功能開發中...")
            
        elif file_type in ['xlsx', 'csv']:
            # 處理 Excel / CSV 數據
            df = pd.read_excel(uploaded_file) if file_type == 'xlsx' else pd.read_csv(uploaded_file)
            st.write("### 數據預覽", df.head())
            
            # TODO: 將 df 與 template 一起帶入 AI LLM 分析
            st.success("數據讀取成功！報告生成功能開發中...")
