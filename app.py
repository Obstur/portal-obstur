import streamlit as st
import pandas as pd

st.set_page_config(page_title="Painel de Turismo", layout="wide")

# Link corrigido para puxar como CSV puro
URL_EMPREGABILIDADE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"

@st.cache_data(ttl=60)
def carregar_dados(url):
    try:
        # Pula a primeira linha de texto ("Fonte: Sistema...")
        df = pd.read_csv(url, skiprows=1)
        return df
    except Exception as e:
        return pd.DataFrame()

df_emp = carregar_dados(URL_EMPREGABILIDADE)

st.title("📊 Observatório de Turismo")
st.markdown("---")

if not df_emp.empty:
    st.success("Dados conectados com sucesso!")
    st.dataframe(df_emp)
else:
    st.error("Erro ao ler a planilha. Verifique se o link está publicado corretamente como CSV.")
