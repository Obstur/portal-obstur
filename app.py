"""
OBSERVATÓRIO DE TURISMO — UFPR
Painel único | Empregabilidade · Cadastur · Fluxo Turístico
Lê dados publicados em CSV no Google Sheets.
"""

import re
import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components


LOGO_URL = "https://raw.githubusercontent.com/Obstur/portal-obstur/main/.devcontainer/logo.jpg"

st.set_page_config(
    page_title="Observatório de Turismo · UFPR",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

URL_CAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQIJaja_RfMVmdabkhm5QyvK6aREnFF267pobuKIZ5BTLaymAb03Fc3N_ofkHaGL8UJIZz-UeWx6Sj5/pub?output=csv"
URL_EMP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqGPUme21AUn8I9-rhiW-fyWOIAU03Rp48B7bB1oywwZWXZWjaYpFqgXDa9XBIjfa7Roh4cI-sPx4i/pub?output=csv"
URL_FLX = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJm-ju6hjisM-TzBsOv1g--vyh_sKd8g_TP8IH50211oZSPyJPVT8P24UFUFvtm9gkqZugsg98nbez/pub?output=csv"

# Cores e Paleta ajustadas
C1 = "#e84624"  # Laranja
C2 = "#005bc5"  # Azul claro
C3 = "#012677"  # Azul médio
C4 = "#001449"  # Azul escuro

BG = "#e0e0e0"       # Fundo geral 100% cinza
BG_ABA = "#d6d6d6"   # Cinza escuro para a lista de abas
CARD = "#ffffff"     # Fundo branco para gráficos e métricas
TEXT = "#000000"     # Letras pretas
BORDER = "#bcbcbc"

PALETA = [C2, C3, C4, C1, "#3b82f6", "#1d4ed8", "#1e3a8a", "#f97316", "#93c5fd", "#60a5fa"]

MESES_ABR = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

MESES_FULL = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

ORDEM_MES = {m: i for i, m in enumerate(MESES_FULL)}

# CSS agressivo para forçar o layout cinza, gráficos brancos e letras pretas
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inclusive+Sans:ital,wght@0,300..700;1,300..700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {{
    background-color: {BG} !important;
    color: {TEXT} !important;
    font-family: "Inclusive Sans", Arial, sans-serif !important;
}}

* {{
    font-family: "Inclusive Sans", Arial, sans-serif !important;
}}

p, span, div, label, h1, h2, h3, h4, h5, h6, li {{
    color: {TEXT} !important;
}}

[data-testid="stHeader"], [data-testid="stToolbar"] {{
    background-color: {BG} !important;
}}

.block-container {{
    padding: 0.75rem 2rem 2rem 2rem !important;
    max-width: 1400px;
}}

section[data-testid="stSidebar"] {{
    display: none !important;
}}

/* Abas */
.stTabs [data-baseweb="tab-list"] {{
    background-color: {BG_ABA} !important;
    border-bottom: 2px solid {C3} !important;
    gap: 4px;
    padding: 8px 10px 0 10px;
    border-radius: 18px 18px 0 0;
}}

.stTabs [data-baseweb="tab"] {{
    color: {TEXT} !important;
    font-weight: 600;
    font-size: 13px;
    padding: 11px 22px;
    background: transparent !important;
}}

.stTabs [aria-selected="true"] {{
    color: {TEXT} !important;
    border-bottom: 3px solid {C1} !important;
    background: {BG} !important;
    border-radius: 14px 14px 0 0;
}}

.stTabs [data-baseweb="tab-panel"] {{
    background-color: {BG} !important;
    padding-top: 1.5rem;
}}

/* Caixa das Métricas Branca */
[data-testid="stMetric"] {{
    background-color: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-left: 5px solid {C1} !important;
    border-radius: 12px !important;
    padding: 16px 18px !important;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
}}

[data-testid="stMetricLabel"] * {{
    font-size: 12px !important;
    text-transform: uppercase;
    font-weight: bold !important;
}}

[data-testid="stMetricValue"] * {{
    font-size: 26px !important;
    font-weight: 800 !important;
}}

/* Títulos das seções */
.sec-title {{
    font-size: 12px;
    font-weight: bold;
    color: {TEXT};
    text-transform: uppercase;
    border-bottom: 2px solid {C1};
    padding-bottom: 4px;
    margin: 18px 0 14px;
}}

.fonte {{
    font-size: 11px;
    font-weight: bold;
    margin-bottom: 8px;
}}

/* Selectbox Branca */
[data-baseweb="select"] > div {{
    background-color: {CARD} !important;
    border-color: {BORDER} !important;
    border-radius: 8px !important;
}}

hr {{
    border-color: {BORDER} !important;
}}
</style>
""", unsafe_allow_html=True)


def sem_acento(valor):
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def normaliza_mes(valor):
    chave = sem_acento(valor).strip().lower()
    mapa = {
        "jan": "Janeiro", "janeiro": "Janeiro",
        "fev": "Fevereiro", "fevereiro": "Fevereiro",
        "mar": "Março", "marco": "Março", "março": "Março",
        "abr": "Abril", "abril": "Abril",
        "mai": "Maio", "maio": "Maio",
        "jun": "Junho", "junho": "Junho",
        "jul": "Julho", "julho": "Julho",
        "ago": "Agosto", "agosto": "Agosto",
        "set": "Setembro", "setembro": "Setembro",
        "out": "Outubro", "outubro": "Outubro",
        "nov": "Novembro", "novembro": "Novembro",
        "dez": "Dezembro", "dezembro": "Dezembro",
    }
    return mapa.get(chave)


def normaliza_numero(valor):
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()
    if not texto:
        return pd.NA

    texto = texto.replace("\xa0", "").replace(" ", "")
    texto = re.sub(r"[^0-9,.\-]", "", texto)

    if texto in {"", "-", ".", ","}:
        return pd.NA

    sinal = -1 if texto.startswith("-") else 1
    texto = texto.lstrip("-")

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        partes = texto.split(",")
        texto = "".join(partes) if len(partes[-1]) == 3 else ".".join(partes)
    elif "." in texto:
        partes = texto.split(".")
        if len(partes) > 1 and all(partes):
            texto = partes[0] + "".join(p.ljust(3, "0") for p in partes[1:])

    try:
        return sinal * float(texto)
    except ValueError:
        return pd.NA


def formata_int(valor):
    if pd.isna(valor):
        return "—"
    return f"{int(round(float(valor))):,}".replace(",", ".")


def prepara_base(df, coluna_valor):
    df = df.copy()
    df.columns = df.columns.str.strip().str.lower()
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
    df["mes"] = df["mes"].apply(normaliza_mes)
    df[coluna_valor] = df[coluna_valor].apply(normaliza_numero)
    return df.dropna(subset=["ano", "mes"])


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_csv(url, coluna_valor):
    df = pd.read_csv(url, dtype=str)
    return prepara_base(df, coluna_valor)


def carregar_dados():
    try:
        emp = carregar_csv(URL_EMP, "saldo")
    except Exception as exc:
        st.error(f"Erro ao carregar empregabilidade: {exc}")
        emp = pd.DataFrame(columns=["ano", "mes", "setor", "saldo"])

    try:
        cad = carregar_csv(URL_CAD, "quantidade")
    except Exception as exc:
        st.error(f"Erro ao carregar Cadastur: {exc}")
        cad = pd.DataFrame(columns=["ano", "mes", "categoria", "quantidade"])

    try:
        flx = carregar_csv(URL_FLX, "valor")
    except Exception as exc:
        st.error(f"Erro ao carregar fluxo turístico: {exc}")
        flx = pd.DataFrame(columns=["ano", "mes", "atrativo", "indicador", "valor"])

    return emp, cad, flx


def layout_base(height=280, title=""):
    layout = dict(
        paper_bgcolor=CARD, # Fundo Branco para o gráfico
        plot_bgcolor=CARD,  # Fundo Branco para a área de plotagem
        font=dict(color=TEXT, size=11, family="Inclusive Sans, Arial, sans-serif"),
        height=height,
        xaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            color=TEXT,
            showgrid=True,
            zeroline=False,
            linecolor="rgba(0,0,0,0.2)",
            ticks="outside",
            tickcolor="rgba(0,0,0,0.2)",
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0.1)",
            color=TEXT,
            showgrid=True,
            zeroline=True,
            zerolinecolor=C1, # Eixo zero em Laranja
            linecolor="rgba(0,0,0,0.2)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.8)",
            borderwidth=0,
            font=dict(size=10, color=TEXT, family="Inclusive Sans, Arial, sans-serif"),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        hoverlabel=dict(
            bgcolor=CARD,
            bordercolor=C1,
            font=dict(color=TEXT, size=12, family="Inclusive Sans, Arial, sans-serif"),
        ),
        hovermode="x unified",
        margin=dict(l=12, r=12, t=42 if title else 18, b=12),
    )

    if title:
        layout["title"] = dict(text=title, font=dict(size=12, color=TEXT), x=0)

    return layout


def rgb(hex_cor):
    h = hex_cor.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def grafico_linha(labels, series, height=280):
    fig = go.Figure()

    for nome, vals, cor in series:
        r, g, b = rgb(cor)
        y = [float(v) if pd.notna(v) else None for v in vals]

        fig.add_trace(go.Scatter(
            x=labels,
            y=y,
            name=str(nome),
            mode="lines+markers",
            line=dict(color=cor, width=3, shape="spline", smoothing=0.95),
            marker=dict(size=7, color=CARD, line=dict(width=2, color=cor)),
            connectgaps=False,
            fill="tozeroy" if len(series) == 1 else "none",
            fillcolor=f"rgba({r},{g},{b},0.14)",
            hovertemplate="%{y:,.0f}<extra>" + str(nome) + "</extra>",
        ))

    fig.update_layout(**layout_base(height=height))

    if len(series) <= 1:
        fig.update_layout(showlegend=False)

    return fig


def grafico_barras(labels, valores, height=260, horizontal=False):
    vals = [float(v) if pd.notna(v) else 0 for v in valores]
    cores = [C2 if v >= 0 else C1 for v in vals]

    if horizontal:
        fig = go.Figure(go.Bar(
            y=labels,
            x=vals,
            orientation="h",
            marker=dict(color=cores, line=dict(width=0)),
            hovertemplate="%{x:,.0f}<extra></extra>",
        ))
    else:
        fig = go.Figure(go.Bar(
            x=labels,
            y=vals,
            marker=dict(color=cores, line=dict(width=0)),
            hovertemplate="%{y:,.0f}<extra></extra>",
        ))

    lay = layout_base(height=height)
    lay["showlegend"] = False
    lay["bargap"] = 0.34

    fig.update_layout(**lay)
    fig.update_traces(opacity=0.95)

    try:
        fig.update_traces(marker_cornerradius=6)
    except Exception:
        pass

    return fig


def serie_mensal(df, grupo, coluna_grupo, coluna_valor):
    sub = df[df[coluna_grupo] == grupo].groupby("mes")[coluna_valor].sum(min_count=1)
    return [sub.get(m, None) for m in MESES_FULL]


df_emp, df_cad, df_flx = carregar_dados()

# Iframe do cabeçalho também com fundo cinza
components.html(
    f"""
<!doctype html>
<html>
<head>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inclusive+Sans:ital,wght@0,300..700;1,300..700&display=swap" rel="stylesheet">
  <style>
    * {{
      box-sizing: border-box;
      font-family: "Inclusive Sans", Arial, sans-serif;
    }}
    body {{
      margin: 0;
      background-color: {BG}; /* Fundo Cinza no Header também */
    }}
    .hero {{
      min-height: 118px;
      width: 100%;
      border-radius: 16px;
      padding: 22px 30px;
      display: flex;
      align-items: center;
      gap: 24px;
      background: {BG};
      border-bottom: 4px solid {C1}; /* Detalhe Laranja */
    }}
    .logo {{
      width: 132px;
      height: 82px;
      flex: 0 0 132px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .logo img {{
      max-width: 132px;
      max-height: 82px;
      object-fit: contain;
      mix-blend-mode: multiply;
      filter: contrast(1.08) saturate(1.05);
    }}
    .copy {{
      min-width: 0;
      flex: 1 1 auto;
    }}
    .title {{
      color: {TEXT};
      font-size: 26px;
      font-weight: 800;
      line-height: 1.16;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin-top: 8px;
      color: {TEXT};
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
    }}
    .source {{
      flex: 0 0 auto;
      border-radius: 8px;
      border: 2px solid {C1}; /* Borda Laranja */
      background: transparent;
      color: {TEXT};
      font-weight: bold;
      padding: 8px 14px;
      font-size: 12px;
      white-space: nowrap;
    }}
  </style>
</head>
<body>
  <section class="hero">
    <div class="logo">
      <img src="{LOGO_URL}" alt="Logo Observatório de Turismo">
    </div>
    <div class="copy">
      <div class="title">OBSERVATÓRIO DE TURISMO · UFPR</div>
      <div class="subtitle">Sistema de Inteligência Turística do Paraná · SITU / SETU</div>
    </div>
    <div class="source">Fonte: SITU / SETU · 2023-2026</div>
  </section>
</body>
</html>
""",
    height=130,
)

aba1, aba2, aba3 = st.tabs(["📊 Empregabilidade", "🏨 Cadastur", "✈️ Fluxo Turístico"])


with aba1:
    st.markdown('<p class="fonte">Fonte: SITU / Secretaria de Estado do Turismo - SETU</p>', unsafe_allow_html=True)

    if df_emp.empty:
        st.warning("Não foi possível carregar os dados de empregabilidade.")
    else:
        anos_emp = sorted(df_emp["ano"].dropna().astype(int).unique().tolist())
        setores_emp = sorted(df_emp["setor"].dropna().unique().tolist())

        f1, f2, f3 = st.columns(3)

        with f1:
            ano_e = st.selectbox("Ano", anos_emp, index=len(anos_emp) - 1, key="ae")

        with f2:
            setor_e = st.selectbox("Setor", ["Todos"] + setores_emp, key="se")

        with f3:
            mes_e = st.selectbox("Mês", ["Todos"] + MESES_FULL, key="me")

        dfe = df_emp[df_emp["ano"] == ano_e].copy()

        if setor_e != "Todos":
            dfe = dfe[dfe["setor"] == setor_e]

        if mes_e != "Todos":
            dfe = dfe[dfe["mes"] == mes_e]

        acum = df_emp[df_emp["ano"] == ano_e].groupby("setor")["saldo"].sum(min_count=1).dropna()
        saldo_total = dfe["saldo"].sum(skipna=True)
        melhor = acum.idxmax() if not acum.empty else "—"

        st.markdown("---")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Saldo Total do Período", formata_int(saldo_total))
        k2.metric("Setores Positivos", int((acum > 0).sum()))
        k3.metric("Setores em Retração", int((acum <= 0).sum()))
        k4.metric("Setor Destaque", str(melhor).split()[0] if melhor != "—" else "—")

        st.markdown("---")

        st.markdown('<div class="sec-title">Evolução Mensal por Setor</div>', unsafe_allow_html=True)

        dfe_ano = df_emp[df_emp["ano"] == ano_e].copy()
        setores_plot = setores_emp if setor_e == "Todos" else [setor_e]

        series_e = [
            (setor, serie_mensal(dfe_ano, setor, "setor", "saldo"), PALETA[i % len(PALETA)])
            for i, setor in enumerate(setores_plot)
        ]

        st.plotly_chart(grafico_linha(MESES_ABR, series_e, height=300), use_container_width=True)

        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown('<div class="sec-title">Saldo Acumulado por Setor</div>', unsafe_allow_html=True)
            acum2 = acum.sort_values().reset_index()
            st.plotly_chart(
                grafico_barras([str(s)[:22] for s in acum2["setor"]], acum2["saldo"], height=280, horizontal=True),
                use_container_width=True,
            )

        with c2:
            st.markdown('<div class="sec-title">Comparativo Anual</div>', unsafe_allow_html=True)
            anual = df_emp.groupby("ano")["saldo"].sum(min_count=1).dropna().reset_index().sort_values("ano")
            st.plotly_chart(
                grafico_linha(anual["ano"].astype(str).tolist(), [("Saldo Total", anual["saldo"].tolist(), C3)], height=280),
                use_container_width=True,
            )

        with c3:
            st.markdown('<div class="sec-title">Total Mensal</div>', unsafe_allow_html=True)
            mensal = dfe_ano.groupby("mes")["saldo"].sum(min_count=1).reindex(MESES_FULL)
            st.plotly_chart(
                grafico_barras(MESES_ABR, mensal.tolist(), height=280),
                use_container_width=True
            )


with aba2:
    st.markdown('<p class="fonte">Fonte: Cadastro de Prestadores de Serviços Turísticos - MTur</p>', unsafe_allow_html=True)

    if df_cad.empty:
        st.warning("Não foi possível carregar os dados do Cadastur.")
    else:
        anos_cad = sorted(df_cad["ano"].dropna().astype(int).unique().tolist())
        cats_cad = sorted(df_cad["categoria"].dropna().unique().tolist())

        f1, f2 = st.columns(2)

        with f1:
            ano_c = st.selectbox("Ano", anos_cad, index=len(anos_cad) - 1, key="ac")

        with f2:
            cat_c = st.selectbox("Categoria", ["Todos"] + cats_cad, key="cc")

        dfc = df_cad[df_cad["ano"] == ano_c].copy()

        if cat_c != "Todos":
            dfc = dfc[dfc["categoria"] == cat_c]

        total_mes = dfc.groupby("mes")["quantidade"].sum(min_count=1).reindex(MESES_FULL)
        total_v = total_mes.dropna()

        st.markdown("---")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Cadastros (pico)", formata_int(total_v.max() if not total_v.empty else pd.NA))
        k2.metric("Média Mensal", formata_int(total_v.mean() if not total_v.empty else pd.NA))
        k3.metric("Mês de Maior Cadastro", total_v.idxmax() if not total_v.empty else "—")
        k4.metric("Categorias Ativas", len(cats_cad))

        st.markdown("---")

        st.markdown('<div class="sec-title">Evolução Total de Cadastros</div>', unsafe_allow_html=True)

        st.plotly_chart(
            grafico_linha(MESES_ABR, [("Total", total_mes.tolist(), C3)], height=260),
            use_container_width=True
        )

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="sec-title">Por Categoria</div>', unsafe_allow_html=True)
            base_cats = df_cad[df_cad["ano"] == ano_c].copy()
            cats_plot = cats_cad if cat_c == "Todos" else [cat_c]
            series_c = [
                (cat, serie_mensal(base_cats, cat, "categoria", "quantidade"), PALETA[i % len(PALETA)])
                for i, cat in enumerate(cats_plot)
            ]
            st.plotly_chart(grafico_linha(MESES_ABR, series_c, height=280), use_container_width=True)

        with c2:
            st.markdown('<div class="sec-title">Comparativo Anual</div>', unsafe_allow_html=True)
            series_ac = []
            for i, ano in enumerate(anos_cad):
                base_ano = df_cad[df_cad["ano"] == ano]
                vals = base_ano.groupby("mes")["quantidade"].sum(min_count=1).reindex(MESES_FULL).tolist()
                series_ac.append((str(ano), vals, PALETA[i % len(PALETA)]))
            st.plotly_chart(grafico_linha(MESES_ABR, series_ac, height=280), use_container_width=True)

        st.markdown('<div class="sec-title">Ranking por Categoria (último valor disponível)</div>', unsafe_allow_html=True)
        rank = df_cad[df_cad["ano"] == ano_c].dropna(subset=["quantidade"]).sort_values(["categoria", "mes"], key=lambda s: s.map(ORDEM_MES) if s.name == "mes" else s).groupby("categoria")["quantidade"].last().sort_values()
        st.plotly_chart(
            grafico_barras(rank.index.tolist(), rank.values.tolist(), horizontal=True, height=300),
            use_container_width=True
        )


with aba3:
    st.markdown('<p class="fonte">Fonte: ICMBio / Serra Verde Express / Itaipu / Parque Vila Velha</p>', unsafe_allow_html=True)

    if df_flx.empty:
        st.warning("Não foi possível carregar os dados de fluxo turístico.")
    else:
        atrativos = sorted(df_flx["atrativo"].dropna().unique().tolist())
        anos_flx = sorted(df_flx["ano"].dropna().astype(int).unique().tolist())

        f1, f2, f3 = st.columns(3)

        with f1:
            atrativo_f = st.selectbox("Atrativo", atrativos, key="atf")

        with f2:
            ano_f = st.selectbox("Ano", anos_flx, index=len(anos_flx) - 1, key="anf")

        dff_at = df_flx[(df_flx["atrativo"] == atrativo_f) & (df_flx["ano"] == ano_f)].copy()
        indicadores = sorted(dff_at.dropna(subset=["valor"])["indicador"].dropna().unique().tolist())

        with f3:
            ind_f = st.selectbox("Indicador", ["Todos"] + indicadores, key="inf")

        dff = dff_at if ind_f == "Todos" else dff_at[dff_at["indicador"] == ind_f]
        total_f = dff["valor"].sum(skipna=True)

        st.markdown("---")

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total do Período", formata_int(total_f if total_f else pd.NA))
        k2.metric("Atrativo", atrativo_f)
        k3.metric("Ano", str(ano_f))
        k4.metric("Indicadores Numéricos", len(indicadores))

        st.markdown("---")

        st.markdown(f'<div class="sec-title">Evolução Mensal - {atrativo_f}</div>', unsafe_allow_html=True)

        inds_plot = indicadores if ind_f == "Todos" else [ind_f]
        series_f = [
            (ind, serie_mensal(dff_at, ind, "indicador", "valor"), PALETA[i % len(PALETA)])
            for i, ind in enumerate(inds_plot[:8])
        ]

        if series_f:
            st.plotly_chart(grafico_linha(MESES_ABR, series_f, height=320), use_container_width=True)
        else:
            st.info("Não há indicador numérico para visualizar nesse filtro.")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="sec-title">Comparativo por Ano</div>', unsafe_allow_html=True)
            if inds_plot:
                ind_comp = inds_plot[0]
                series_anos = []
                for i, ano in enumerate(anos_flx):
                    base = df_flx[(df_flx["atrativo"] == atrativo_f) & (df_flx["ano"] == ano) & (df_flx["indicador"] == ind_comp)]
                    vals = base.groupby("mes")["valor"].sum(min_count=1).reindex(MESES_FULL).tolist()
                    series_anos.append((str(ano), vals, PALETA[i % len(PALETA)]))
                st.plotly_chart(grafico_linha(MESES_ABR, series_anos, height=280), use_container_width=True)

        with c2:
            st.markdown('<div class="sec-title">Total por Indicador</div>', unsafe_allow_html=True)
            rank_f = dff_at.dropna(subset=["valor"]).groupby("indicador")["valor"].sum().sort_values()
            if not rank_f.empty:
                st.plotly_chart(
                    grafico_barras([str(s)[:26] for s in rank_f.index], rank_f.values, horizontal=True, height=280),
                    use_container_width=True,
                )

st.markdown("---")

st.markdown(
    f'<p style="text-align:center;font-size:10px;font-weight:bold;color:{TEXT};letter-spacing:0.04em">'
    f'OBSERVATÓRIO DE TURISMO · UFPR · Fonte: SITU / SETU / ICMBio · 2023-2026</p>',
    unsafe_allow_html=True,
)
