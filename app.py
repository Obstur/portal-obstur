"""
OBSERVATÓRIO DE TURISMO — UFPR
Painel único | Empregabilidade · Cadastur · Fluxo PNI
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Observatório de Turismo · UFPR",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── PALETA ────────────────────────────────────────────────────────────────────
C1 = "#2b8ab6"
C2 = "#20729b"
C3 = "#155a81"
C4 = "#0b4166"
C5 = "#00294c"
BG = "#2c2c2c"
BG2 = "#383838"
CARD = "#3a3a3a"
BORDER = "#4a4a4a"
TEXT = "#f0f0f0"
MUTED = "#a0a0a0"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    html, body, .stApp {{ background-color: {BG} !important; color: {TEXT}; }}
    .block-container {{ padding: 0 2rem 2rem 2rem; max-width: 1400px; }}
    section[data-testid="stSidebar"] {{ display: none; }}

    /* HEADER */
    .obs-header {{
        background: linear-gradient(135deg, {C4}, {C5});
        padding: 18px 28px; border-radius: 0 0 16px 16px;
        border-bottom: 3px solid {C1};
        display: flex; align-items: center; gap: 16px;
        margin-bottom: 24px;
    }}
    .obs-header h1 {{ color: white; font-size: 18px; font-weight: 700; letter-spacing: 1px; margin: 0; }}
    .obs-header p  {{ color: #a8d4ea; font-size: 10px; margin: 3px 0 0; letter-spacing: 2px; text-transform: uppercase; }}
    .obs-badge {{
        margin-left: auto; background: rgba(43,138,182,0.2);
        border: 1px solid {C1}; padding: 4px 14px;
        border-radius: 20px; font-size: 10px; color: {C1}; letter-spacing: 1px;
    }}

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {{ background: {BG2}; border-bottom: 1px solid {BORDER}; gap: 4px; padding: 0 8px; border-radius: 10px 10px 0 0; }}
    .stTabs [data-baseweb="tab"] {{ color: {MUTED}; font-weight: 600; font-size: 12px; letter-spacing: 1px; padding: 10px 22px; }}
    .stTabs [aria-selected="true"] {{ color: {C1} !important; border-bottom: 2px solid {C1} !important; background: transparent !important; }}
    .stTabs [data-baseweb="tab-panel"] {{ background: {BG}; padding-top: 1.5rem; }}

    /* METRICS */
    div[data-testid="metric-container"] {{
        background: {CARD}; border: 1px solid {BORDER};
        border-top: 3px solid {C2}; border-radius: 12px; padding: 14px 16px;
    }}
    div[data-testid="metric-container"] label {{ color: {MUTED} !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1px; }}
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {{ color: {C1}; font-size: 22px; font-weight: 700; }}
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{ color: #5dade2; }}

    /* SELECTS */
    .stSelectbox label {{ color: {MUTED} !important; font-size: 10px !important; text-transform: uppercase; letter-spacing: 1px; }}
    .stSelectbox > div > div {{ background: {BG2} !important; border-color: {BORDER} !important; color: {TEXT} !important; border-radius: 8px !important; }}

    /* FILTER BAR */
    .filter-bar {{
        background: {BG2}; border: 1px solid {BORDER}; border-radius: 12px;
        padding: 12px 20px; margin-bottom: 20px;
    }}
    .filter-title {{ font-size: 10px; color: {MUTED}; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }}

    /* SECTION */
    .sec-title {{
        font-size: 10px; color: {MUTED}; text-transform: uppercase;
        letter-spacing: 2px; border-bottom: 1px solid {BORDER};
        padding-bottom: 6px; margin: 20px 0 14px;
    }}
    .fonte {{ font-size: 9px; color: {MUTED}; font-style: italic; margin-top: 4px; }}

    hr {{ border-color: {BORDER}; }}
</style>
""", unsafe_allow_html=True)

# ── DADOS ─────────────────────────────────────────────────────────────────────
MESES     = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
             "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
MESES_ABR = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

# LINK GOOGLE SHEETS (substitua pela URL CSV do seu arquivo organizado)
URL_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTSuFcr1bsidcqW5XAF5Mp29d1ymk8n3jatA8k6ipLACByBpvEAq9qkevYmtQlLoKQzfnGzNu9ZTwao/pub?output=csv"

