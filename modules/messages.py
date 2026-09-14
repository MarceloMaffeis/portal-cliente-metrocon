# -*- coding: utf-8 -*-
import streamlit as st
import os
import datetime
from database.connection import execute_query, execute_one, execute_insert, execute_update
from modules.auth import log_audit
from utils.security import sanitize_filename

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

def render_messages(project: dict, user: dict):
    st.subheader("💬 Central de Mensagens & Comunicação Formal")
    st.caption("Canal único, formal e registrado entre o Cliente e a equipe técnica da Metrocon Engenharia.")

    # 1. Formulário de Nova Mensagem
    with st.expander("✉️ Escrever Nova Mensagem Oficial", expanded=False):
        with st.form("new_message_form", clear_on_submit=True):
            subject = st.text_input("Assunto da Mensagem*", placeholder="ex: Dúvida sobre acabamento ou prazo de entrega")
            content = st.text_area("Conteúdo da Mensagem*", placeholder="Escreva sua mensagem detalhada...")
            attached_file = st.file_uploader("Anexo (opcional - PDF, Imagem ou Documento)", type=['pdf', 'jpg', 'jpeg', 'png', 'docx'])

            btn_send = st.form_submit_button("Enviar Mensagem ➔", use_container_width=True)

            if btn_send:
                if not subject or not content:
                    st.warning("⚠️ Preencha o assunto e o conteúdo da mensagem.")
                else:
                    att_path = None
                    att_name = None
                    if attached_file:
                        os.makedirs(UPLOADS_DIR, exist_ok=True)
                        safe_name = sanitize_filename(attached_file.name)
                        att_path = os.path.join(UPLOADS_DIR, f"msg_{datetime.date.today()}_{safe_name}")
                        with open(att_path, 'wb') as f:
                            f.write(attached_file.getbuffer())
                        att_name = safe_name

                    recipient_id = None
                    if user['role'] == 'client':
                        eng = execute_one('SELECT id FROM users WHERE role = ? LIMIT 1', ('engineer',))
                        recipient_id = eng['id'] if eng else None
                    else:
                        recipient_id = project['client_id']

                    msg_id = execute_insert(
                        '''INSERT INTO messages (project_id, sender_id, recipient_id, subject, content, attachment_path, attachment_name, is_read)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 0)''',
                        (project['id'], user['id'], recipient_id, subject, content, att_path, att_name)
                    )

                    log_audit(user['id'], user['name'], user['role'], 'MESSAGE_SENT', 'messages', str(msg_id), f"Mensagem enviada sobre: {subject}")
                    st.success("✅ Mensagem enviada com sucesso! A equipe técnica foi notificada.")
                    st.rerun()

    # 2. Histórico de Mensagens do Projeto
    messages = execute_query(
        '''SELECT m.*, u.name as sender_name, u.role as sender_role, u.company as sender_company 
        FROM messages m 
        JOIN users u ON m.sender_id = u.id 
        WHERE m.project_id = ? 
        ORDER BY m.created_at DESC''',
        (project['id'],)
    )

    if not messages:
        st.info("Nenhuma mensagem trocada ainda neste projeto.")
        return

    st.markdown("### 📜 Histórico de Comunicações")

    for msg in messages:
        is_me = msg['sender_id'] == user['id']
        is_client_sender = msg['sender_role'] == 'client'

        role_badge = "🏠 Cliente" if is_client_sender else "👷 Metrocon Engenharia"
        bg_color = "#F8FAFC" if is_client_sender else "#EFF6FF"
        border_color = "#CBD5E1" if is_client_sender else "#93C5FD"

        with st.container():
            st.html(f"""
            <div style="background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; padding: 1.1rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 6px;">
                    <div>
                        <strong style="color: #0F2D59; font-size: 1rem;">{msg['subject']}</strong>
                    </div>
                    <div style="font-size: 0.78rem; color: #64748B;">
                        📅 {msg['created_at']}
                    </div>
                </div>
                <div style="font-size: 0.82rem; color: #475569; margin-bottom: 8px;">
                    De: <strong>{msg['sender_name']}</strong> ({role_badge})
                </div>
                <div style="color: #1E293B; font-size: 0.9rem; line-height: 1.5; white-space: pre-wrap;">
{msg['content']}
                </div>
            </div>
            """)

            if msg['attachment_path'] and os.path.exists(msg['attachment_path']):
                with open(msg['attachment_path'], 'rb') as af:
                    att_bytes = af.read()
                st.download_button(
                    label=f"📎 Baixar Anexo: {msg['attachment_name'] or 'arquivo'}",
                    data=att_bytes,
                    file_name=msg['attachment_name'] or 'anexo_mensagem.pdf',
                    key=f"dl_msg_{msg['id']}",
                    use_container_width=False
                )

            if not is_me and msg['is_read'] == 0:
                execute_update('UPDATE messages SET is_read = 1 WHERE id = ?', (msg['id'],))
