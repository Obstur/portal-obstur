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
        linha_meses = df_raw[df_raw[0].astype(str).str.strip().str.lower().isin(['mês', 'mês ', 'meses', 'mês/ano', 'ano'])]
        
        if not linha_meses.empty:
            idx_inicio = linha_meses.index[0]
            df_clean = df_raw.iloc[idx_inicio:].copy()
        else:
            df_clean = df_raw.copy()
            
        df_clean.columns = df_clean.iloc[0]
        df_clean = df_clean.iloc[1:]
        
        df_clean.columns.values[0] = coluna_chave
        df_clean = df_clean.dropna(subset=[coluna_chave])
        df_clean[coluna_chave] = df_clean[coluna_chave].astype(str).str.strip()
        df_clean = df_clean[~df_clean[coluna_chave].str.lower().str.contains('total|fonte|comparativo')]
        
        df_t = df_clean.set_index(coluna_chave).T.reset_index()
        df_t.rename(columns={df_t.columns[0]: 'Mês'}, inplace=True)
        df_t['Mês'] = df_t['Mês'].astype(str).str.strip()
        df_t = df_t[df_t['Mês'] != '']
        
        for col in df_t.columns:
            if col != 'Mês':
                df_t[col] = df_t[col].apply(limpar_numeros)
                
        return df_t
    except Exception:
        return pd.DataFrame()

# Execução automática
df_emp = processar_base_turismo(URL_EMPREGABILIDADE, 'Setor')
df_cad = processar_base_turismo(URL_CADASTUR, 'Categoria')
df_fluxo = processar_base_turismo(URL_FLUXO, 'Atrativo')

st.title("📊 Painel de Controle - Observatório de Turismo")
st.markdown("---")

aba1, aba2, aba3 = st.tabs(["💼 Empregabilidade", "📝 Cadastur", "✈️ Fluxo Turístico"])

def aplicar_estilo_grafico(fig, y_title):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=12, color="#333333"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        margin=dict(l=50, r=20, t=50, b=50),
        height=450
    )
    fig.update_xaxes(showline=True, linewidth=1, linecolor='#EAEAEA', gridcolor='#F9F9F9')
    fig.update_yaxes(showline=True, linewidth=1, linecolor='#EAEAEA', gridcolor='#EAEAEA', title_text=y_title)
    return fig

# --- EMPREGABILIDADE ---
with aba1:
    if not df_emp.empty:
        setores_cols = [c for c in df_emp.columns if c != 'Mês']
        col1, col2, col3 = st.columns(3)
        col1.metric("Saldo Acumulado", f"{int(df_emp[setores_cols].sum().sum()):,}".replace(',', '.'))
        col2.metric("Principal Setor", df_emp[setores_cols].sum().idxmax())
        col3.metric("Meses Analisados", len(df_emp))
        
        df_melt = df_emp.melt(id_vars=['Mês'], var_name='Setor', value_name='Saldo')
        fig_emp = px.line(df_melt, x='Mês', y='Saldo', color='Setor', template="plotly_white", markers=True)
        st.plotly_chart(aplicar_estilo_grafico(fig_emp, "Saldo de Empregos"), use_container_width=True)
        
        st.markdown("### 📊 Acumulado Consolidado por Setor")
        df_bar = df_emp[setores_cols].sum().reset_index()
        df_bar.columns = ['Setor', 'Total']
        df_bar = df_bar.sort_values(by='Total', ascending=True)
        fig_bar = px.bar(df_bar, x='Total', y='Setor', orientation='h', template="plotly_white", color_discrete_sequence=['#0066FF'])
        st.plotly_chart(aplicar_estilo_grafico(fig_bar, ""), use_container_width=True)
    else:
        st.error("Erro ao estruturar dados de Empregabilidade.")

# --- CADASTUR ---
with aba2:
    if not df_cad.empty:
        cat_cols = [c for c in df_cad.columns if c != 'Mês']
        st.columns(2)[0].metric("Registros Ativos Recentes", f"{int(df_cad[cat_cols].iloc[-1].sum() if len(df_cad) > 0 else 0):,}".replace(',', '.'))
        
        df_melt_cad = df_cad.melt(id_vars=['Mês'], var_name='Categoria', value_name='Total')
        fig_cad = px.line(df_melt_cad, x='Mês', y='Total', color='Categoria', template="plotly_white", markers=True)
        st.plotly_chart(aplicar_estilo_grafico(fig_cad, "Prestadores Ativos"), use_container_width=True)
    else:
        st.error("Erro ao estruturar dados do Cadastur.")

# --- FLUXO TURÍSTICO ---
with aba3:
    if not df
