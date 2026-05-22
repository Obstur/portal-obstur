import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página e Identidade Visual Minimalista (Branco Premium)
st.set_page_config(page_title="Observatório de Turismo", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; font-family: 'Inter', sans-serif; }
    h1, h2, h3 { color: #111111; font-weight: 700; letter-spacing: -0.5px; }
    .stTabs [data-baseweb="tab-list"] { gap: 16px; border-bottom: 2px solid #F0F0F0; }
    .stTabs [data-baseweb="tab"] { height: 45px; background-color: transparent; border-radius: 0px; padding: 10px 20px; color: #666666; font-weight: 500; }
    .stTabs [aria-selected="true"] { color: #0066FF; border-bottom: 2px solid #0066FF; font-weight: 600; }
    div[data-testid="stMetricValue"] { color: #0066FF; font-size: 32px; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: #666666; font-size: 14px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# Exibição do logo em formato JPG
try:
    st.image("logo.jpg", width=220)
except Exception:
    pass

# Links das Planilhas do Google Sheets
URL_EMPREGABILIDADE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"
URL_CADASTUR = "https://docs.google.com/spreadsheets/d/e/2PACX-1vScKBQfjVOP_WRtCo7QilgnPPGh3cA2VCT-RUnrJ_KoxxLixbTmcFAsfuG9EONT5F7bciZIBCn6Rwmw/pub?output=csv"
URL_FLUXO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD0hlDacayEi-hCuWnZC37z-etoULtAG0DTrmnVbAMJc_A3Eo_EqapaE_3hCkA8Dudcv3kdOFbbT/pub?output=csv"

# Limpeza e conversão numérica
def limpar_numeros(val):
    if pd.isna(val): return 0.0
    s = str(val).strip().replace(' ', '').replace('%', '')
    if not s or s in ['-', 'None', '']: return 0.0
    try:
        return float(s)
    except ValueError:
        pass
    if ',' in s and '.' in s:
        s = s.replace('.', '')
        s = s.replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0

# Processador dinâmico
@st.cache_data(ttl=60)
def processar_base_turismo(url, coluna_chave):
    try:
        df_raw = pd.read_csv(url, header=None).dropna(how='all')
        linha_meses = df_raw[df_raw[0].astype(str).str.strip().str.lower().isin(['mês', 'mês ', 'meses', 'mês/
