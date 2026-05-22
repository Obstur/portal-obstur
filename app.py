import streamlit as st
import pandas as pd
import plotly.express as px

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Observatório de Turismo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Minimalista Premium
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

# Logo
try:
    st.image("logo.jpg", width=220)
except:
    st.title("Observatório de Turismo")

st.title("📊 Observatório de Turismo")

# ==================== LINKS DAS PLANILHAS ====================
URL_EMPREGABILIDADE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"
URL_CADASTUR = "https://docs.google.com/spreadsheets/d/e/2PACX-1vScKBQfjVOP_WRtCo7QilgnPPGh3cA2VCT-RUnrJ_KoxxLixbTmcFAsfuG9EONT5F7bciZIBCn6Rwmw/pub?output=csv"
URL_FLUXO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD0hlDacayEi-hCuWnZC37z-etoULtAG0DTrmnVbAMJc_A3Eo_EqapaE_3hCkA8Dudcv3kdOFbbT/pub?output=csv"

# ==================== FUNÇÃO DE LIMPEZA ====================
def limpar_numeros(val):
    if pd.isna(val):
        return 0.0
    s = str(val).strip().replace(' ', '').replace('%', '')
    if not s or s in ['-', 'None', '']:
        return 0.0
    try:
        return float(s)
    except ValueError:
        pass
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return 0.0

# ==================== PROCESSADOR DE PLANILHAS ====================
@st.cache_data(ttl=300)
def processar_base_turismo(url):
    try:
        df_raw = pd.read_csv(url, header=None).dropna(how='all')
        
        # Normaliza primeira coluna para busca
        col0 = df_raw[0].astype(str).str.strip().str.lower()
        
        # Busca linha de cabeçalho dos meses (mais robusto)
        mask_meses = col0.str.contains(r'mês|meses|periodo|competência', na=False, regex=True)
        linha_meses_idx = col0[mask_meses].index
        
        if len(linha_meses_idx) == 0:
            st.warning("Não encontrou linha de meses automaticamente.")
            return df_raw, None
        
        idx = linha_meses_idx[0]
        
        # Extrai cabeçalhos
        headers = df_raw.iloc[idx].values
        df = df_raw.iloc[idx+1:].copy()
        df.columns = headers
        
        # Limpa números
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(limpar_numeros)
        
        return df, headers
        
    except Exception as e:
        st.error(f"Erro ao processar planilha: {e}")
        return None, None

# ==================== INTERFACE ====================
tab1, tab2, tab3 = st.tabs(["Empregabilidade", "Cadastur", "Fluxo Turístico"])

with tab1:
    st.subheader("Empregabilidade no Turismo")
    with st.spinner("Carregando dados de Empregabilidade..."):
        df_emp, headers_emp = processar_base_turismo(URL_EMPREGABILIDADE)
    
    if df_emp is not None:
        st.dataframe(df_emp, use_container_width=True)
        
        # Exemplo de gráfico automático
        if len(df_emp.columns) > 1:
            fig = px.bar(df_emp, x=df_emp.columns[0], y=df_emp.columns[1:],
                        title="Evolução por Mês")
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Cadastur")
    with st.spinner("Carregando dados do Cadastur..."):
        df_cad, headers_cad = processar_base_turismo(URL_CADASTUR)
    
    if df_cad is not None:
        st.dataframe(df_cad, use_container_width=True)

with tab3:
    st.subheader("Fluxo Turístico")
    with st.spinner("Carregando dados de Fluxo..."):
        df_fluxo, headers_fluxo = processar_base_turismo(URL_FLUXO)
    
    if df_fluxo is not None:
        st.dataframe(df_fluxo, use_container_width=True)
        
        if len(df_fluxo.columns) > 1:
            fig2 = px.line(df_fluxo, x=df_fluxo.columns[0], y=df_fluxo.columns[1:],
                          title="Fluxo Turístico ao Longo do Tempo")
            st.plotly_chart(fig2, use_container_width=True)

st.caption("Observatório de Turismo • Atualização automática via Google Sheets")
