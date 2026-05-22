import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Observatório de Turismo", layout="wide")

# CSS - Fundo Branco e Logo
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; }
    div[data-testid="stMetricValue"] { color: #0066FF; font-size: 28px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

URL_EMP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"
URL_CAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vScKBQfjVOP_WRtCo7QilgnPPGh3cA2VCT-RUnrJ_KoxxLixbTmcFAsfuG9EONT5F7bciZIBCn6Rwmw/pub?output=csv"
URL_FLX = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD0hlDacayEi-hCuWnZC37z-etoULtAG0DTrmnVbAMJc_A3Eo_EqapaE_3hCkA8Dudcv3kdOFbbT/pub?output=csv"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Garante que o Ano não fica com ".0"
        df['Ano'] = df['Ano'].astype(str).str.replace(".0", "", regex=False)
        df['Mês'] = df['Mês'].astype(str).str.strip()
        return df
    except Exception:
        return pd.DataFrame()

df_emp = carregar_dados(URL_EMP)
df_cad = carregar_dados(URL_CAD)
df_fluxo = carregar_dados(URL_FLX)

# --- SIDEBAR (FILTROS) ---
try:
    st.sidebar.image("logo.jpg", use_container_width=True)
except Exception:
    pass

st.sidebar.header("Filtros")

anos_disp = []
if not df_cad.empty and 'Ano' in df_cad.columns: anos_disp.extend(df_cad['Ano'].unique())
if not df_emp.empty and 'Ano' in df_emp.columns: anos_disp.extend(df_emp['Ano'].unique())
anos_disp = sorted(list(set(anos_disp))) if anos_disp else ["2024"]

ano_sel = st.sidebar.selectbox("Ano", anos_disp)
mes_sel = st.sidebar.selectbox("Mês", ["Todos", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])

def aplicar_filtros(df):
    if df.empty or 'Ano' not in df.columns: return df
    df_f = df[df['Ano'] == ano_sel]
    if mes_sel != "Todos":
        df_f = df_f[df_f['Mês'] == mes_sel]
    return df_f

df_e_f = aplicar_filtros(df_emp)
df_c_f = aplicar_filtros(df_cad)
df_f_f = aplicar_filtros(df_fluxo)

# --- CABEÇALHO (LOGO + TÍTULO) ---
col1, col2 = st.columns([1, 8])
with col1:
    try:
        st.image("logo.jpg", width=80)
    except Exception:
        pass
with col2:
    st.markdown("<h1 style='margin-top:-15px;'>Painel de Controle - Observatório</h1>", unsafe_allow_html=True)

st.markdown("---")

# --- ABAS E GRÁFICOS ---
aba1, aba2, aba3 = st.tabs(["💼 Empregabilidade", "📝 Cadastur", "✈️ Fluxo"])

def gerar_grafico(df, x_col, y_col, color_col, titulo_y):
    # Se um mês específico for escolhido, mostra gráfico de barras. Caso contrário, linha do tempo.
    if mes_sel == "Todos":
        fig = px.line(df, x=x_col, y=y_col, color=color_col, markers=True, template='plotly_white')
    else:
        fig = px.bar(df, x=color_col, y=y_col, color=color_col, template='plotly_white')
    
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=30, b=0))
    fig.update_yaxes(title_text=titulo_y)
    return fig

with aba1:
    if not df_e_f.empty and 'Setor' in df_e_f.columns:
        c1, c2 = st.columns(2)
        c1.metric("Saldo Total", int(df_e_f['Saldo'].sum()))
        c2.metric("Principal Setor", df_e_f.groupby('Setor')['Saldo'].sum().idxmax())
        st.plotly_chart(gerar_grafico(df_e_f, 'Mês', 'Saldo', 'Setor', "Saldo"), use_container_width=True)
    else:
        st.info("Aguardando atualização das colunas (Ano | Mês | Setor | Saldo) no Google Sheets.")

with aba2:
    if not df_c_f.empty and 'Categoria' in df_c_f.columns:
        c1, c2 = st.columns(2)
        c1.metric("Total de Registros", int(df_c_f['Total'].sum()))
        c2.metric("Principal Categoria", df_c_f.groupby('Categoria')['Total'].sum().idxmax())
        st.plotly_chart(gerar_grafico(df_c_f, 'Mês', 'Total', 'Categoria', "Registros"), use_container_width=True)
    else:
        st.info("Aguardando atualização das colunas (Ano | Mês | Categoria | Total) no Google Sheets.")

with aba3:
    if not df_f_f.empty and 'Atrativo' in df_f_f.columns:
        c1, c2 = st.columns(2)
        c1.metric("Total de Visitantes", int(df_f_f['Visitantes'].sum()))
        c2.metric("Principal Atrativo", df_f_f.groupby('Atrativo')['Visitantes'].sum().idxmax())
        st.plotly_chart(gerar_grafico(df_f_f, 'Mês', 'Visitantes', 'Atrativo', "Visitantes"), use_container_width=True)
    else:
        st.info("Aguardando atualização das colunas (Ano | Mês | Atrativo | Visitantes) no Google Sheets.")
