import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração e Design Minimalista (Dark Mode + Detalhes em Ciano)
st.set_page_config(page_title="Observatório de Turismo", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border-radius: 4px 4px 0px 0px; padding-top: 10px; padding-bottom: 10px; }
    .stTabs [aria-selected="true"] { color: #00E5FF; border-bottom: 2px solid #00E5FF; }
    </style>
""", unsafe_allow_html=True)

URL_EMPREGABILIDADE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        # Lê os dados, tira a linha de "Ano" e transforma os Meses em colunas para o gráfico
        df = pd.read_csv(url, skiprows=1, header=None)
        df = df.drop(0) 
        df = df.set_index(0).T 
        return df
    except Exception as e:
        return pd.DataFrame()

df_emp = carregar_dados(URL_EMPREGABILIDADE)

st.title("📊 Observatório de Turismo")
st.markdown("---")

aba1, aba2, aba3 = st.tabs(["💼 Empregabilidade", "📝 Cadastur", "✈️ Fluxo Turístico"])

with aba1:
    st.subheader("Evolução Mensal de Empregabilidade")
    if not df_emp.empty and 'Mês' in df_emp.columns:
        # Ajusta os dados automaticamente para o gráfico
        df_melt = df_emp.melt(id_vars=['Mês'], var_name='Setor', value_name='Saldo')
        df_melt['Saldo'] = pd.to_numeric(df_melt['Saldo'], errors='coerce')
        df_melt = df_melt.dropna(subset=['Saldo'])
        
        # Gera o Gráfico Interativo
        fig = px.line(df_melt, x='Mês', y='Saldo', color='Setor', template="plotly_dark", markers=True)
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=30, b=0), legend_title_text='',
            xaxis_title="", yaxis_title="Saldo de Empregos"
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#333333")
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Erro ao processar estrutura da planilha.")

with aba2:
    st.subheader("Registros Cadastur")
    st.info("Insira o link do Cadastur no código para visualizar.")

with aba3:
    st.subheader("Fluxo Turístico")
    st.info("Insira o link do Fluxo no código para visualizar.")