EMP_SETORES = [
    "Serviços de Alimentação","Alojamento","Transporte rodoviário",
    "Agências e Operadoras","Aluguel de Automóveis","Atividades Culturais",
    "Transporte aéreo","Transporte ferroviário","Transporte aquaviário",
    "Ativ. desportivas e recreativas"
]
EMP = {
    2023: {"Serviços de Alimentação":[24,944,561,592,246,652,589,583,665,471,494,-1412],"Alojamento":[14,126,164,44,-117,174,139,153,166,170,173,191],"Transporte rodoviário":[-8,189,32,162,-26,99,-5,101,108,22,185,-181],"Agências e Operadoras":[2,36,55,53,59,23,9,51,37,23,26,-11],"Aluguel de Automóveis":[-1,-9,41,18,40,13,23,26,49,56,89,-69],"Atividades Culturais":[1,44,8,14,9,9,8,4,6,2,15,-31],"Transporte aéreo":[0,5,41,4,20,8,-7,2,-5,26,12,0],"Transporte ferroviário":[0,2,0,0,0,2,0,-1,2,0,0,0],"Transporte aquaviário":[0,-5,1,0,-20,-2,4,21,2,1,-11,-5],"Ativ. desportivas e recreativas":[6,108,-2,53,-6,-14,-5,46,24,73,24,-141]},
    2024: {"Serviços de Alimentação":[-186,953,232,610,509,276,411,509,397,276,502,None],"Alojamento":[-20,164,111,44,164,-36,-21,164,53,94,176,None],"Transporte rodoviário":[-109,278,21,83,-8,52,74,-8,43,29,184,None],"Agências e Operadoras":[13,18,22,10,47,10,4,47,5,4,26,None],"Aluguel de Automóveis":[3,-1,114,34,52,-6,26,52,40,53,89,None],"Atividades Culturais":[1,37,48,-3,3,38,2,3,15,129,15,None],"Transporte aéreo":[7,0,0,4,5,5,5,5,-1,22,12,None],"Transporte ferroviário":[1,-1,-1,-1,-3,0,0,-3,2,-1,0,None],"Transporte aquaviário":[-1,7,5,-17,3,6,5,3,-17,0,-11,None],"Ativ. desportivas e recreativas":[0,130,209,96,93,-28,-11,93,80,-9,23,None]},
    2025: {"Serviços de Alimentação":[-308,388,-153,965,-135,172,843,542,633,678,515,-1562],"Alojamento":[-48,202,-91,62,-36,27,109,-23,197,119,113,-34],"Transporte rodoviário":[-93,5,-31,136,-69,18,-22,69,64,55,24,-180],"Agências e Operadoras":[13,27,-1,-11,-10,14,25,17,41,-34,-2,-33],"Aluguel de Automóveis":[-17,5,29,3,-7,-1,31,50,30,19,24,-23],"Atividades Culturais":[-2,54,114,3,3,-10,-6,1,-3,6,134,-42],"Transporte aéreo":[19,7,4,27,2,7,16,15,-2,20,-2,-8],"Transporte ferroviário":[None]*12,"Transporte aquaviário":[-13,-17,10,23,-1,-2,18,8,2,10,2,-2],"Ativ. desportivas e recreativas":[-19,210,118,99,187,47,-112,114,105,3,112,-296]},
    2026: {"Serviços de Alimentação":[-338,324,172,None,None,None,None,None,None,None,None,None],"Alojamento":[18,123,39,None,None,None,None,None,None,None,None,None],"Transporte rodoviário":[-160,495,36,None,None,None,None,None,None,None,None,None],"Agências e Operadoras":[24,-8,-9,None,None,None,None,None,None,None,None,None],"Aluguel de Automóveis":[16,80,10,None,None,None,None,None,None,None,None,None],"Atividades Culturais":[9,24,-3,None,None,None,None,None,None,None,None,None],"Transporte aéreo":[-5,-1,1,None,None,None,None,None,None,None,None,None],"Transporte ferroviário":[None]*12,"Transporte aquaviário":[7,-3,None,None,None,None,None,None,None,None,None,None],"Ativ. desportivas e recreativas":[-33,135,113,None,None,None,None,None,None,None,None,None]},
}

