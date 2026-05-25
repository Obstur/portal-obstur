"""


OBSERVATORIO DE TURISMO - UFPR
Painel unico | Empregabilidade | Cadastur | Fluxo Turistico

Le dados publicados em CSV no Google Sheets.
"""

import re
import unicodedata

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="Observatorio de Turismo - UFPR",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# URLs recebidas. A ordem real dos links e:
# 1) Cadastur, 2) Empregabilidade, 3) Fluxo Turistico.
URL_CAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQIJaja_RfMVmdabkhm5QyvK6aREnFF267pobuKIZ5BTLaymAb03Fc3N_ofkHaGL8UJIZz-UeWx6Sj5/pub?output=csv"
URL_EMP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqGPUme21AUn8I9-rhiW-fyWOIAU03Rp48B7bB1oywwZWXZWjaYpFqgXDa9XBIjfa7Roh4cI-sPx4i/pub?output=csv"
URL_FLX = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJm-ju6hjisM-TzBsOv1g--vyh_sKd8g_TP8IH50211oZSPyJPVT8P24UFUFvtm9gkqZugsg98nbez/pub?output=csv"


# Paleta
C1 = "#2b8ab6"
C2 = "#20729b"
C3 = "#155a81"
C4 = "#0b4166"
C5 = "#00294c"
NEG = "#d9534f"
BG = "#e9f2f9"
BG2 = "#d6e8f4"
CARD = "#c8dff0"
BORDER = "#a8c8e0"
TEXT = "#0b3a5a"
MUTED = "#4a7a9b"
PALETA = [C1, C2, C3, "#5dade2", "#85c1e9", "#2e86c1", "#1a5276", "#154360", "#72b6d8", "#4f9ec9"]

MESES_ABR = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
MESES_FULL = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]
ORDEM_MES = {m: i for i, m in enumerate(MESES_FULL)}


