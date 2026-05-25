"""
OBSERVATÓRIO DE TURISMO — UFPR
Painel único | Empregabilidade · Cadastur · Fluxo de Turistas
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
BG = "#e9f2f9"
BG2 = "#d6e8f4"
CARD = "#c8dff0"
BORDER = "#a8c8e0"
TEXT = "#0b3a5a"
MUTED = "#4a7a9b"

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {{
        background-color: {BG} !important;
        color: {TEXT} !important;
    }}

    [data-testid="stHeader"] {{
        background-color: {BG} !important;
    }}

    [data-testid="stToolbar"] {{
        background-color: {BG} !important;
    }}

    .block-container {{
        padding: 1.25rem 2rem 2rem 2rem !important;
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

    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
        color: #5dade2 !important;
    }}

    .stSelectbox label {{
        color: {MUTED} !important;
        font-size: 10px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}

    .stSelectbox > div > div {{
        background: {BG2} !important;
        border-color: {BORDER} !important;
        color: {TEXT} !important;
        border-radius: 8px !important;
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

    .header-painel {{
        background: linear-gradient(135deg, {C4}, {C5});
        padding: 26px 28px 22px 28px;
        border-radius: 0 0 16px 16px;
        border-bottom: 3px solid {C1};
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 18px 0 24px 0;
        min-height: 96px;
        overflow: visible;
        box-sizing: border-box;
    }}

    .header-icon {{
        font-size: 30px;
        line-height: 1;
        min-width: 42px;
        min-height: 42px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .header-texto {{
        min-width: 0;
        flex: 1;
    }}

    .header-titulo {{
        color: white;
        font-size: 19px;
        font-weight: 700;
        letter-spacing: 1px;
        line-height: 1.25;
        white-space: normal;
    }}

    .header-subtitulo {{
        color: #a8d4ea;
        font-size: 10px;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-top: 6px;
        line-height: 1.4;
        white-space: normal;
    }}

    .header-live {{
        margin-left: auto;
        background: rgba(43, 138, 182, 0.2);
        border: 1px solid {C1};
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 10px;
        color: #a8d4ea;
        letter-spacing: 1px;
        white-space: nowrap;
    }}

    @media (max-width: 760px) {{
        .block-container {{
            padding: 1rem 0.75rem 2rem 0.75rem !important;
        }}

        .header-painel {{
            flex-wrap: wrap;
            align-items: flex-start;
            padding: 22px 18px 20px 18px;
            min-height: 118px;
        }}

        .header-live {{
            margin-left: 58px;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES ────────────────────────────────────────────────────────────────
MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

MESES_ABR = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]

PALETA = [
    C1, C2, C3, "#5dade2", "#85c1e9", "#aed6f1",
    "#2e86c1", "#1a5276", "#154360", "#d6eaf8"
]

EMP_SETORES = [
    "Serviços de Alimentação",
    "Alojamento",
    "Transporte rodoviário",
    "Agências e Operadoras",
    "Aluguel de Automóveis",
    "Atividades Culturais",
    "Transporte aéreo",
    "Transporte ferroviário",
    "Transporte aquaviário",
    "Ativ. desportivas e recreativas"
]

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-painel">
    <div class="header-icon">▣</div>

    <div class="header-texto">
        <div class="header-titulo">
            OBSERVATÓRIO DE TURISMO · UFPR
        </div>
        <div class="header-subtitulo">
            Sistema de Inteligência Turística do Paraná · SITU / SETU
        </div>
    </div>

    <div class="header-live">
        AO VIVO
    </div>
</div>
""", unsafe_allow_html=True)
