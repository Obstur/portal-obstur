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
    k4.metric("Setor Destaque", str(melhor).split()[0] if melhor!="—" else "—")
    
    st.markdown("---")
    st.markdown('<div class="sec-title">Evolução Mensal por Setor</div>', unsafe_allow_html=True)
    
    setores_plot = setores_emp if setor_e=="Todos" else [setor_e]
    dfe_ano = df_emp[df_emp["ano"]==ano_e].copy()
    
    if not dfe_ano.empty:
        dfe_ano["mes_idx"] = dfe_ano["mes"].map(mes_idx)
        dfe_ano = dfe_ano.sort_values("mes_idx")
        
        series_e = []
        for i, s in enumerate(setores_plot):
            sub = dfe_ano[dfe_ano["setor"] == s].groupby("mes")["saldo"].sum()  # ← Mudança importante
            vals = [sub.get(m, None) for m in MESES_FULL]
            series_e.append((s, vals, PALETA[i % len(PALETA)]))
        
        st.plotly_chart(grafico_linha(MESES_ABR, series_e, height=300), 
                        use_container_width=True, 
                        key="emp_evolucao_mensal")
    else:
        st.info("Sem dados disponíveis para o ano selecionado.")

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown('<div class="sec-title">Saldo Acumulado por Setor</div>', unsafe_allow_html=True)
        acum2 = df_emp[df_emp["ano"]==ano_e].groupby("setor")["saldo"].sum().reset_index()
        if not acum2.empty:
            st.plotly_chart(grafico_barras([s[:16] for s in acum2["setor"]], 
                                           acum2["saldo"].tolist(), 
                                           height=260, horizontal=True), 
                            use_container_width=True, 
                            key="emp_acumulado_setor")
        else:
            st.info("Sem dados acumulados.")

    with c2:
        st.markdown('<div class="sec-title">Comparativo Anual</div>', unsafe_allow_html=True)
        anual = df_emp.groupby("ano")["saldo"].sum().reset_index().sort_values("ano")
        if not anual.empty:
            st.plotly_chart(grafico_linha(anual["ano"].astype(str).tolist(), 
                                          [("Saldo Total", anual["saldo"].tolist(), C1)], height=260), 
                            use_container_width=True, 
                            key="emp_comparativo_anual")
        else:
            st.info("Sem dados para comparativo anual.")

    with c3:
        st.markdown('<div class="sec-title">Total Mensal</div>', unsafe_allow_html=True)
        mensal = dfe_ano.groupby("mes")["saldo"].sum().reindex(MESES_FULL, fill_value=0)
        st.plotly_chart(grafico_barras(MESES_ABR, mensal.tolist(), height=260), 
                        use_container_width=True, 
                        key="emp_total_mensal")

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
                    use_container_width=True, 
                    key="cad_evolucao_total")
    
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="sec-title">Por Categoria</div>', unsafe_allow_html=True)
        cats_plot = cats_cad if cat_c=="Todos" else [cat_c]
        series_c = []
        for i, cat in enumerate(cats_plot):
            sub = dfc[dfc["categoria"] == cat].groupby("mes")["quantidade"].sum()  # ← Correção aqui
            vals = [sub.get(m, None) for m in MESES_FULL]
            series_c.append((cat, vals, PALETA[i % len(PALETA)]))
        
        st.plotly_chart(grafico_linha(MESES_ABR, series_c, height=260), 
                        use_container_width=True, 
                        key="cad_por_categoria")
    
    with c2:
        st.markdown('<div class="sec-title">Comparativo Anual</div>', unsafe_allow_html=True)
        series_ac = []
        for i, a in enumerate(sorted(df_cad["ano"].dropna().unique())):
            valores = df_cad[df_cad["ano"]==a].groupby("mes")["quantidade"].sum().reindex(MESES_FULL, fill_value=0).tolist()
            series_ac.append((str(a), valores, PALETA[i % len(PALETA)]))
        
        st.plotly_chart(grafico_linha(MESES_ABR, series_ac, height=260), 
                        use_container_width=True, 
                        key="cad_comparativo_anual")
    
    st.markdown('<div class="sec-title">Ranking por Categoria (último valor disponível)</div>', unsafe_allow_html=True)
    rank = dfc.groupby("categoria")["quantidade"].last().sort_values(ascending=True)
    if not rank.empty:
        st.plotly_chart(grafico_barras(rank.index.tolist(), rank.values.tolist(), 
                                       horizontal=True, height=280), 
                        use_container_width=True, 
                        key="cad_ranking_categoria")
    else:
        st.info("Sem dados para ranking.")