CAD = {
    2023: {"AGÊNCIA":[1965,1982,1982,2082,2133,2186,2215,2270,2336,2369,2445,2503],"MEIOS DE HOSPEDAGEM":[688,672,672,702,743,760,765,778,768,772,771,773],"ORGANIZADORA DE EVENTOS":[478,470,470,473,475,474,482,501,522,527,542,543],"TRANSPORTADORA TURÍSTICA":[1059,1053,1053,1071,1112,1134,1161,1206,1280,1320,1387,1441],"RESTAURANTES":[1523,1481,1481,1398,1415,1427,1433,1440,1502,1509,1509,1596],"LOCADORA DE VEÍCULOS":[121,121,121,124,122,121,122,126,125,124,127,128],"Total":[6259,6185,6185,6221,6367,6459,6534,6679,6892,7173,7128,7335]},
    2024: {"AGÊNCIA":[1030,1077,1056,1077,1136,1149,1192,1216,1251,1284,1309,1323],"MEIOS DE HOSPEDAGEM":[116,115,114,155,112,119,121,124,121,122,120,120],"ORGANIZADORA DE EVENTOS":[137,139,138,139,169,176,179,185,195,207,211,214],"TRANSPORTADORA TURÍSTICA":[164,170,174,170,183,179,184,181,184,191,194,196],"RESTAURANTES":[435,452,458,452,450,457,476,481,492,500,512,514],"LOCADORA DE VEÍCULOS":[30,31,27,31,30,34,32,33,34,34,37,37],"GUIA DE TURISMO":[452,451,448,451,457,454,459,470,484,485,480,478],"Total":[2644,2724,2683,2724,2813,2848,2925,2966,3046,3122,3162,3182]},
    2025: {"AGÊNCIA":[1380,1410,1445,1417,1458,1490,1489,1509,1540,1580,1590,1591],"MEIOS DE HOSPEDAGEM":[120,121,122,118,116,113,113,112,110,109,108,104],"ORGANIZADORA DE EVENTOS":[219,225,227,208,205,205,197,195,195,194,195,195],"TRANSPORTADORA TURÍSTICA":[200,201,203,191,188,186,185,176,180,184,180,181],"RESTAURANTES":[522,531,539,486,487,476,469,466,455,446,442,438],"LOCADORA DE VEÍCULOS":[39,38,39,33,34,35,34,32,33,34,32,32],"GUIA DE TURISMO":[544,555,565,560,572,578,594,592,565,538,542,545],"Total":[3271,3329,3393,3237,3277,3288,3280,3279,3310,3344,3345,3339]},
    2026: {"AGÊNCIA":[1615,1613,1662,1678,None,None,None,None,None,None,None,None],"MEIOS DE HOSPEDAGEM":[106,114,117,122,None,None,None,None,None,None,None,None],"ORGANIZADORA DE EVENTOS":[202,201,208,197,None,None,None,None,None,None,None,None],"TRANSPORTADORA TURÍSTICA":[183,180,179,178,None,None,None,None,None,None,None,None],"RESTAURANTES":[438,429,429,396,None,None,None,None,None,None,None,None],"LOCADORA DE VEÍCULOS":[34,33,33,29,None,None,None,None,None,None,None,None],"GUIA DE TURISMO":[553,561,559,566,None,None,None,None,None,None,None,None],"Total":[3378,3371,3433,3408,None,None,None,None,None,None,None,None]},
}

FLX = {
    2025: {
        "Total Internacional":[234376,135458,166819,160695,136888,112182,219216,155780,157727,181065,199353,198980],
        "Total Nacional":     [137793,49319,77513,85287,78563,64665,124604,79659,83650,103250,119248,128412],
    },
    2026: {
        "Total Internacional":[252803,169009,None,None,None,None,None,None,None,None,None,None],
        "Total Nacional":     [163648,85294,None,None,None,None,None,None,None,None,None,None],
    }
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
PALETA = [C1, C2, C3, "#5dade2", "#85c1e9", "#aed6f1", "#d6eaf8"]

def fig_base():
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG2,
        font=dict(color=TEXT, size=11),
        xaxis=dict(gridcolor=BORDER, color=MUTED, showgrid=True),
        yaxis=dict(gridcolor=BORDER, color=MUTED, showgrid=True),
        margin=dict(l=10, r=10, t=36, b=10),
        legend=dict(bgcolor=BG2, bordercolor=BORDER, borderwidth=1, font=dict(size=10)),
        hoverlabel=dict(bgcolor=CARD, bordercolor=C1, font=dict(color=TEXT)),
    )

