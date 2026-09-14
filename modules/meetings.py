# -*- coding: utf-8 -*-
import streamlit as st
import datetime
from database.connection import execute_query, execute_one, execute_insert
from modules.auth import log_audit

def render_meetings(project: dict, user: dict):
    st.subheader("📝 Atas de Reunião & Alinhamentos Estratégicos")
    st.caption("Registro formal de decisões, participantes, pendências e histórico contratual dos alinhamentos.")

    can_create = user['role'] in ('admin', 'engineer')

    if can_create:
        with st.expander("➕ Registrar Nova Ata de Reunião", expanded=False):
            with st.form("new_meeting_form", clear_on_submit=True):
                mc1, mc2 = st.columns(2)
                with mc1:
                    m_title = st.text_input("Título da Reunião*", placeholder="ex: Ata de Alinhamento de Acabamentos e Prazos")
                    m_date = st.date_input("Data da Reunião*", value=datetime.date.today())
                with mc2:
                    m_time = st.text_input("Horário / Duração", value="15:00 às 16:30")
                    m_location = st.text_input("Local ou Link Virtual*", value="Canteiro de Obras / Virtual via Google Meet")

                m_participants = st.text_area("Participantes Presentes*", placeholder="ex: Dr. Roberto (Cliente), Eng. Carlos Eduardo (Metrocon)...")
                m_summary = st.text_area("Pauta e Resumo das Discussões*", placeholder="1. Pauta 1;\n2. Pauta 2...")
                m_decisions = st.text_area("Decisões e Acordos Estabelecidos*", placeholder="- Decisão 1;\n- Decisão 2...")
                m_actions = st.text_area("Pendências e Próximos Passos (Ação, Responsável e Prazo)", placeholder="- Metrocon: Enviar orçamento até 15/09;\n- Cliente: Aprovar amostra até 20/09.")

                btn_save_meeting = st.form_submit_button("Salvar e Publicar Ata Oficial ➔", use_container_width=True)

                if btn_save_meeting:
                    if not m_title or not m_summary or not m_decisions:
                        st.warning("⚠️ Preencha os campos obrigatórios da ata.")
                    else:
                        full_date_str = f"{m_date.strftime('%Y-%m-%d')} {m_time}"
                        meeting_id = execute_insert(
                            '''INSERT INTO meeting_minutes (project_id, title, meeting_date, location_or_link, participants, summary_topics, decisions, action_items)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (project['id'], m_title, full_date_str, m_location, m_participants, m_summary, m_decisions, m_actions)
                        )
                        log_audit(user['id'], user['name'], user['role'], 'MEETING_MINUTES_CREATE', 'meeting_minutes', str(meeting_id), f"Publicada ata de reunião: {m_title}")
                        st.success("✅ Ata de reunião registrada com sucesso!")
                        st.rerun()

    meetings = execute_query(
        '''SELECT * FROM meeting_minutes 
        WHERE project_id = ? 
        ORDER BY meeting_date DESC, id DESC''',
        (project['id'],)
    )

    if not meetings:
        st.info("Nenhuma ata de reunião cadastrada para este projeto.")
        return

    for m in meetings:
        with st.container():
            st.html(f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #E65100; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.2rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                    <div>
                        <h4 style="margin: 0; color: #0F2D59;">📋 {m['title']}</h4>
                        <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: #64748B;">
                            📅 <strong>Data/Horário:</strong> {m['meeting_date']} • 📍 <strong>Local:</strong> {m['location_or_link']}
                        </p>
                        <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: #475569;">
                            👥 <strong>Participantes:</strong> {m['participants']}
                        </p>
                    </div>
                </div>
            </div>
            """)

            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**📌 Pauta & Resumo:**")
                st.markdown(m['summary_topics'] or "Sem resumo detalhado.")

                st.markdown("**✅ Decisões Firmadas:**")
                st.markdown(m['decisions'] or "Sem decisões formais.")

            with col_b:
                st.markdown("**⏳ Pendências & Plano de Ação:**")
                if m['action_items']:
                    st.info(m['action_items'])
                else:
                    st.caption("Nenhuma pendência em aberto.")

            st.markdown("---")
