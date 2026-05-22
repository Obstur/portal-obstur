import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Observatório", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    .stTabs [data-baseweb="tab-list"] { border-bottom: 2px solid #F0F0F0; }
    div[data-testid="stMetricValue"] { color: #0066FF; font-size: 32px; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

try:
    st.image("logo.jpg", width=220)
except Exception:
    pass

URL_EMP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"
URL_CAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vScKBQfjVOP_WRtCo7QilgnPPGh3cA2VCT-RUnrJ_KoxxLixbTmcFAsfuG9EONT5F7bciZIBCn6Rwmw/pub?output=csv"
URL_FLX = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD0hlDacayEi-hCuWnZC37z-etoULtAG0DTrmnVbAMJc_A3Eo_EqapaE_3hCkA8Dudcv3kdOFbbT/pub?output=csv"

def limpar_num(val):
    if pd.isna(val): return 0.0
    s = str(val).strip().replace(' ', '').replace('%', '')
    if not s or s in ['-', 'None', '']: return 0.0
    if ',' in s and '.' in s:
        s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        s = s.replace(',', '.')
    try: return float(s)
    except Exception: return 0.0

@st.cache_data(ttl=60)
def processar(url, chave):
    try:
        df = pd.read_csv(url, header=None).dropna(how='all')
        
        idx = 0
        for i in range(5):
            txt = str(df.iloc[i, 0]).lower()
            if 'm' in txt or 'a' in txt:
                idx = i
                break
                
        df_c = df.iloc[idx:].copy()
        df_c.columns = df_c.iloc[0]
        df_c = df_c.iloc[1:]
        
        df_c.columns.values[0] = chave
        df_c = df_c.dropna(subset=[chave])
        df_c = df_c[~df_c[chave].astype(str).str.lower().str.contains('total|fonte')]
        
        dft = df_c.set_index(chave).T.reset_index()
        dft.rename(columns={dft.columns[0]: 'Mes'}, inplace=True)
        dft = dft[dft['Mes'].astype(str).str.strip() != '']
        
        for c in dft.columns:
            if c != 'Mes':
                dft[c] = dft[c].apply(limpar_num)
        return dft
    except Exception:
        return pd.DataFrame()

df_e = processar(URL_EMP, 'Setor')
df_c = processar(URL_CAD, 'Categoria')
df_f = processar(URL_FLX, 'Atrativo')

st.title("📊 Painel de Controle - Observatório")
st.markdown("---")

aba1, aba2, aba3 = st.tabs(["💼 Empregabilidade", "📝 Cadastur", "✈️ Fluxo"])

def aplicar_graf(fig, titulo_y):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=50, r=20, t=50, b=50), height=450
    )
    fig.update_yaxes(title_text=titulo_y)
    return fig

with aba1:
    if not df_e.empty:
        cols = [c for c in df_e.columns if c != 'Mes']
        c1, c2, c3 = st.columns(3)
        c1.metric("Saldo Acumulado", f"{int(df_e[cols].sum().sum()):,}".replace(',', '.'))
        c2.metric("Principal Setor", df_e[cols].sum().idxmax())
        c3.metric("Meses Analisados", len(df_e))
        
        dfm = df_e.melt(id_vars=['Mes'], var_name='Setor', value_name='Saldo')
        fig1 = px.line(dfm, x='Mes', y='Saldo', color='Setor', template="plotly_white", markers=True)
        st.plotly_chart(aplicar_graf(fig1, "Saldo"), use_container_width=True)
        
        df_b = df_e[cols].sum().reset_index()
        df_b.columns = ['Setor', 'Total']
        fig2 = px.bar(df_b.sort_values(by='Total'), x='Total', y='Setor', orientation='h', template="plotly_white")
        st.plotly_chart(aplicar_graf(fig2, ""), use_container_width=True)

with aba2:
    if not df_c.empty:
        dfm2 = df_c.melt(id_vars=['Mes'], var_name='Cat', value_name='Total')
        fig3 = px.line(dfm2, x='Mes', y='Total', color='Cat', template="plotly_white", markers=True)
        st.plotly_chart(aplicar_graf(fig3, "Prestadores"), use_container_width=True)

with aba3:
    if not df_f.empty:
        dfm3 = df_f.melt(id_vars=['Mes'], var_name='Atrativo', value_name='Total')
        fig4 = px.line(dfm3, x='Mes', y='Total', color='Atrativo', template="plotly_white", markers=True)
        st.plotly_chart(aplicar_graf(fig4, "Visitantes"), use_container_width=True)
        
