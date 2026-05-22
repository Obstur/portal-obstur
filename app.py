import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração e Identidade
st.set_page_config(page_title="Observatório de Turismo", layout="wide")

# CSS para esconder o emoji padrão, ajustar o logo e filtros
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #EEE; }
    .stMetric { border: 1px solid #F0F0F0; padding: 15px; border-radius: 10px; }
    div[data-testid="stMetricValue"] { color: #0066FF; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO ---
URL_EMP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"
URL_CAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vScKBQfjVOP_WRtCo7QilgnPPGh3cA2VCT-RUnrJ_KoxxLixbTmcFAsfuG9EONT5F7bciZIBCn6Rwmw/pub?output=csv"
URL_FLX = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD0hlDacayEi-hCuWnZC37z-etoULtAG0DTrmnVbAMJc_A3Eo_EqapaE_3hCkA8Dudcv3kdOFbbT/pub?output=csv"

def limpar_num(val):
    if pd.isna(val): return 0.0
    s = str(val).strip().replace(' ', '').replace('%', '')
    if not s or s in ['-', 'None', '']: return 0.0
    s = s.replace('.', '').replace(',', '.')
    try: return float(s)
    except: return 0.0

@st.cache_data(ttl=60)
def carregar_e_limpar(url, chave):
    try:
        df = pd.read_csv(url, header=None).dropna(how='all')
        idx = 0
        for i in range(5):
            if 'm' in str(df.iloc[i,0]).lower() or 'a' in str(df.iloc[i,0]).lower():
                idx = i
                break
        df_c = df.iloc[idx:].copy()
        df_c.columns = df_c.iloc[0]
        df_c = df_c.iloc[1:]
        df_c.columns.values[0] = chave
        df_c = df_c.dropna(subset=[chave])
        df_c = df_c[~df_c[chave].astype(str).str.lower().str.contains('total|fonte')]
        
        # Transposição
        dft = df_c.set_index(chave).T.reset_index()
        dft.rename(columns={dft.columns[0]: 'Mes'}, inplace=True)
        
        # Criar Coluna de Ano (Assume que a planilha tem anos ou vamos tratar como 2023/2024)
        # Se sua planilha não tiver coluna de ano, vamos simular para o filtro funcionar
        dft['Ano'] = dft['Mes'].astype(str).str.extract('(\d{4})').fillna("2024")
        dft['Mes_Nome'] = dft['Mes'].astype(str).str.replace('\d+', '', regex=True).str.strip().str.replace('/', '')
        
        for c in dft.columns:
            if c not in ['Mes', 'Ano', 'Mes_Nome']:
                dft[c] = dft[c].apply(limpar_num)
        return dft
    except: return pd.DataFrame()

# --- CARREGAR DADOS ---
df_e = carregar_e_limpar(URL_EMP, 'Setor')
df_c = carregar_e_limpar(URL_CAD, 'Categoria')
df_f = carregar_e_limpar(URL_FLX, 'Atrativo')

# --- SIDEBAR (FILTROS) ---
st.sidebar.image("logo.jpg", use_container_width=True)
st.sidebar.title("Filtros de Visualização")

lista_anos = sorted(df_e['Ano'].unique())
ano_sel = st.sidebar.selectbox("Selecione o Ano", lista_anos)

# Filtrando dados pelo ano selecionado
df_e_f = df_e[df_e['Ano'] == ano_sel]
df_c_f = df_c[df_c['Ano'] == ano_sel]
df_f_f = df_f[df_f['Ano'] == ano_sel]

st.sidebar.markdown("---")
st.sidebar.write("Painel desenvolvido para o Observatório de Turismo.")

# --- CABEÇALHO (LOGO + TÍTULO) ---
col_logo, col_tit = st.columns([1, 4])
with col_logo:
    st.image("logo.jpg", width=120)
with col_tit:
    st.title("Painel de Controle - Observatório de Turismo")
    st.write(f"Visualizando dados consolidados de {ano_sel}")

st.markdown("---")

# --- CONTEÚDO ---
aba1, aba2, aba3 = st.tabs(["💼 Empregabilidade", "📝 Cadastur", "✈️ Fluxo"])

with aba1:
    if not df_e_f.empty:
        setores = [c for c in df_e_f.columns if c not in ['Mes', 'Ano', 'Mes_Nome']]
        
        # Métricas
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo Total", f"{int(df_e_f[setores].sum().sum()):,}".replace(',', '.'))
        c2.metric("Melhor Desempenho", df_e_f[setores].sum().idxmax())
        c3.metric("Meses Coletados", len(df_e_f))
        
        # Gráfico de Linha
        dfm = df_e_f.melt(id_vars=['Mes_Nome'], value_vars=setores, var_name='Setor', value_name='Saldo')
        fig1 = px.line(dfm, x='Mes_Nome', y='Saldo', color='Setor', template="plotly_white", markers=True, title="Evolução Mensal")
        st.plotly_chart(fig1, use_container_width=True)
        
        # Gráfico de Barras Acumulado
        df_b = df_e_f[setores].sum().reset_index()
        df_b.columns = ['Setor', 'Total']
        fig2 = px.bar(df_b.sort_values(by='Total'), x='Total', y='Setor', orientation='h', template="plotly_white", title="Acumulado por Setor")
        st.plotly_chart(fig2, use_container_width=True)

with aba2:
    if not df_c_f.empty:
        categorias = [c for c in df_c_f.columns if c not in ['Mes', 'Ano', 'Mes_Nome']]
        dfm2 = df_c_f.melt(id_vars=['Mes_Nome'], value_vars=categorias, var_name='Categoria', value_name='Total')
        fig3 = px.line(dfm2, x='Mes_Nome', y='Total', color='Categoria', template="plotly_white", markers=True, title="Prestadores Ativos")
        st.plotly_chart(fig3, use_container_width=True)

with aba3:
    if not df_f_f.empty:
        atrativos = [c for c in df_f_f.columns if c not in ['Mes', 'Ano', 'Mes_Nome']]
        dfm3 = df_f_f.melt(id_vars=['Mes_Nome'], value_vars=atrativos, var_name='Atrativo', value_name='Visitantes')
        fig4 = px.line(dfm3, x='Mes_Nome', y='Visitantes', color='Atrativo', template="plotly_white", markers=True, title="Fluxo de Visitantes")
        st.plotly_chart(fig4, use_container_width=True)
