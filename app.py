import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuração e Design Minimalista (Branco)
st.set_page_config(page_title="Observatório de Turismo", layout="wide")

# CSS para garantir fundo branco e visual limpo
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; color: #31333F; font-family: 'Inter', sans-serif; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #E6E6E6; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border-radius: 4px 4px 0px 0px; padding: 10px 16px; color: #31333F; }
    .stTabs [aria-selected="true"] { color: #007BFF; border-bottom: 2px solid #007BFF; font-weight: bold; }
    .stImage { margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# 2. Exibição do Logo do Observatório
# Certifique-se de que o arquivo 'logo.png' esteja no seu GitHub
st.image("logo.png", width=200)

# Links Públicos dos Dados Corrigidos
URL_EMPREGABILIDADE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQT-EtDg1pO7uGcQf8yHNiLKb2euWDVDOP84yaZKzOPQNlssQbhbR4kSHJ5HNqbVt1NS8VPFsFDm5dp/pub?output=csv"
URL_CADASTUR = "https://docs.google.com/spreadsheets/d/e/2PACX-1vScKBQfjVOP_WRtCo7QilgnPPGh3cA2VCT-RUnrJ_KoxxLixbTmcFAsfuG9EONT5F7bciZIBCn6Rwmw/pub?output=csv"
URL_FLUXO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQKgD0hlDacayEi-hCuWnZC37z-etoULtAG0DTrmnVbAMJc_A3Eo_EqapaE_3hCkA8Dudcv3kdOFbbT/pub?output=csv"

# 3. Cache para Otimizar o Carregamento
@st.cache_data(ttl=60)
def carregar_dados_formatados(url):
    try:
        # Carrega pulando a linha de título ("Fonte: Sistema...")
        df = pd.read_csv(url, skiprows=1)
        # Limpa espaços em branco dos cabeçalhos
        df.columns = df.columns.str.strip()
        
        # Converte colunas numéricas para float, lidando com erros
        colunas_valores = df.columns.drop('Mês')
        for col in colunas_valores:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            
        return df
    except Exception as e:
        return pd.DataFrame()

# Carregando e Processando os Dados
df_emp = carregar_dados_formatados(URL_EMPREGABILIDADE)
df_cad = carregar_dados_formatados(URL_CADASTUR)
df_fluxo = carregar_dados_formatados(URL_FLUXO)

# 4. Título Principal
st.title("📊 Observatório de Turismo - Painel Interativo")
st.markdown("---")

# 5. Estrutura de Abas
aba1, aba2, aba3 = st.tabs(["💼 Empregabilidade", "📝 Cadastur", "✈️ Fluxo Turístico"])

# --- ABA 1: EMPREGABILIDADE ---
with aba1:
    st.subheader("Evolução Mensal e Comparativo por Setor")
    
    if not df_emp.empty:
        # Preparando dados para o gráfico de linha (automático)
        df_melt = df_emp.melt(id_vars=['Mês'], var_name='Setor', value_name='Saldo')
        
        # Filtro interativo automático (gerado a partir dos dados)
        setores = df_melt['Setor'].unique()
        setores_selecionados = st.multiselect("Selecione os Setores para Comparação", setores, default=setores[:2])
        
        # Filtra os dados com base na seleção
        df_filtrado = df_melt[df_melt['Setor'].isin(setores_selecionados)]
        
        # Gráfico Interativo de Evolução Mensal
        fig_evolucao = px.line(df_filtrado, x='Mês', y='Saldo', color='Setor', template="plotly_white", markers=True)
        fig_evolucao.update_layout(xaxis_title="", yaxis_title="Saldo de Empregos", legend_title="")
        st.plotly_chart(fig_evolucao, use_container_width=True)
        
        st.markdown("---")
        
        # Comparativo Total Acumulado (automático)
        st.subheader("Saldo Acumulado no Período (2023)")
        
        df_acumulado = df_emp.drop(columns='Mês').sum().sort_values()
        
        # Gráfico Interativo de Barras Comparativo
        fig_acumulado = px.bar(df_acumulado, x=df_acumulado.values, y=df_acumulado.index, orientation='h', template="plotly_white")
        fig_acumulado.update_layout(xaxis_title="Saldo Total de Empregos", yaxis_title="")
        st.plotly_chart(fig_acumulado, use_container_width=True)

    else:
        st.error("Erro ao processar dados de Empregabilidade. Verifique a planilha.")

# --- ABA 2: CADASTUR ---
with aba2:
    st.subheader("Evolução e Distribuição de Registros Cadastur")
    
    if not df_cad.empty:
        # Preparando dados para o gráfico de linha (automático)
        df_melt_cad = df_cad.melt(id_vars=['Mês'], var_name='Categoria', value_name='Total')
        
        # Filtro interativo automático
        categorias_cad = df_melt_cad['Categoria'].unique()
        categorias_selecionadas_cad = st.multiselect("Selecione as Categorias", categorias_cad, default=categorias_cad[:1])
        
        # Filtra os dados
        df_filtrado_cad = df_melt_cad[df_melt_cad['Categoria'].isin(categorias_selecionadas_cad)]
        
        # Gráfico Interativo de Evolução Mensal
        fig_evolucao_cad = px.line(df_filtrado_cad, x='Mês', y='Total', color='Categoria', template="plotly_white", markers=True)
        fig_evolucao_cad.update_layout(xaxis_title="", yaxis_title="Total de Registros", legend_title="")
        st.plotly_chart(fig_evolucao_cad, use_container_width=True)
        
    else:
        st.error("Dados de Cadastur não carregados. Verifique se o link está público como CSV.")

# --- ABA 3: FLUXO TURÍSTICO ---
with aba3:
    st.subheader("Volume de Visitantes e Sazonalidade")
    
    if not df_fluxo.empty:
        # Preparando dados para o gráfico de linha (automático)
        df_melt_fluxo = df_fluxo.melt(id_vars=['Mês'], var_name='Atrativo/Tipo', value_name='Visitantes')
        
        # Filtro interativo automático
        atrativos = df_melt_fluxo['Atrativo/Tipo'].unique()
        atrativos_selecionados = st.multiselect("Selecione Atrativos ou Tipos", atrativos, default=atrativos[:2])
        
        # Filtra os dados
        df_filtrado_fluxo = df_melt_fluxo[df_melt_fluxo['Atrativo/Tipo'].isin(atrativos_selecionados)]
        
        # Gráfico Interativo de Evolução Mensal
        fig_evolucao_fluxo = px.line(df_filtrado_fluxo, x='Mês', y='Visitantes', color='Atrativo/Tipo', template="plotly_white", markers=True)
        fig_evolucao_fluxo.update_layout(xaxis_title="", yaxis_title="Número de Visitantes", legend_title="")
        st.plotly_chart(fig_evolucao_fluxo, use_container_width=True)
        
    else:
        st.error("Dados de Fluxo Turístico não carregados. Verifique se o link está público como CSV.")
