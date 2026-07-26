import streamlit as st
import pandas as pd

st.set_page_config(page_title="FinBrief · 財略摘要器", layout="wide")
st.title("📊 FinBrief · 財略摘要器")

uploaded_file = st.file_uploader("上傳季度財務數據 (Excel/CSV)", type=['xlsx', 'csv'])
template = st.text_area("貼上你的標準分析模板", height=150)

if uploaded_file and st.button("生成報告"):
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    st.write("### 數據預覽", df.head())
    # TODO: 串接 AI 計算指標並生成報告
    st.success("報告生成功能開發中...")