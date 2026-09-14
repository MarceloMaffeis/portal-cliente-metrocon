# -*- coding: utf-8 -*-
import streamlit as st
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.connection import init_db, execute_query, execute_one
from database.seed import run_seed
from modules.auth import render_login_screen, logout_user, record_lgpd_consent
from modules.dashboard import render_dashboard
from modules.documents import render_documents
from modules.daily_log import render_daily_log
from modules.schedule import render_schedule
from modules.meetings import render_meetings
from modules.messages import render_messages
from modules.admin_management import render_admin_management
from modules.lgpd_compliance import render_lgpd_compliance
from utils.ui_components import render_header, render_footer, COMPANY_NAME, COMPANY_CNPJ, COMPANY_CREA

st.set_page_config(
    page_title="Portal do Cliente | Metrocon Engenharia",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()
run_seed()

if 'user' not in st.session_state:
    st.session_state.user = None
if 'selected_project_id' not in st.session_state:
    st.session_state.selected_project_id = None

if not st.session_state.user:
    render_login_screen()
    st.stop()

user = st.session_state.user

if not user.get('lgpd_consent_date'):
    st.warning("🔒 **Termo de Consentimento e Privacidade (LGPD):**")
    st.markdown("""
    Para prosseguir no portal da **Metrocon Engenharia**, é necessário concordar com nossa Política de Privacidade e o armazenamento seguro de seus dados de contato e documentos.
    """)
    if st.button("✅ Li e Concordo com os Termos da LGPD", use_container_width=True):
        record_lgpd_consent(user['id'])
        st.rerun()
    st.stop()

if user['role'] == 'client':
    user_projects = execute_query('SELECT * FROM projects WHERE client_id = ? ORDER BY id DESC', (user['id'],))
else:
    user_projects = execute_query('SELECT * FROM projects ORDER BY id DESC')

if not user_projects:
    st.warning("⚠️ Você não possui projetos atribuídos no momento. Entre em contato com a administração.")
    if st.button("Sair"):
        logout_user()
    st.stop()

if st.session_state.selected_project_id is None or not any(p['id'] == st.session_state.selected_project_id for p in user_projects):
    st.session_state.selected_project_id = user_projects[0]['id']

current_project = next((dict(p) for p in user_projects if p['id'] == st.session_state.selected_project_id), dict(user_projects[0]))

with st.sidebar:
    st.html(f"""
    <div style="text-align: center; padding-bottom: 10px; border-bottom: 1px solid #E2E8F0; margin-bottom: 12px;">
        <h3 style="margin: 0; color: #0F2D59; font-size: 1.25rem;">🏢 METROCON</h3>
        <span style="font-size: 0.72rem; color: #E65100; font-weight: 700; text-transform: uppercase;">Engenharia e Construções</span>
        <div style="font-size: 0.7rem; color: #64748B; margin-top: 2px;">CNPJ: {COMPANY_CNPJ}</div>
    </div>
    """)

    st.markdown("**📍 Selecione o Projeto / Obra:**")
    proj_options = {p['id']: f"{'🏛️' if p['type'] == 'administrativo' else ('🔨' if p['type'] == 'reforma' else '🏗️')} {p['title']}" for p in user_projects}
    
    selected_pid = st.selectbox(
        "Projeto Ativo",
        options=list(proj_options.keys()),
        format_func=lambda x: proj_options[x],
        index=list(proj_options.keys()).index(current_project['id']),
        label_visibility="collapsed"
    )

    if selected_pid != st.session_state.selected_project_id:
        st.session_state.selected_project_id = selected_pid
        st.rerun()

    current_project = next((dict(p) for p in user_projects if p['id'] == st.session_state.selected_project_id), current_project)

    st.markdown("---")

    unread_count = execute_one(
        'SELECT COUNT(*) as c FROM messages WHERE project_id = ? AND recipient_id = ? AND is_read = 0',
        (current_project['id'], user['id'])
    )['c']
    msg_label = f"💬 Central de Mensagens ({unread_count})" if unread_count > 0 else "💬 Central de Mensagens"

    nav_options = [
        "📊 Painel Geral (Dashboard)",
        "📁 Central de Documentos",
        f"{'🏛️ Diário de Processo (RDP)' if current_project['type'] == 'administrativo' else '🏗️ Diário de Obra (RDO)'}",
        "📅 Cronograma & Gantt",
        "📝 Atas de Reunião",
        msg_label,
        "🛡️ LGPD & Privacidade"
    ]

    if user['role'] in ('admin', 'engineer'):
        nav_options.append("⚙️ Gestão Administrativa")

    st.markdown("**🧭 Navegação:**")
    selected_tab = st.radio(
        "Navegação do Portal",
        options=nav_options,
        label_visibility="collapsed"
    )

    st.markdown("---")

    st.html(f"""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 10px; font-size: 0.82rem;">
        <div style="font-weight: 700; color: #0F2D59;">👤 {user['name']}</div>
        <div style="color: #64748B;">{user['email']}</div>
        <div style="color: #475569; margin-top: 4px;"><strong>Perfil:</strong> {user['role'].upper()}</div>
        <div style="color: #475569;"><strong>Entidade:</strong> {user['company'] or 'N/A'}</div>
    </div>
    """)

    if st.button("🚪 Sair do Portal (Logout)", use_container_width=True):
        logout_user()

render_header(current_project, user)

if "Dashboard" in selected_tab:
    render_dashboard(current_project, user)
elif "Central de Documentos" in selected_tab:
    render_documents(current_project, user)
elif "Diário" in selected_tab:
    render_daily_log(current_project, user)
elif "Cronograma" in selected_tab:
    render_schedule(current_project, user)
elif "Atas de Reunião" in selected_tab:
    render_meetings(current_project, user)
elif "Mensagens" in selected_tab:
    render_messages(current_project, user)
elif "LGPD" in selected_tab:
    render_lgpd_compliance(user)
elif "Gestão Administrativa" in selected_tab:
    render_admin_management(user)

render_footer()
