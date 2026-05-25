"""
OBSERVATÓRIO DE TURISMO — UFPR
Painel único | Empregabilidade · Cadastur · Fluxo Turístico
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Observatório de Turismo · UFPR",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── PALETA ────────────────────────────────────────────────────────────────────
C1="#2b8ab6"; C2="#20729b"; C3="#155a81"; C4="#0b4166"; C5="#00294c"
BG="#e9f2f9"; BG2="#d6e8f4"; CARD="#c8dff0"; BORDER="#a8c8e0"
TEXT="#0b3a5a"; MUTED="#4a7a9b"
PALETA=[C1,C2,C3,"#5dade2","#85c1e9","#aed6f1","#2e86c1","#1a5276","#154360","#d6eaf8"]

st.markdown(f"""
<style>
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"],.stApp{{
    background-color:{BG}!important;color:{TEXT}!important;}}
[data-testid="stHeader"],[data-testid="stToolbar"]{{background-color:{BG}!important;}}
.block-container{{padding:0 2rem 2rem 2rem!important;max-width:1400px;}}
section[data-testid="stSidebar"]{{display:none!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{BG2}!important;border-bottom:2px solid {C3};gap:4px;padding:0 8px;border-radius:10px 10px 0 0;}}
.stTabs [data-baseweb="tab"]{{color:{MUTED}!important;font-weight:600;font-size:13px;letter-spacing:1px;padding:10px 22px;background:transparent!important;}}
.stTabs [aria-selected="true"]{{color:{C1}!important;border-bottom:3px solid {C1}!important;background:transparent!important;}}
.stTabs [data-baseweb="tab-panel"]{{background:{BG}!important;padding-top:1.5rem;}}
div[data-testid="metric-container"]{{background:{CARD}!important;border:1px solid {BORDER}!important;border-top:3px solid {C2}!important;border-radius:12px!important;padding:14px 16px!important;}}
div[data-testid="metric-container"] label{{color:{MUTED}!important;font-size:10px!important;text-transform:uppercase;letter-spacing:1px;}}
div[data-testid="metric-container"] [data-testid="stMetricValue"]{{color:{C1}!important;font-size:22px!important;font-weight:700!important;}}
.stSelectbox label{{color:{MUTED}!important;font-size:10px!important;text-transform:uppercase;letter-spacing:1px;}}
.stSelectbox>div>div{{background:{BG2}!important;border-color:{BORDER}!important;color:{TEXT}!important;border-radius:8px!important;}}
.sec-title{{font-size:10px;color:{MUTED};text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid {BORDER};padding-bottom:6px;margin:16px 0 12px;}}
.fonte{{font-size:9px;color:{MUTED};font-style:italic;margin-bottom:8px;}}
hr{{border-color:{BORDER}!important;}}
</style>
""", unsafe_allow_html=True)

# ── URLS ──────────────────────────────────────────────────────────────────────
URL_EMP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQIJaja_RfMVmdabkhm5QyvK6aREnFF267pobuKIZ5BTLaymAb03Fc3N_ofkHaGL8UJIZz-UeWx6Sj5/pub?output=csv"
URL_CAD = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQqGPUme21AUn8I9-rhiW-fyWOIAU03Rp48B7bB1oywwZWXZWjaYpFqgXDa9XBIjfa7Roh4cI-sPx4i/pub?output=csv"
URL_FLX = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRJm-ju6hjisM-TzBsOv1g--vyh_sKd8g_TP8IH50211oZSPyJPVT8P24UFUFvtm9gkqZugsg98nbez/pub?output=csv"

MESES_ABR = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
MESES_FULL = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
ORDEM_MES = {m:i for i,m in enumerate(MESES_FULL)}

# ── CARREGAR DADOS ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_emp():
    try:
        df = pd.read_csv(URL_EMP)
        df.columns = df.columns.str.strip()
        df["saldo"] = pd.to_numeric(df["saldo"], errors="coerce")
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
        return df
    except:
        return pd.DataFrame(columns=["ano","mes","setor","saldo"])

@st.cache_data(ttl=3600)
def load_cad():
    try:
        df = pd.read_csv(URL_CAD)
        df.columns = df.columns.str.strip()
        df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
        return df
    except:
        return pd.DataFrame(columns=["ano","mes","categoria","quantidade"])

@st.cache_data(ttl=3600)
def load_flx():
    try:
        df = pd.read_csv(URL_FLX)
        df.columns = df.columns.str.strip()
        df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
        df["ano"] = pd.to_numeric(df["ano"], errors="coerce").astype("Int64")
        return df
    except:
        return pd.DataFrame(columns=["ano","mes","atrativo","indicador","valor"])

df_emp = load_emp()
df_cad = load_cad()
df_flx = load_flx()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def mes_idx(m):
    return ORDEM_MES.get(m, 99)

def layout_base(height=280, title=""):
    return dict(
        paper_bgcolor=BG, plot_bgcolor=BG2,
        font=dict(color=TEXT, size=11), height=height,
        title=dict(text=title, font=dict(size=12,color=TEXT), x=0) if title else None,
        xaxis=dict(gridcolor=BORDER, color=MUTED, showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=BORDER, color=MUTED, showgrid=True, zeroline=True, zerolinecolor=BORDER),
        legend=dict(bgcolor=BG2, bordercolor=BORDER, borderwidth=1, font=dict(size=10,color=TEXT)),
        hoverlabel=dict(bgcolor=CARD, bordercolor=C1, font=dict(color=TEXT)),
        margin=dict(l=10,r=10,t=36 if title else 10,b=10),
    )

def rgb(hex_cor):
    h = hex_cor.lstrip("#")
    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

def grafico_linha(labels, series, height=280):
    fig = go.Figure()
    for nome, vals, cor in series:
        r,g,b = rgb(cor)
        y = [float(v) if pd.notna(v) else None for v in vals]
        fig.add_trace(go.Scatter(
            x=labels, y=y, name=str(nome),
            mode="lines+markers",
            line=dict(color=cor, width=2.5),
            marker=dict(size=6, color=cor),
            connectgaps=False,
            fill="tozeroy" if len(series)==1 else "none",
            fillcolor=f"rgba({r},{g},{b},0.12)",
        ))
    fig.update_layout(**layout_base(height=height))
    return fig

def grafico_barras(labels, valores, height=260, horizontal=False):
    cores = [C2 if (pd.notna(v) and float(v)>=0) else "#e74c3c" for v in valores]
    y_vals = [float(v) if pd.notna(v) else 0 for v in valores]
    if horizontal:
        fig = go.Figure(go.Bar(y=labels, x=y_vals, orientation="h", marker_color=cores))
    else:
        fig = go.Figure(go.Bar(x=labels, y=y_vals, marker_color=cores))
    fig.update_traces(marker=dict(cornerradius=4))
    lay = layout_base(height=height)
    lay["showlegend"] = False
    fig.update_layout(**lay)
    return fig

def soma(serie): 
    return serie.dropna().sum()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,{C4},{C5});padding:18px 28px;
border-radius:0 0 16px 16px;border-bottom:3px solid {C1};
display:flex;align-items:center;gap:16px;margin-bottom:24px;">
  <span style="font-size:30px">🧭</span>
  <div>
    <div style="color:white;font-size:19px;font-weight:700;letter-spacing:1px;">
      OBSERVATÓRIO DE TURISMO · UFPR
    </div>
    <div style="color:#a8d4ea;font-size:10px;letter-spacing:2px;text-transform:uppercase;margin-top:3px;">
      Sistema de Inteligência Turística do Paraná · SITU / SETU
    </div>
  </div>
  <div style="margin-left:auto;font-size:9px;color:#a8d4ea;letter-spacing:1px;">
    Fonte: SITU / SETU · 2023–2026
  </div>
</div>
""", unsafe_allow_html=True)

