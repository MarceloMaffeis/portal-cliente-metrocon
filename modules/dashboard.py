# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import datetime
from database.connection import execute_one, execute_query
from utils.ui_components import render_status_pill, render_type_pill

def render_dashboard(project: dict, user: dict):
    st.subheader(f"📊 Painel de Controle • {project['title']}")
    
    # 1. Cards de Métricas Principais
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        prog = float(project['progress_percent'] or 0.0)
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Progresso Geral</div>
            <div class="metric-value">{prog:.1f}%</div>
            <div class="metric-sub">Físico-financeiro</div>
        </div>
        """)
        st.progress(prog / 100.0)

    with col2:
        status_pill_html = render_status_pill(project['status'])
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Status Atual</div>
            <div style="margin-top: 8px; margin-bottom: 6px;">{status_pill_html}</div>
            <div class="metric-sub">Serviço ativo</div>
        </div>
        """)

    with col3:
        st_date = project['start_date'] or "Não informada"
        end_date = project['end_date_estimated'] or "Não informada"
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Previsão de Entrega</div>
            <div class="metric-value" style="font-size: 1.15rem; color: #E65100;">📅 {end_date}</div>
            <div class="metric-sub">Início: {st_date}</div>
        </div>
        """)

    with col4:
        resp = project['responsible_name'] or "Metrocon Engenharia"
        cont = project['responsible_phone'] or "(11) 3456-7800"
        st.html(f"""
        <div class="metric-card">
            <div class="metric-label">Responsável Técnico</div>
            <div class="metric-value" style="font-size: 1.05rem; color: #0F2D59;">👷 {resp}</div>
            <div class="metric-sub">📞 {cont}</div>
        </div>
        """)

    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

    # 2. Informações Detalhadas do Projeto / Processo
    c_info1, c_info2 = st.columns([1.2, 0.8])

    with c_info1:
        st.markdown("### 📋 Ficha Técnica e Escopo do Serviço")
        
        info_items = [
            ("Categoria", project['category_label'] or "Construção Civil"),
            ("Tipo de Atendimento", "Processo Administrativo / Legalização" if project['type'] == 'administrativo' else ("Reforma Corporativa" if project['type'] == 'reforma' else "Obra Nova")),
            ("Localização / Órgão Competente", project['address_or_agency'] or "Não informado"),
            ("Número de Protocolo / Alvará", project['protocol_number'] or "Em tramitação"),
            ("Cliente Vinculado", execute_one('SELECT name, company FROM users WHERE id = ?', (project['client_id'],))['name'] if project['client_id'] else "Geral")
        ]

        for label, val in info_items:
            st.markdown(f"**{label}:** {val}")

        if project['technical_notes']:
            st.info(f"💡 **Nota da Engenharia Metrocon:** {project['technical_notes']}")

    with c_info2:
        st.markdown("### ⚡ Ações Rápidas")
        st.markdown("Acesse diretamente as ferramentas essenciais:")
        
        ca, cb = st.columns(2)
        with ca:
            st.metric("Total Documentos", execute_one('SELECT COUNT(*) as c FROM documents WHERE project_id = ?', (project['id'],))['c'])
            st.metric("Diários Postados", execute_one('SELECT COUNT(*) as c FROM daily_logs WHERE project_id = ?', (project['id'],))['c'])
        with cb:
            st.metric("Etapas no Cronograma", execute_one('SELECT COUNT(*) as c FROM schedule_stages WHERE project_id = ?', (project['id'],))['c'])
            st.metric("Atas de Reunião", execute_one('SELECT COUNT(*) as c FROM meeting_minutes WHERE project_id = ?', (project['id'],))['c'])

    st.markdown("---")

    # 3. Destaques das Últimas Atualizações
    st.markdown("### 🕒 Últimas Atualizações Realizadas")
    
    col_u1, col_u2 = st.columns(2)

    with col_u1:
        st.markdown("#### 📷 Último Diário (RDO / RDP)")
        last_log = execute_one('SELECT * FROM daily_logs WHERE project_id = ? ORDER BY log_date DESC LIMIT 1', (project['id'],))
        if last_log:
            st.markdown(f"**Data:** {last_log['log_date']} • **{last_log['title']}**")
            st.markdown(f"*{last_log['description'][:180]}...*")
            
            photo = execute_one('SELECT * FROM daily_log_photos WHERE daily_log_id = ? LIMIT 1', (last_log['id'],))
            if photo and photo['file_path']:
                try:
                    st.image(photo['file_path'], caption=photo['caption'] or "Foto do Registro", use_container_width=True)
                except Exception:
                    pass
        else:
            st.info("Nenhum diário registrado até o momento.")

    with col_u2:
        st.markdown("#### 📝 Última Ata & Alinhamentos")
        last_meeting = execute_one('SELECT * FROM meeting_minutes WHERE project_id = ? ORDER BY meeting_date DESC LIMIT 1', (project['id'],))
        if last_meeting:
            st.markdown(f"**Data:** {last_meeting['meeting_date']} • **{last_meeting['title']}**")
            st.markdown(f"**Participantes:** {last_meeting['participants']}")
            st.markdown(f"**Decisões:**\n{last_meeting['decisions']}")
        else:
            st.info("Nenhuma ata de reunião registrada para este projeto.")

        st.markdown("#### 📄 Documento Recente")
        last_doc = execute_one('SELECT * FROM documents WHERE project_id = ? ORDER BY uploaded_at DESC LIMIT 1', (project['id'],))
        if last_doc:
            st.markdown(f"**{last_doc['title']}** (v{last_doc['version']}) • Categoria: `{last_doc['category'].upper()}`")
            st.caption(f"Inserido em: {last_doc['uploaded_at']} • Tamanho: {last_doc['file_size_kb']} KB")
        else:
            st.info("Nenhum documento anexado ainda.")