st.markdown(
    f"""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {{
    background-color: {BG} !important;
    color: {TEXT} !important;
}}
[data-testid="stHeader"], [data-testid="stToolbar"] {{
    background-color: {BG} !important;
}}
.block-container {{
    padding: 0 2rem 2rem 2rem !important;
    max-width: 1400px;
}}
section[data-testid="stSidebar"] {{
    display: none !important;
}}
.stTabs [data-baseweb="tab-list"] {{
    background: {BG2} !important;
    border-bottom: 2px solid {C3};
    gap: 4px;
    padding: 0 8px;
    border-radius: 10px 10px 0 0;
}}
.stTabs [data-baseweb="tab"] {{
    color: {MUTED} !important;
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 1px;
    padding: 10px 22px;
    background: transparent !important;
}}
.stTabs [aria-selected="true"] {{
    color: {C1} !important;
    border-bottom: 3px solid {C1} !important;
    background: transparent !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
    background: {BG} !important;
    padding-top: 1.5rem;
}}
div[data-testid="metric-container"] {{
    background: {CARD} !important;
    border: 1px solid {BORDER} !important;
    border-top: 3px solid {C2} !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
}}
div[data-testid="metric-container"] label {{
    color: {MUTED} !important;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: {C1} !important;
    font-size: 22px !important;
    font-weight: 700 !important;
}}
.sec-title {{
    font-size: 10px;
    color: {MUTED};
    text-transform: uppercase;
    letter-spacing: 2px;
    border-bottom: 1px solid {BORDER};
    padding-bottom: 6px;
    margin: 16px 0 12px;
}}
.fonte {{
    font-size: 9px;
    color: {MUTED};
    font-style: italic;
    margin-bottom: 8px;
}}
hr {{
    border-color: {BORDER} !important;
}}
.app-hero {{
    background: linear-gradient(135deg, {C4}, {C5});
    padding: 24px 28px 22px 28px;
    border-radius: 0 0 16px 16px;
    border-bottom: 3px solid {C1};
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 18px 0 24px 0;
    min-height: 92px;
    overflow: visible;
    box-sizing: border-box;
}}
div[style*="linear-gradient(135deg"] {{
    padding: 26px 28px 22px 28px !important;
    margin-top: 18px !important;
    min-height: 96px !important;
    overflow: visible !important;
    box-sizing: border-box !important;
    align-items: center !important;
    flex-wrap: wrap !important;
}}
div[style*="linear-gradient(135deg"] > span {{
    line-height: 1 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: 42px !important;
    min-height: 42px !important;
}}
div[style*="linear-gradient(135deg"] > div {{
    min-width: 0 !important;
}}
div[style*="linear-gradient(135deg"] > div:last-child {{
    flex-shrink: 0 !important;
}}
.app-hero-icon {{
    width: 42px;
    height: 42px;
    min-width: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.24);
    font-size: 24px;
    line-height: 1;
}}
.app-hero-copy {{
    min-width: 0;
    flex: 1 1 auto;
}}
.app-hero-title {{
    color: white;
    font-size: 19px;
    font-weight: 700;
    letter-spacing: 1px;
    line-height: 1.28;
    white-space: normal;
    overflow-wrap: anywhere;
}}
.app-hero-subtitle {{
    color: #a8d4ea;
    font-size: 10px;
    letter-spacing: 2px;
    text-transform: uppercase;
    line-height: 1.45;
    margin-top: 6px;
    white-space: normal;
    overflow-wrap: anywhere;
}}
.app-hero-live {{
    flex: 0 0 auto;
    background: rgba(43, 138, 182, 0.2);
    border: 1px solid {C1};
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 10px;
    color: #a8d4ea;
    letter-spacing: 1px;
    line-height: 1;
    white-space: nowrap;
}}
@media (max-width: 760px) {{
    .block-container {{
        padding: 1.25rem 0.75rem 2rem 0.75rem !important;
    }}
    .app-hero {{
        align-items: flex-start;
        flex-wrap: wrap;
        padding: 22px 18px 20px 18px;
        margin-top: 16px;
        min-height: 118px;
    }}
    .app-hero-live {{
        margin-left: 58px;
    }}
}}
</style>
""",
    unsafe_allow_html=True,
)