# ── ABAS ──────────────────────────────────────────────────────────────────────
aba1, aba2, aba3 = st.tabs(["📊 Empregabilidade", "🏨 Cadastur", "✈️ Fluxo Turístico"])

# ═══════════════════════════════════════════════════════
# ABA 1 — EMPREGABILIDADE
# ═══════════════════════════════════════════════════════
with aba1:
    st.markdown('<p class="fonte">Fonte: SITU / Secretaria de Estado do Turismo — SETU</p>', unsafe_allow_html=True)
    
    anos_emp = sorted(df_emp["ano"].dropna().unique().tolist()) if not df_emp.empty else [2023,2024,2025,2026]
    setores_emp = sorted(df_emp["setor"].dropna().unique().tolist()) if not df_emp.empty else []
    
    f1,f2,f3 = st.columns(3)
    with f1: ano_e = st.selectbox("Ano", anos_emp, index=len(anos_emp)-1, key="ae")
    with f2: setor_e = st.selectbox("Setor", ["Todos"]+setores_emp, key="se")
    with f3: mes_e = st.selectbox("Mês", ["Todos"]+MESES_FULL, key="me")
    
    dfe = df_emp[df_emp["ano"]==ano_e].copy()
    if setor_e != "Todos": dfe = dfe[dfe["setor"]==setor_e]
    if mes_e != "Todos": dfe = dfe[dfe["mes"]==mes_e]
    
    saldo_total = soma(dfe["saldo"])
    acum = df_emp[df_emp["ano"]==ano_e].groupby("setor")["saldo"].sum()
    pos = (acum>0).sum(); neg = (acum<=0).sum()
    melhor = acum.idxmax() if not acum.empty else "—"
    
    st.markdown("---")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Saldo Total do Período", f"{int(saldo_total):,}".replace(",",".") if pd.notna(saldo_total) else "0")
    k2.metric("Setores Positivos ✅", int(pos))
    k3.metric("Setores em Retração ⚠️", int(neg))
    k4.metric("Setor Destaque", str(melhor).split()[0] if melhor != "—" else "—")
    
    st.markdown("---")
    st.markdown('<div class="sec-title">Evolução Mensal por Setor</div>', unsafe_allow_html=True)
    
    setores_plot = setores_emp if setor_e=="Todos" else [setor_e]
    dfe_ano = df_emp[df_emp["ano"]==ano_e].copy()
    
    if not dfe_ano.empty:
        dfe_ano["mes_idx"] = dfe_ano["mes"].map(mes_idx)
        dfe_ano = dfe_ano.sort_values("mes_idx")
        
        series_e = []
        for i, s in enumerate(setores_plot):
            sub = dfe_ano[dfe_ano["setor"] == s].groupby("mes")["saldo"].sum()
            vals = [sub.get(m, None) for m in MESES_FULL]
            series_e.append((s, vals, PALETA[i % len(PALETA)]))
        
        st.plotly_chart(grafico_linha(MESES_ABR, series_e, height=300), 
                        use_container_width=True, key="emp_evolucao_mensal")
    else:
        st.info("Sem dados disponíveis para o ano selecionado.")

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="sec-title">Saldo Acumulado por Setor</div>', unsafe_allow_html=True)
        acum2 = df_emp[df_emp["ano"]==ano_e].groupby("setor")["saldo"].sum().reset_index()
        if not acum2.empty:
            st.plotly_chart(grafico_barras([s[:16] for s in acum2["setor"]], acum2["saldo"].tolist(), 
                                           height=260, horizontal=True), 
                            use_container_width=True, key="emp_acumulado_setor")
        else:
            st.info("Sem dados acumulados.")

    with c2:
        st.markdown('<div class="sec-title">Comparativo Anual</div>', unsafe_allow_html=True)
        anual = df_emp.groupby("ano")["saldo"].sum().reset_index().sort_values("ano")
        if not anual.empty:
            st.plotly_chart(grafico_linha(anual["ano"].astype(str).tolist(), 
                                          [("Saldo Total", anual["saldo"].tolist(), C1)], height=260), 
                            use_container_width=True, key="emp_comparativo_anual")
        else:
            st.info("Sem dados para comparativo anual.")

    with c3:
        st.markdown('<div class="sec-title">Total Mensal</div>', unsafe_allow_html=True)
        mensal = dfe_ano.groupby("mes")["saldo"].sum().reindex(MESES_FULL, fill_value=0)
        st.plotly_chart(grafico_barras(MESES_ABR, mensal.tolist(), height=260), 
                        use_container_width=True, key="emp_total_mensal")

