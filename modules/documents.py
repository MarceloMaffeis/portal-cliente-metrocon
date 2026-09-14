# -*- coding: utf-8 -*-
import streamlit as st
import os
import datetime
from database.connection import execute_query, execute_one, execute_insert, execute_update
from modules.auth import log_audit
from utils.security import sanitize_filename

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

def render_documents(project: dict, user: dict):
    st.subheader(f"📁 Central de Documentos & Acervo Técnico")
    st.caption("Organização categorizada com controle de versões, autenticidade e download seguro.")

    can_manage = user['role'] in ('admin', 'engineer')

    if can_manage:
        with st.expander("📤 Enviar Novo Documento / Nova Versão (Engenharia & Admin)", expanded=False):
            with st.form("upload_doc_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    doc_title = st.text_input("Título do Documento*", placeholder="ex: Projeto Arquitetônico Executivo")
                    doc_category = st.selectbox(
                        "Categoria*",
                        [
                            ('projetos', '📐 Projetos (Arquitetônico, Estrutural, etc.)'),
                            ('contratos', '📝 Contratos & Termos'),
                            ('documentos_legais', '⚖️ Documentos Legais & ART/RRT'),
                            ('aprovacoes', '🏛️ Aprovações em Órgãos & Alvarás'),
                            ('anexos', '📎 Anexos Gerais & Laudos')
                        ],
                        format_func=lambda x: x[1]
                    )
                with col2:
                    doc_version = st.text_input("Versão", value="1.0", placeholder="ex: 1.0, 2.0, 2.1")
                    uploaded_file = st.file_uploader("Arquivo (PDF, DWG, DOCX, ZIP, JPG, PNG)*", type=['pdf', 'dwg', 'docx', 'zip', 'jpg', 'png', 'jpeg'])

                doc_notes = st.text_area("Observações Técnicas / Histórico da Versão", placeholder="ex: Revisão atendendo solicitação de alteração da suíte...")
                submit_doc = st.form_submit_button("Salvar e Disponibilizar Documento ➔", use_container_width=True)

                if submit_doc:
                    if not doc_title or not uploaded_file:
                        st.warning("⚠️ Preencha o título e selecione um arquivo para upload.")
                    else:
                        os.makedirs(UPLOADS_DIR, exist_ok=True)
                        safe_name = sanitize_filename(uploaded_file.name)
                        file_path = os.path.join(UPLOADS_DIR, f"p{project['id']}_{safe_name}")
                        
                        with open(file_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())

                        size_kb = round(len(uploaded_file.getbuffer()) / 1024.0, 1)

                        doc_id = execute_insert(
                            '''INSERT INTO documents (project_id, user_id, category, title, file_name, file_path, file_size_kb, version, is_current, notes)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (project['id'], user['id'], doc_category[0], doc_title, safe_name, file_path, size_kb, doc_version, 1, doc_notes)
                        )

                        log_audit(user['id'], user['name'], user['role'], 'DOCUMENT_UPLOAD', 'documents', str(doc_id), f"Upload do documento: {doc_title} (v{doc_version})")
                        st.success(f"✅ Documento '{doc_title}' cadastrado com sucesso!")
                        st.rerun()

    # Categorias em Tabs
    categories = [
        ('projetos', '📐 Projetos'),
        ('contratos', '📝 Contratos'),
        ('documentos_legais', '⚖️ Documentos Legais'),
        ('aprovacoes', '🏛️ Aprovações & Órgãos'),
        ('anexos', '📎 Anexos Gerais')
    ]

    tabs = st.tabs([cat[1] for cat in categories])

    for i, (cat_key, cat_label) in enumerate(categories):
        with tabs[i]:
            docs = execute_query(
                '''SELECT d.*, u.name as author_name 
                FROM documents d 
                LEFT JOIN users u ON d.user_id = u.id 
                WHERE d.project_id = ? AND d.category = ? 
                ORDER BY d.uploaded_at DESC''',
                (project['id'], cat_key)
            )

            if not docs:
                st.info(f"Nenhum documento cadastrado na categoria '{cat_label}'.")
            else:
                for doc in docs:
                    with st.container():
                        st.html(f"""
                        <div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1.1rem; margin-bottom: 0.8rem; box-shadow: 0 2px 5px rgba(0,0,0,0.02);">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
                                <div>
                                    <h4 style="margin: 0; color: #0F2D59;">📄 {doc['title']}</h4>
                                    <p style="margin: 4px 0 0 0; font-size: 0.82rem; color: #64748B;">
                                        <strong>Versão:</strong> <span style="background: #E0E7FF; color: #3730A3; padding: 2px 6px; border-radius: 4px; font-weight: 700;">v{doc['version']}</span> • 
                                        <strong>Arquivo:</strong> {doc['file_name']} • 
                                        <strong>Tamanho:</strong> {doc['file_size_kb']} KB • 
                                        <strong>Data de Inclusão:</strong> {doc['uploaded_at']}
                                    </p>
                                    <p style="margin: 6px 0 0 0; font-size: 0.85rem; color: #334155;">
                                        {doc['notes'] or 'Documento técnico oficial disponibilizado pela Metrocon Engenharia.'}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """)

                        if os.path.exists(doc['file_path']):
                            with open(doc['file_path'], 'rb') as f:
                                file_bytes = f.read()

                            btn_col1, btn_col2 = st.columns([0.3, 0.7])
                            with btn_col1:
                                if st.download_button(
                                    label=f"⬇️ Baixar {doc['file_name']}",
                                    data=file_bytes,
                                    file_name=doc['file_name'],
                                    key=f"dl_doc_{doc['id']}",
                                    use_container_width=True
                                ):
                                    log_audit(user['id'], user['name'], user['role'], 'DOCUMENT_DOWNLOAD', 'documents', str(doc['id']), f"Download do documento: {doc['file_name']} (v{doc['version']})")
                        else:
                            st.warning("⚠️ Arquivo físico não localizado no servidor.")