def sem_acento(valor):
    texto = "" if pd.isna(valor) else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def normaliza_mes(valor):
    chave = sem_acento(valor).strip().lower()
    mapa = {
        "jan": "Janeiro",
        "janeiro": "Janeiro",
        "fev": "Fevereiro",
        "fevereiro": "Fevereiro",
        "mar": "Março",
        "marco": "Março",
        "abr": "Abril",
        "abril": "Abril",
        "mai": "Maio",
        "maio": "Maio",
        "jun": "Junho",
        "junho": "Junho",
        "jul": "Julho",
        "julho": "Julho",
        "ago": "Agosto",
        "agosto": "Agosto",
        "set": "Setembro",
        "setembro": "Setembro",
        "out": "Outubro",
        "outubro": "Outubro",
        "nov": "Novembro",
        "novembro": "Novembro",
        "dez": "Dezembro",
        "dezembro": "Dezembro",
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
        st.error(f"Erro ao carregar fluxo turistico: {exc}")
        flx = pd.DataFrame(columns=["ano", "mes", "atrativo", "indicador", "valor"])

    return emp, cad, flx


def layout_base(height=280, title=""):
    layout = dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG2,
        font=dict(color=TEXT, size=11),
        height=height,
        xaxis=dict(gridcolor=BORDER, color=MUTED, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=BORDER, color=MUTED, showgrid=True, zeroline=True, zerolinecolor=BORDER),
        legend=dict(bgcolor=BG2, bordercolor=BORDER, borderwidth=1, font=dict(size=10, color=TEXT)),
        hoverlabel=dict(bgcolor=CARD, bordercolor=C1, font=dict(color=TEXT)),
        margin=dict(l=10, r=10, t=36 if title else 10, b=10),
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
        fig.add_trace(
            go.Scatter(
                x=labels,
                y=y,
                name=str(nome),
                mode="lines+markers",
                line=dict(color=cor, width=2.5),
                marker=dict(size=6, color=cor),
                connectgaps=False,
                fill="tozeroy" if len(series) == 1 else "none",
                fillcolor=f"rgba({r},{g},{b},0.12)",
            )
        )
    fig.update_layout(**layout_base(height=height))
    return fig


def grafico_barras(labels, valores, height=260, horizontal=False):
    vals = [float(v) if pd.notna(v) else 0 for v in valores]
    cores = [C2 if v >= 0 else NEG for v in vals]

    if horizontal:
        fig = go.Figure(go.Bar(y=labels, x=vals, orientation="h", marker_color=cores, marker_line_width=0))
    else:
        fig = go.Figure(go.Bar(x=labels, y=vals, marker_color=cores, marker_line_width=0))

    lay = layout_base(height=height)
    lay["showlegend"] = False
    fig.update_layout(**lay)
    return fig


def serie_mensal(df, grupo, coluna_grupo, coluna_valor):
    sub = df[df[coluna_grupo] == grupo].groupby("mes")[coluna_valor].sum(min_count=1)
    return [sub.get(m, None) for m in MESES_FULL]


def valores_validos(df, coluna):
    return pd.to_numeric(df[coluna], errors="coerce").dropna()


df_emp, df_cad, df_flx = carregar_dados()


st.markdown(
    f"""
<div style="background:linear-gradient(135deg,{C4},{C5});padding:18px 28px;
border-radius:0 0 16px 16px;border-bottom:3px solid {C1};
display:flex;align-items:center;gap:16px;margin-bottom:24px;">
  <span style="font-size:30px">🧭</span>
  <div>
    <div style="color:white;font-size:19px;font-weight:700;letter-spacing:1px;">
      OBSERVATORIO DE TURISMO · UFPR
    </div>
    <div style="color:#a8d4ea;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-top:3px;">
      Sistema de Inteligencia Turistica do Parana · SITU / SETU
    </div>
  </div>
  <div style="margin-left:auto;font-size:9px;color:#a8d4ea;letter-spacing:1px;">
    Fonte: SITU / SETU · 2023-2026
  </div>
</div>
""",
    unsafe_allow_html=True,
)


aba1, aba2, aba3 = st.tabs(["📊 Empregabilidade", "🏨 Cadastur", "✈️ Fluxo Turistico"])


with aba1:
    st.markdown('<p class="fonte">Fonte: SITU / Secretaria de Estado do Turismo - SETU</p>', unsafe_allow_html=True)

    if df_emp.empty:
        st.warning("Nao foi possivel carregar os dados de empregabilidade.")
    else:
        anos_emp = sorted(df_emp["ano"].dropna().astype(int).unique().tolist())
        setores_emp = sorted(df_emp["setor"].dropna().unique().tolist())

        f1, f2, f3 = st.columns(3)
        with f1:
            ano_e = st.selectbox("Ano", anos_emp, index=len(anos_emp) - 1, key="ae")
        with f2:
            setor_e = st.selectbox("Setor", ["Todos"] + setores_emp, key="se")
        with f3:
            mes_e = st.selectbox("Mes", ["Todos"] + MESES_FULL, key="me")

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
        k1.metric("Saldo Total do Periodo", formata_int(saldo_total))
        k2.metric("Setores Positivos", int((acum > 0).sum()))
        k3.metric("Setores em Retracao", int((acum <= 0).sum()))
        k4.metric("Setor Destaque", str(melhor).split()[0] if melhor != "—" else "—")
        st.markdown("---")

        st.markdown('<div class="sec-title">Evolucao Mensal por Setor</div>', unsafe_allow_html=True)
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
                grafico_linha(anual["ano"].astype(str).tolist(), [("Saldo Total", anual["saldo"].tolist(), C1)], height=280),
                use_container_width=True,
            )

        with c3:
            st.markdown('<div class="sec-title">Total Mensal</div>', unsafe_allow_html=True)
            mensal = dfe_ano.groupby("mes")["saldo"].sum(min_count=1).reindex(MESES_FULL)
            st.plotly_chart(grafico_barras(MESES_ABR, mensal.tolist(), height=280), use_container_width=True)


