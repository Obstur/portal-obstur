O texto foi cortado novamente pelo navegador na hora de colar.

Eu quebrei as linhas longas do código em partes menores para evitar que o GitHub corte o texto.

Por favor, clique no botão Copy code no canto superior direito do bloco abaixo, apague tudo no GitHub e cole:

Python
import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
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

try:
    st.image("logo.jpg", width=220)
except Exception:
    pass

URL_EMP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"
URL_CAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vScKBQfjVOP_WRtCo7QilgnPPGh3cA2VCT-RUnrJ_KoxxLixbTmcFAsfuG9EONT5F7bciZIBCn6Rwmw/pub?output=csv"
URL_FLX = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD0hlDacayEi-hCuWnZC37z-etoULtAG0DTrmnVbAMJc_A3Eo_EqapaE_3hCkA8Dudcv3kdOFbbT/pub?output=csv"

def limpar_numeros(val):
    if pd.isna(val): return 0.0
    s = str(val).strip().replace(' ', '').replace('%', '')
    if not s or s in ['-', 'None', '']: return 0.0
    try: return float(s)
    except ValueError: pass
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try: return float(s)
    except ValueError: return 0.0

@st.cache_data(ttl=60)
def processar_base(url, coluna_chave):
    try:
        df_raw = pd.read_csv(url, header=None).dropna(how='all')
        
        # Linhas divididas para não dar erro ao colar
        termos = ['mês', 'mês ', 'meses', 'mês/ano', 'ano']
        buscas = df_raw[0].astype(str).str.strip().str.lower()
        linha_meses = df_raw[buscas.isin(termos)]
        
        if not linha_meses.empty:
            df_clean = df_raw.iloc[linha_meses.index[0]:].copy()
        else:
            df_clean = df_raw.copy()
            
        df_clean.columns = df_clean.iloc[0]
        df_clean = df_clean.iloc[1:]
        
        df_clean.columns.values[0] = coluna_chave
        df_clean = df_clean.dropna(subset=[coluna_chave])
        df_clean[coluna_chave] = df_clean[coluna_chave].astype(str).str.strip()
        
        filtro_txt = df_clean[coluna_chave].str.lower()
        df_clean = df_clean[~filtro_txt.str.contains('total|fonte|comparativo')]
        
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

df_emp = processar_base(URL_EMP, 'Setor')
df_cad = processar_base(URL_CAD, 'Categoria')
df_fluxo = processar_base(URL_FLX, 'Atrativo')

st.title("📊 Painel de Controle - Observatório de Turismo")
st.markdown("---")

aba1, aba2, aba3 = st.tabs(["💼 Empregabilidade", "📝 Cadastur", "✈️ Fluxo Turístico"])

def estilo_graf(fig, y_title):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12, color="#333"),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5),
        margin=dict(l=50, r=20, t=50, b=50), height=450
    )
    fig.update_xaxes(showline=True, linecolor='#EAEAEA', gridcolor='#F9F9F9')
    fig.update_yaxes(showline=True, linecolor='#EAEAEA', gridcolor='#EAEAEA', title_text=y_title)
    return fig

with aba1:
    if not df_emp.empty:
        cols = [c for c in df_emp.columns if c != 'Mês']
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo Acumulado", f"{int(df_emp[cols].sum().sum()):,}".replace(',', '.'))
        c2.metric("Principal Setor", df_emp[cols].sum().idxmax())
        c3.metric("Meses Analisados", len(df_emp))
        
        df_m = df_emp.melt(id_vars=['Mês'], var_name='Setor', value_name='Saldo')
        fig1 = px.line(df_m, x='Mês', y='Saldo', color='Setor', template="plotly_white", markers=True)
        st.plotly_chart(estilo_graf(fig1, "Saldo"), use_container_width=True)
        
        st.markdown("### 📊 Acumulado por Setor")
        df_b = df_emp[cols].sum().reset_index()
        df_b.columns = ['Setor', 'Total']
        df_b = df_b.sort_values(by='Total')
        fig2 = px.bar(df_b, x='Total', y='Setor', orientation='h', template="plotly_white", color_discrete_sequence=['#0066FF'])
        st.plotly_chart(estilo_graf(fig2, ""), use_container_width=True)

with aba2:
    if not df_cad.empty:
        cols = [c for c in df_cad.columns if c != 'Mês']
        st.columns(2)[0].metric("Registros Ativos", f"{int(df_cad[cols].iloc[-1].sum() if len(df_cad)>0 else 0):,}".replace(',', '.'))
        
        df_m2 = df_cad.melt(id_vars=['Mês'], var_name='Categoria', value_name='Total')
        fig3 = px.line(df_m2, x='Mês', y='Total', color='Categoria', template="plotly_white", markers=True)
        st.plotly_chart(estilo_graf(fig3, "Prestadores"), use_container_width=True)

with aba3:
    if not df_fluxo.empty:
        cols = [c for c in df_fluxo.columns if c != 'Mês']
        st.columns(2)[0].metric("Volume de Visitantes", f"{int(df_fluxo[cols].sum().sum()):,}".replace(',', '.'))
        
        df_m3 = df_fluxo.melt(id_vars=['Mês'], var_name='Atrativo', value_name='Visitantes')
        fig4 = px.line(df_m3, x='Mês', y='Visitantes', color='Atrativo', template="plotly_white", markers=True)
        st.plotly_chart(estilo_graf(fig4, "Visitantes"), use_container_width=True)