# ═══════════════════════════════════════════════════════
# ABA 2 — CADASTUR
# ═══════════════════════════════════════════════════════
with aba2:
    st.markdown('<p class="fonte">Fonte: Cadastro de Prestadores de Serviços Turísticos — MTur</p>', unsafe_allow_html=True)
    
    anos_cad = sorted(df_cad["ano"].dropna().unique().tolist()) if not df_cad.empty else []
    cats_cad = sorted(df_cad["categoria"].dropna().unique().tolist()) if not df_cad.empty else []
    
    f1,f2 = st.columns(2)
    with f1: ano_c = st.selectbox("Ano", anos_cad, index=len(anos_cad)-1 if anos_cad else 0, key="ac")
    with f2: cat_c = st.selectbox("Categoria", ["Todos"]+cats_cad, key="cc")
    
    dfc = df_cad[df_cad["ano"]==ano_c].copy()
    if not dfc.empty:
        dfc["mes_idx"] = dfc["mes"].map(mes_idx)
        dfc = dfc.sort_values("mes_idx")
    
    total_mes = dfc.groupby("mes")["quantidade"].sum().reindex(MESES_FULL, fill_value=0)
    total_v = total_mes.dropna()
    
    st.markdown("---")
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Cadastros (pico)", f"{int(total_v.max()):,}".replace(",",".") if not total_v.empty else "—")
    k2.metric("Média Mensal", f"{int(total_v.mean()):,}".replace(",",".") if not total_v.empty else "—")
    k3.metric("Mês de Maior Cadastro", total_v.idxmax() if not total_v.empty else "—")
    k4.metric("Categorias Ativas", len(cats_cad))
    
    st.markdown("---")
    st.markdown('<div class="sec-title">Evolução Total de Cadastros</div>', unsafe_allow_html=True)
    st.plotly_chart(grafico_linha(MESES_ABR, [("Total", total_mes.tolist(), C1)], height=240), 
                    use_container_width=True, key="cad_evolucao_total")
    
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">Por Categoria</div>', unsafe_allow_html=True)
        cats_plot = cats_cad if cat_c=="Todos" else [cat_c]
        series_c = []
        for i, cat in enumerate(cats_plot):
            sub = dfc[dfc["categoria"] == cat].groupby("mes")["quantidade"].sum()
            vals = [sub.get(m, None) for m in MESES_FULL]
            series_c.append((cat, vals, PALETA[i % len(PALETA)]))
        
        st.plotly_chart(grafico_linha(MESES_ABR, series_c, height=260), 
                        use_container_width=True, key="cad_por_categoria")
    
    with c2:
        st.markdown('<div class="sec-title">Comparativo Anual</div>', unsafe_allow_html=True)
        series_ac = []
        for i, a in enumerate(sorted(df_cad["ano"].dropna().unique())):
            valores = df_cad[df_cad["ano"]==a].groupby("mes")["quantidade"].sum().reindex(MESES_FULL, fill_value=0).tolist()
            series_ac.append((str(a), valores, PALETA[i % len(PALETA)]))
        
        st.plotly_chart(grafico_linha(MESES_ABR, series_ac, height=260), 
                        use_container_width=True, key="cad_comparativo_anual")
    
    st.markdown('<div class="sec-title">Ranking por Categoria (último valor disponível)</div>', unsafe_allow_html=True)
    rank = dfc.groupby("categoria")["quantidade"].last().sort_values(ascending=True)
    if not rank.empty:
        st.plotly_chart(grafico_barras(rank.index.tolist(), rank.values.tolist(), 
                                       horizontal=True, height=280), 
                        use_container_width=True, key="cad_ranking_categoria")
    else:
        st.info("Sem dados para ranking.")

# ═══════════════════════════════════════════════════════
# ABA 3 — FLUXO TURÍSTICO (mantida)
# ═══════════════════════════════════════════════════════
with aba3:
    st.markdown('<p class="fonte">Fonte: ICMBio / Serra Verde Express / Itaipu / Parque Vila Velha</p>', unsafe_allow_html=True)
    # ... (você pode colar aqui o conteúdo anterior da aba 3 se quiser)

st.markdown("---")
st.markdown(f'<p style="text-align:center;font-size:9px;color:{MUTED};letter-spacing:1px">'
            f'OBSERVATÓRIO DE TURISMO · UFPR · Fonte: SITU / SETU / ICMBio · 2023–2026</p>',
            unsafe_allow_html=True)