def linha(x, datasets, titulo="", height=280):
    fig = go.Figure()
    for i, (nome, vals, cor) in enumerate(datasets):
        fig.add_trace(go.Scatter(
            x=x, y=vals, name=nome,
            mode="lines+markers",
            line=dict(color=cor, width=2.5),
            marker=dict(size=6, color=cor),
            connectgaps=False,
            fill="tozeroy" if len(datasets)==1 else "none",
            fillcolor=cor+"22",
        ))
    layout = fig_base()
    layout["title"] = dict(text=titulo, font=dict(size=12, color=TEXT), x=0)
    layout["height"] = height
    fig.update_layout(**layout)
    return fig

def barras(x, y, titulo="", cor=C1, height=260, horizontal=False):
    cores = [C2 if v is None or v >= 0 else "#e74c3c" for v in y]
    if horizontal:
        fig = go.Figure(go.Bar(y=x, x=y, orientation="h", marker_color=cores, marker_line_width=0))
    else:
        fig = go.Figure(go.Bar(x=x, y=y, marker_color=cores, marker_line_width=0))
    layout = fig_base()
    layout["title"] = dict(text=titulo, font=dict(size=12, color=TEXT), x=0)
    layout["height"] = height
    layout["showlegend"] = False
    fig.update_layout(**layout)
    fig.update_traces(marker=dict(cornerradius=4))
    return fig

def get_emp_df(ano, setor="Todos"):
    dados = EMP.get(ano, {})
    rows = []
    setores = EMP_SETORES if setor == "Todos" else [setor]
    for s in setores:
        for m, v in enumerate(dados.get(s, [None]*12)):
            rows.append({"mes": m, "mes_nome": MESES[m], "mes_abr": MESES_ABR[m], "setor": s, "saldo": v})
    return pd.DataFrame(rows)

def get_cad_df(ano, cat="Total"):
    dados = CAD.get(ano, {})
    rows = []
    key = cat if cat != "Total" else "Total"
    cats = [k for k in dados if k != "Total"] if cat == "Todos" else [cat]
    for c in cats:
        for m, v in enumerate(dados.get(c, [None]*12)):
            rows.append({"mes": m, "mes_abr": MESES_ABR[m], "categoria": c, "valor": v})
    return pd.DataFrame(rows)

# ── HEADER ────────────────────────────────────────────────────────────────────
try:
    from PIL import Image
    logo = Image.open("logo.jpg")
    col_logo, col_title = st.columns([1, 11])
    with col_logo:
        st.image(logo, width=70)
    with col_title:
        st.markdown(f"""
        <div style="padding:8px 0">
            <h1 style="color:{C1};font-size:20px;font-weight:700;letter-spacing:1px;margin:0">
                OBSERVATÓRIO DE TURISMO · UFPR
            </h1>
            <p style="color:{MUTED};font-size:10px;letter-spacing:2px;text-transform:uppercase;margin:4px 0 0">
                Sistema de Inteligência Turística do Paraná · SITU / SETU
            </p>
        </div>
        """, unsafe_allow_html=True)
