# -*- coding: utf-8 -*-
import streamlit as st
import datetime
from database.connection import execute_one, execute_query, execute_insert, execute_update
from utils.security import verify_password, hash_password
from utils.ui_components import COMPANY_NAME, COMPANY_CNPJ, COMPANY_CREA, COMPANY_PHONE, COMPANY_EMAIL

def log_audit(user_id: int, user_name: str, user_role: str, action: str, resource_type: str, resource_id: str, details: str):
    """Registra trilha de auditoria em conformidade com a LGPD."""
    try:
        execute_insert(
            '''INSERT INTO audit_logs (user_id, user_name, user_role, action, resource_type, resource_id, details, ip_or_session)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, user_name, user_role, action, resource_type, resource_id, details, "session_active")
        )
    except Exception as e:
        print(f"Erro ao registrar log de auditoria: {e}")

def login_user(email: str, password: str) -> bool:
    user = execute_one('SELECT * FROM users WHERE email = ? AND active = 1', (email.strip().lower(),))
    if not user:
        st.error("❌ E-mail ou senha incorretos.")
        return False
    
    if verify_password(password, user['password_hash'], user['salt']):
        st.session_state.user = dict(user)
        log_audit(user['id'], user['name'], user['role'], 'LOGIN', 'auth', 'user_session', f"Login realizado com sucesso ({user['email']})")
        return True
    else:
        st.error("❌ E-mail ou senha incorretos.")
        return False

def logout_user():
    if 'user' in st.session_state and st.session_state.user:
        u = st.session_state.user
        log_audit(u['id'], u['name'], u['role'], 'LOGOUT', 'auth', 'user_session', "Logout realizado pelo usuário")
    st.session_state.user = None
    st.session_state.selected_project_id = None
    st.rerun()

def record_lgpd_consent(user_id: int):
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    execute_update('UPDATE users SET lgpd_consent_date = ? WHERE id = ?', (now_str, user_id))
    st.session_state.user['lgpd_consent_date'] = now_str
    u = st.session_state.user
    log_audit(u['id'], u['name'], u['role'], 'LGPD_CONSENT', 'privacy_policy', 'terms_v1', "Aceite formal dos termos da LGPD registrado.")

def render_login_screen():
    st.html("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <div style="background: linear-gradient(135deg, #0A192F 0%, #172A46 50%, #0F2D59 100%); padding: 2rem; border-radius: 12px; color: white; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h1 style="margin: 0; font-size: 2rem; color: #FFFFFF;">🏢 METROCON ENGENHARIA</h1>
            <p style="margin: 6px 0 0 0; color: #E65100; font-weight: 700; font-size: 1.1rem; letter-spacing: 0.5px;">PORTAL DE RELACIONAMENTO & GESTÃO DO CLIENTE</p>
            <p style="margin: 6px 0 0 0; color: #CBD5E1; font-size: 0.85rem;">CNPJ: 07.427.908/0001-25 • CREA-SP 0742790-PJ</p>
            <p style="margin-top: 10px; font-size: 0.9rem; color: #E2E8F0;">Centralize obras, reformas, diários, cronogramas e processos administrativos em um único ambiente seguro.</p>
        </div>
    </div>
    """)

    col1, col2 = st.columns([1.1, 0.9], gap="large")

    with col1:
        st.subheader("🔐 Acesso Restrito e Seguro")
        st.markdown("Informe suas credenciais corporativas para acessar seus projetos:")

        with st.form("login_form"):
            email = st.text_input("E-mail cadastrado", placeholder="ex: cliente@email.com")
            password = st.text_input("Senha de acesso", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Entrar no Portal ➔", use_container_width=True)

            if submit:
                if not email or not password:
                    st.warning("⚠️ Preencha todos os campos.")
                else:
                    if login_user(email, password):
                        st.success("✅ Autenticado com sucesso!")
                        st.rerun()

        st.info("🔒 **Conformidade LGPD:** Suas informações e documentos são confidenciais e criptografados.")

    with col2:
        st.markdown("### ⚡ Acesso Rápido de Demonstração")
        st.caption("Selecione um perfil para testar as permissões e funcionalidades:")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("👑 Diretor Admin\n(Acesso Geral)", use_container_width=True):
                login_user('admin@metrocon.com.br', 'Admin@123456')
                st.rerun()

            if st.button("🏠 Dr. Roberto\n(Cliente - Obra Casa 42)", use_container_width=True):
                login_user('cliente.reserva@gmail.com', 'Cliente@123456')
                st.rerun()

        with c2:
            if st.button("👷 Eng. Carlos Eduardo\n(Responsável Técnico)", use_container_width=True):
                login_user('engenharia@metrocon.com.br', 'Eng@123456')
                st.rerun()

            if st.button("🏢 Dra. Juliana\n(Cliente - Proc. Administrativo)", use_container_width=True):
                login_user('diretoria@inovaempreendimentos.com.br', 'Cliente@123456')
                st.rerun()

        st.markdown("""
        ---
        **Contatos de Suporte Técnico:**  
        📞 (11) 3456-7800 / (11) 98765-4321  
        📧 contato@metrocon.com.br  
        🏢 Metrocon Engenharia e Construções Ltda
        """)
