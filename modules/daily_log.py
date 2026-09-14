# -*- coding: utf-8 -*-
import streamlit as st
import os
import datetime
from database.connection import execute_query, execute_one, execute_insert
from modules.auth import log_audit
from utils.security import sanitize_filename

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

def render_daily_log(project: dict, user: dict):
    is_admin_or_eng = user['role'] in ('admin', 'engineer')
    is_admin_proc = project['type'] == 'administrativo'

    title_label = "🏛️ Diário de Processo & Tramitações (RDP)" if is_admin_proc else "🏗️ Diário de Obra & Evolução Física (RDO)"
    st.subheader(title_label)
    st.caption("Acompanhamento transparente das atividades executadas, protocolos, registros fotográficos e ocorrências.")

    if is_admin_or_eng:
        with st.expander("➕ Publicar Novo Registro no Diário", expanded=False):
            with st.form("new_daily_log_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    log_date = st.date_input("Data do Registro*", value=datetime.date.today())
                    log_title = st.text_input("Título do Registro*", placeholder="ex: Concretagem da laje superior / Protocolo na Prefeitura")
                with c2:
                    if is_admin_proc:
                        weather_or_mode = st.selectbox("Modo de Tramitação", ["Digital (Portal SEI / VRE)", "Presencial em Órgão Público", "Reunião Técnica com Fiscal", "Vistoria no Imóvel"])
                        team_count = st.number_input("Técnicos Envolvidos", min_value=1, value=2, step=1)
                    else:
                        weather_or_mode = st.selectbox("Condições Climáticas", ["Ensolarado (Tempo Bom)", "Parcialmente Nublado", "Chuvoso / Impróprio para Concretagem", "Nublado e Firme"])
                        team_count = st.number_input("Efetivo em Canteiro (Operários/Técnicos)", min_value=0, value=12, step=1)

                log_desc = st.text_area("Descrição Geral dos Trabalhos*", placeholder="Descreva os serviços executados no dia...")
                highlights = st.text_area("Principais Atividades Executadas (em tópicos)", placeholder="- Item 1;\n- Item 2;\n- Item 3...")
                occurrences = st.text_input("Ocorrências / Desvios / Observações Técnicas", value="Nenhuma ocorrência prejudicial ao andamento dos serviços.")
                
                uploaded_photos = st.file_uploader("Fotos do Registro (JPG, PNG)", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

                submit_log = st.form_submit_button("Publicar Registro Oficial ➔", use_container_width=True)

                if submit_log:
                    if not log_title or not log_desc:
                        st.warning("⚠️ Preencha o título e a descrição dos trabalhos.")
                    else:
                        log_id = execute_insert(
                            '''INSERT INTO daily_logs (project_id, author_id, log_date, title, description, weather_conditions, team_count, highlight_activities, occurrences)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (project['id'], user['id'], log_date.strftime('%Y-%m-%d'), log_title, log_desc, weather_or_mode, team_count, highlights, occurrences)
                        )

                        if uploaded_photos:
                            os.makedirs(UPLOADS_DIR, exist_ok=True)
                            for idx, photo in enumerate(uploaded_photos):
                                safe_name = sanitize_filename(photo.name)
                                save_path = os.path.join(UPLOADS_DIR, f"log_{log_id}_{idx}_{safe_name}")
                                with open(save_path, 'wb') as f:
                                    f.write(photo.getbuffer())
                                execute_insert(
                                    '''INSERT INTO daily_log_photos (daily_log_id, file_path, file_name, caption)
                                    VALUES (?, ?, ?, ?)''',
                                    (log_id, save_path, safe_name, f"Foto {idx+1} - {log_title}")
                                )

                        log_audit(user['id'], user['name'], user['role'], 'DAILY_LOG_CREATE', 'daily_logs', str(log_id), f"Publicado diário: {log_title} ({log_date})")
                        st.success("✅ Registro publicado com sucesso no Diário!")
                        st.rerun()

    # Listagem dos Diários
    logs = execute_query(
        '''SELECT l.*, u.name as author_name, u.role as author_role 
        FROM daily_logs l 
        LEFT JOIN users u ON l.author_id = u.id 
        WHERE l.project_id = ? 
        ORDER BY l.log_date DESC, l.id DESC''',
        (project['id'],)
    )

    if not logs:
        st.info("Nenhum relatório diário publicado ainda para este projeto.")
        return

    for log in logs:
        with st.container():
            st.html(f"""
            <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-left: 5px solid #0F2D59; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.03);">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; border-bottom: 1px solid #F1F5F9; padding-bottom: 8px; margin-bottom: 10px;">
                    <div>
                        <strong style="color: #0F2D59; font-size: 1.15rem;">📅 {log['log_date']} • {log['title']}</strong>
                    </div>
                    <div style="font-size: 0.8rem; color: #64748B;">
                        Responsável: <strong>{log['author_name']}</strong> • ⛅ {log['weather_conditions']} • 👷 {log['team_count']} envolvidos
                    </div>
                </div>
                <div style="color: #1E293B; font-size: 0.92rem; line-height: 1.5; margin-bottom: 10px;">
                    {log['description']}
                </div>
            </div>
            """)

            if log['highlight_activities']:
                st.markdown(f"**📌 Atividades Executadas:**\n{log['highlight_activities']}")

            if log['occurrences']:
                st.caption(f"⚠️ **Observações / Ocorrências:** {log['occurrences']}")

            photos = execute_query('SELECT * FROM daily_log_photos WHERE daily_log_id = ?', (log['id'],))
            if photos:
                st.markdown("**📸 Galeria de Fotos do Registro:**")
                cols = st.columns(min(len(photos), 3))
                for idx, p in enumerate(photos):
                    with cols[idx % 3]:
                        if os.path.exists(p['file_path']):
                            st.image(p['file_path'], caption=p['caption'] or p['file_name'], use_container_width=True)
                        else:
                            st.caption(f"📷 [Foto: {p['file_name']}]")
            
            st.markdown("---")