except:
    st.markdown(f"""
    <div class="obs-header">
        <span style="font-size:28px">🧭</span>
        <div>
            <h1>OBSERVATÓRIO DE TURISMO · UFPR</h1>
            <p>Sistema de Inteligência Turística do Paraná · SITU / SETU</p>
        </div>
        <div class="obs-badge">● AO VIVO</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── ABAS ──────────────────────────────────────────────────────────────────────
aba1, aba2, aba3 = st.tabs(["📊  Empregabilidade", "🏨  Cadastur", "✈️  Fluxo — PNI"])

# ═══════════════════════════════════════════════════════
# ABA 1 — EMPREGABILIDADE
# ═══════════════════════════════════════════════════════
with aba1:
    st.markdown('<p class="fonte">Fonte: SITU / Secretaria de Estado do Turismo — SETU</p>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)
    with f1: ano_e = st.selectbox("Ano", [2023,2024,2025,2026], index=2, key="ae")
    with f2: setor_e = st.selectbox("Setor", ["Todos"] + EMP_SETORES, key="se")
    with f3: mes_e = st.selectbox("Mês", ["Todos"] + MESES, key="me")

    df_e = get_emp_df(ano_e, setor_e)
    if mes_e != "Todos":
        df_e = df_e[df_e["mes_nome"] == mes_e]

    saldo_total = df_e["saldo"].dropna().sum()
    pos = (df_e.groupby("setor")["saldo"].sum() > 0).sum()
    neg = (df_e.groupby("setor")["saldo"].sum() <= 0).sum()
    melhor = df_e.groupby("setor")["saldo"].sum().idxmax() if not df_e.empty else "—"

    st.markdown("---")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Saldo Total do Período", f"{int(saldo_total):,}".replace(",","."))
    k2.metric("Setores com Saldo ✅", int(pos))
    k3.metric("Setores em Retração ⚠️", int(neg))
    k4.metric("Setor Destaque", melhor.split()[0] if melhor != "—" else "—")
    st.markdown("---")

    # Gráfico principal — linhas por setor
    st.markdown('<div class="sec-title">Evolução Mensal por Setor</div>', unsafe_allow_html=True)
    setores_plot = EMP_SETORES if setor_e == "Todos" else [setor_e]
    datasets = []
    for i, s in enumerate(setores_plot):
        vals = EMP[ano_e].get(s, [None]*12)
        datasets.append((s, vals, PALETA[i % len(PALETA)]))
    st.plotly_chart(linha(MESES_ABR, datasets, height=300), use_container_width=True)

    # Linha 2
    c1, c2, c3 = st.columns(3)
    with c1:
        acum = {s: sum(v for v in EMP[ano_e].get(s,[]) if v is not None) for s in EMP_SETORES}
        st.plotly_chart(barras(
            [s[:18] for s in acum], list(acum.values()),
            "Saldo Acumulado por Setor", height=260, horizontal=True
        ), use_container_width=True)

    with c2:
        anos_vals = [sum(v for s in EMP_SETORES for v in EMP.get(a,{}).get(s,[]) if v is not None) for a in [2023,2024,2025,2026]]
        st.plotly_chart(linha(
            ["2023","2024","2025","2026"],
            [("Saldo Total", anos_vals, C1)],
            "Comparativo Anual", height=260
        ), use_container_width=True)

    with c3:
        total_mes = [sum(v for s in EMP_SETORES for v in [EMP[ano_e].get(s,[None]*12)[m]] if v is not None) for m in range(12)]
        st.plotly_chart(barras(MESES_ABR, total_mes, "Total Mensal", height=260), use_container_width=True)

# ═══════════════════════════════════════════════════════
# ABA 2 — CADASTUR
# ═══════════════════════════════════════════════════════
with aba2:
    st.markdown('<p class="fonte">Fonte: Cadastro de Prestadores de Serviços Turísticos — MTur</p>', unsafe_allow_html=True)

    cats_disponiveis = list({k for a in CAD for k in CAD[a] if k != "Total"})
    f1, f2 = st.columns(2)
    with f1: ano_c = st.selectbox("Ano", [2023,2024,2025,2026], index=2, key="ac")
    with f2: cat_c = st.selectbox("Categoria", ["Todos"] + sorted(cats_disponiveis), key="cc")

    total_c = CAD[ano_c].get("Total", [None]*12)
    total_valido = [v for v in total_c if v is not None]
    media_c = int(sum(total_valido)/len(total_valido)) if total_valido else 0
    pico_mes = MESES[total_c.index(max(total_valido))] if total_valido else "—"
    cats_ano = [k for k in CAD[ano_c] if k != "Total"]

    st.markdown("---")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Cadastros (pico)", f"{max(total_valido):,}".replace(",",".") if total_valido else "—")
    k2.metric("Média Mensal", f"{media_c:,}".replace(",","."))
    k3.metric("Mês de Maior Cadastro", pico_mes)
    k4.metric("Categorias Ativas", len(cats_ano))
    st.markdown("---")

    # Gráfico total mensal
    st.markdown('<div class="sec-title">Evolução do Total de Cadastros</div>', unsafe_allow_html=True)
    st.plotly_chart(linha(MESES_ABR, [("Total Cadastros", total_c, C1)], height=260), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">Por Categoria (mês a mês)</div>', unsafe_allow_html=True)
        cats_plot = cats_ano if cat_c == "Todos" else [cat_c]
        ds_cad = [(cat, CAD[ano_c].get(cat,[None]*12), PALETA[i%len(PALETA)]) for i, cat in enumerate(cats_plot)]
        st.plotly_chart(linha(MESES_ABR, ds_cad, height=280), use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">Comparativo Anual — Total</div>', unsafe_allow_html=True)
        anos_cad = []
        for a in [2023,2024,2025,2026]:
            t = CAD[a].get("Total",[None]*12)
            anos_cad.append((str(a), t, PALETA[[2023,2024,2025,2026].index(a)]))
        st.plotly_chart(linha(MESES_ABR, anos_cad, height=280), use_container_width=True)

    # Ranking por categoria
    st.markdown('<div class="sec-title">Ranking por Categoria (último mês disponível)</div>', unsafe_allow_html=True)
    rank_cats, rank_vals = [], []
    for cat in cats_ano:
        vals = [v for v in CAD[ano_c].get(cat,[]) if v is not None]
        if vals:
            rank_cats.append(cat)
            rank_vals.append(vals[-1])
    st.plotly_chart(barras(rank_cats, rank_vals, horizontal=True, height=280), use_container_width=True)

# ═══════════════════════════════════════════════════════
# ABA 3 — FLUXO PNI
# ═══════════════════════════════════════════════════════
with aba3:
    st.markdown('<p class="fonte">Fonte: Parque Nacional do Iguaçu / ICMBio</p>', unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1: ano_f = st.selectbox("Ano", [2025, 2026], key="af")
    with f2: origem_f = st.selectbox("Origem", ["Todos","Nacional","Internacional"], key="of")

    intl = FLX[ano_f]["Total Internacional"]
    nac  = FLX[ano_f]["Total Nacional"]
    total_f = [((i or 0)+(n or 0)) if (i is not None or n is not None) else None for i,n in zip(intl,nac)]

    intl_v = [v for v in intl if v is not None]
    nac_v  = [v for v in nac  if v is not None]

    st.markdown("---")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total de Visitantes", f"{sum(v for v in total_f if v):,}".replace(",","."))
    k2.metric("Visitantes Internacionais", f"{sum(intl_v):,}".replace(",","."))
    k3.metric("Visitantes Nacionais", f"{sum(nac_v):,}".replace(",","."))
    k4.metric("% Internacional", f"{sum(intl_v)/(sum(intl_v)+sum(nac_v))*100:.1f}%" if nac_v else "—")
    st.markdown("---")

    # Gráfico principal
    st.markdown('<div class="sec-title">Evolução Mensal de Visitantes</div>', unsafe_allow_html=True)
    if origem_f == "Todos":
        ds_flx = [("Internacional", intl, C1), ("Nacional", nac, C2)]
    elif origem_f == "Internacional":
        ds_flx = [("Internacional", intl, C1)]
    else:
        ds_flx = [("Nacional", nac, C2)]
    st.plotly_chart(linha(MESES_ABR, ds_flx, height=300), use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">Comparativo Nacional × Internacional</div>', unsafe_allow_html=True)
        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(name="Internacional", x=MESES_ABR, y=intl, marker_color=C1, marker_line_width=0))
        fig_comp.add_trace(go.Bar(name="Nacional", x=MESES_ABR, y=nac, marker_color=C3, marker_line_width=0))
        layout = fig_base()
        layout["barmode"] = "group"
        layout["height"] = 260
        layout["title"] = dict(text="", font=dict(size=12))
        fig_comp.update_layout(**layout)
        st.plotly_chart(fig_comp, use_container_width=True)

    with c2:
        st.markdown('<div class="sec-title">Comparativo 2025 × 2026</div>', unsafe_allow_html=True)
        ds_anos = [
            ("2025 — Internacional", FLX[2025]["Total Internacional"], C1),
            ("2026 — Internacional", FLX[2026]["Total Internacional"], C2),
        ]
        st.plotly_chart(linha(MESES_ABR, ds_anos, height=260), use_container_width=True)

    # Distribuição acumulada
    st.markdown('<div class="sec-title">Participação por Origem (acumulado)</div>', unsafe_allow_html=True)
    fig_pie = go.Figure(go.Pie(
        labels=["Internacional","Nacional"],
        values=[sum(intl_v), sum(nac_v)],
        marker_colors=[C1, C3],
        hole=0.55,
        textfont=dict(color=TEXT),
    ))
    fig_pie.update_layout(paper_bgcolor=BG, plot_bgcolor=BG, font=dict(color=TEXT), height=260,
                          legend=dict(bgcolor=BG2, bordercolor=BORDER, borderwidth=1),
                          margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.markdown(f'<p style="text-align:center;font-size:9px;color:{MUTED};letter-spacing:1px">OBSERVATÓRIO DE TURISMO · UFPR · Fonte: SITU / SETU / ICMBio · 2023–2026</p>', unsafe_allow_html=True)