with aba2:
    st.markdown('<p class="fonte">Fonte: Cadastro de Prestadores de Servicos Turisticos - MTur</p>', unsafe_allow_html=True)

    if df_cad.empty:
        st.warning("Nao foi possivel carregar os dados do Cadastur.")
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
        k2.metric("Media Mensal", formata_int(total_v.mean() if not total_v.empty else pd.NA))
        k3.metric("Mes de Maior Cadastro", total_v.idxmax() if not total_v.empty else "—")
        k4.metric("Categorias Ativas", len(cats_cad))
        st.markdown("---")

        st.markdown('<div class="sec-title">Evolucao Total de Cadastros</div>', unsafe_allow_html=True)
        st.plotly_chart(grafico_linha(MESES_ABR, [("Total", total_mes.tolist(), C1)], height=260), use_container_width=True)

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

        st.markdown('<div class="sec-title">Ranking por Categoria (ultimo valor disponivel)</div>', unsafe_allow_html=True)
        rank = (
            df_cad[df_cad["ano"] == ano_c]
            .dropna(subset=["quantidade"])
            .sort_values(["categoria", "mes"], key=lambda s: s.map(ORDEM_MES) if s.name == "mes" else s)
            .groupby("categoria")["quantidade"]
            .last()
            .sort_values()
        )
        st.plotly_chart(grafico_barras(rank.index.tolist(), rank.values.tolist(), horizontal=True, height=300), use_container_width=True)


with aba3:
    st.markdown('<p class="fonte">Fonte: ICMBio / Serra Verde Express / Itaipu / Parque Vila Velha</p>', unsafe_allow_html=True)

    if df_flx.empty:
        st.warning("Nao foi possivel carregar os dados de fluxo turistico.")
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
        k1.metric("Total do Periodo", formata_int(total_f if total_f else pd.NA))
        k2.metric("Atrativo", atrativo_f)
        k3.metric("Ano", str(ano_f))
        k4.metric("Indicadores Numericos", len(indicadores))
        st.markdown("---")

        st.markdown(f'<div class="sec-title">Evolucao Mensal - {atrativo_f}</div>', unsafe_allow_html=True)
        inds_plot = indicadores if ind_f == "Todos" else [ind_f]
        series_f = [
            (ind, serie_mensal(dff_at, ind, "indicador", "valor"), PALETA[i % len(PALETA)])
            for i, ind in enumerate(inds_plot[:8])
        ]

        if series_f:
            st.plotly_chart(grafico_linha(MESES_ABR, series_f, height=320), use_container_width=True)
        else:
            st.info("Nao ha indicador numerico para visualizar nesse filtro.")

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="sec-title">Comparativo por Ano</div>', unsafe_allow_html=True)
            if inds_plot:
                ind_comp = inds_plot[0]
                series_anos = []
                for i, ano in enumerate(anos_flx):
                    base = df_flx[
                        (df_flx["atrativo"] == atrativo_f)
                        & (df_flx["ano"] == ano)
                        & (df_flx["indicador"] == ind_comp)
                    ]
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
    f'<p style="text-align:center;font-size:9px;color:{MUTED};letter-spacing:1px">'
    f'OBSERVATORIO DE TURISMO · UFPR · Fonte: SITU / SETU / ICMBio · 2023-2026</p>',
    unsafe_allow_html=True,
)
