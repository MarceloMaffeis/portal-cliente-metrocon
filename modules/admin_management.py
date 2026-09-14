# -*- coding: utf-8 -*-
import streamlit as st
import datetime
from database.connection import execute_query, execute_one, execute_insert, execute_update
from utils.security import hash_password
from modules.auth import log_audit

def render_admin_management(user: dict):
    if user['role'] not in ('admin', 'engineer'):
        st.error("🚫 Acesso restrito a administradores e engenheiros responsáveis.")
        return

    st.subheader("⚙️ Painel de Gestão & Administração de Projetos")
    st.caption("Cadastre e gerencie novos projetos, clientes, engenheiros e etapas construtivas/processuais.")

    tab_proj, tab_users, tab_stages = st.tabs(["🏗️ Gestão de Projetos", "👥 Gestão de Usuários & Clientes", "📌 Gestão de Etapas"])

    # 1. Gestão de Projetos
    with tab_proj:
        st.markdown("### ➕ Cadastrar Novo Projeto / Processo")
        clients = execute_query('SELECT id, name, company FROM users WHERE role = ?', ('client',))

        with st.form("create_project_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_title = st.text_input("Título do Projeto / Obra*", placeholder="ex: Construção Residencial Alphaville 3")
                p_type = st.selectbox("Tipo de Serviço*", [
                    ('obra', 'Construção Civil (Obra Nova)'),
                    ('reforma', 'Reforma & Retrofit'),
                    ('administrativo', 'Processo Administrativo / Legalização')
                ], format_func=lambda x: x[1])
                p_cat = st.text_input("Categoria / Escopo*", placeholder="ex: Residencial Unifamiliar 450 m² / Habite-se Comercial")
                
                if clients:
                    p_client = st.selectbox("Cliente Titular*", clients, format_func=lambda x: f"{x['name']} ({x['company'] or 'Pessoa Física'})")
                else:
                    st.warning("Cadastre um cliente antes de criar um projeto.")
                    p_client = None

            with c2:
                p_address = st.text_input("Endereço da Obra ou Órgão Público*", placeholder="ex: Alameda das Flores, 100 / Prefeitura de SP")
                p_protocol = st.text_input("Número de Protocolo / Alvará", placeholder="ex: ALV-2026/123 ou PMSP-9912")
                p_st_date = st.date_input("Data de Início", value=datetime.date.today())
                p_end_date = st.date_input("Previsão de Conclusão", value=datetime.date.today() + datetime.timedelta(days=180))

            p_desc = st.text_area("Descrição Geral do Escopo*", placeholder="Descreva os serviços contratados...")
            p_notes = st.text_input("Notas Técnicas da Metrocon", value="Início dos serviços conforme cronograma aprovado.")

            submit_proj = st.form_submit_button("Cadastrar Projeto ➔", use_container_width=True)

            if submit_proj:
                if not p_title or not p_cat or not p_client or not p_desc:
                    st.warning("⚠️ Preencha todos os campos obrigatórios.")
                else:
                    new_pid = execute_insert(
                        '''INSERT INTO projects (client_id, title, type, category_label, description, address_or_agency, protocol_number, status, progress_percent, start_date, end_date_estimated, responsible_name, responsible_phone, responsible_email, technical_notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'planejamento', 0.0, ?, ?, ?, ?, ?, ?)''',
                        (
                            p_client['id'],
                            p_title,
                            p_type[0],
                            p_cat,
                            p_desc,
                            p_address,
                            p_protocol,
                            p_st_date.strftime('%Y-%m-%d'),
                            p_end_date.strftime('%Y-%m-%d'),
                            user['name'],
                            '(11) 3456-7800',
                            user['email'],
                            p_notes
                        )
                    )
                    log_audit(user['id'], user['name'], user['role'], 'PROJECT_CREATE', 'projects', str(new_pid), f"Novo projeto cadastrado: {p_title}")
                    st.success(f"✅ Projeto '{p_title}' cadastrado com sucesso!")
                    st.rerun()

        st.markdown("---")
        st.markdown("### 📋 Projetos Existentes")
        all_projs = execute_query('SELECT p.*, u.name as client_name FROM projects p JOIN users u ON p.client_id = u.id ORDER BY p.id DESC')
        for p in all_projs:
            with st.expander(f"📍 {p['title']} ({p['type'].upper()}) - Progresso: {p['progress_percent']}%"):
                st.write(f"**Cliente:** {p['client_name']} | **Status:** `{p['status']}` | **Prazo:** {p['end_date_estimated']}")
                st.write(f"**Local/Órgão:** {p['address_or_agency']} | **Protocolo:** {p['protocol_number']}")
                st.write(f"**Notas:** {p['technical_notes']}")

    # 2. Gestão de Usuários
    with tab_users:
        st.markdown("### ➕ Cadastrar Novo Usuário (Cliente ou Engenheiro)")
        with st.form("create_user_form"):
            u1, u2 = st.columns(2)
            with u1:
                u_name = st.text_input("Nome Completo*", placeholder="ex: Eng. Mariana Souza / Dr. Fernando Costa")
                u_email = st.text_input("E-mail de Acesso*", placeholder="ex: mariana@metrocon.com.br")
                u_role = st.selectbox("Perfil de Acesso*", [
                    ('client', 'Cliente (Acesso Restrito aos Próprios Projetos)'),
                    ('engineer', 'Engenheiro / Técnico (Gestão Técnica)'),
                    ('admin', 'Administrador (Acesso Total)')
                ], format_func=lambda x: x[1])
            with u2:
                u_pass = st.text_input("Senha Inicial*", type="password", value="Metrocon@2026")
                u_phone = st.text_input("Telefone de Contato", placeholder="(11) 98765-4321")
                u_company = st.text_input("Empresa / Condomínio", placeholder="ex: Inova Participações / Residencial Alpha")

            submit_user = st.form_submit_button("Cadastrar Usuário ➔", use_container_width=True)

            if submit_user:
                if not u_name or not u_email or not u_pass:
                    st.warning("⚠️ Preencha nome, e-mail e senha.")
                else:
                    existing = execute_one('SELECT id FROM users WHERE email = ?', (u_email.strip().lower(),))
                    if existing:
                        st.error("❌ Já existe um usuário cadastrado com este e-mail.")
                    else:
                        phash, psalt = hash_password(u_pass)
                        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        new_uid = execute_insert(
                            '''INSERT INTO users (name, email, password_hash, salt, role, phone, company, lgpd_consent_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            (u_name, u_email.strip().lower(), phash, psalt, u_role[0], u_phone, u_company, now_str)
                        )
                        log_audit(user['id'], user['name'], user['role'], 'USER_CREATE', 'users', str(new_uid), f"Novo usuário criado: {u_name} ({u_role[0]})")
                        st.success(f"✅ Usuário '{u_name}' cadastrado com sucesso!")
                        st.rerun()

        st.markdown("---")
        st.markdown("### 👥 Lista de Usuários do Sistema")
        users_list = execute_query('SELECT id, name, email, role, phone, company, created_at, lgpd_consent_date FROM users ORDER BY id ASC')
        st.dataframe(
            [dict(u) for u in users_list],
            use_container_width=True,
            column_config={
                'role': 'Perfil',
                'name': 'Nome',
                'email': 'E-mail',
                'company': 'Empresa / Imóvel',
                'phone': 'Telefone',
                'lgpd_consent_date': 'Aceite LGPD'
            }
        )

    # 3. Gestão de Etapas
    with tab_stages:
        st.markdown("### ➕ Adicionar Nova Etapa ao Cronograma de um Projeto")
        all_p = execute_query('SELECT id, title FROM projects ORDER BY title ASC')
        if not all_p:
            st.info("Nenhum projeto cadastrado.")
            return

        with st.form("add_stage_form"):
            selected_proj = st.selectbox("Selecione o Projeto*", all_p, format_func=lambda x: x['title'])
            
            s1, s2 = st.columns(2)
            with s1:
                stg_name = st.text_input("Nome da Etapa*", placeholder="ex: Instalação de Esquadrias / Vistoria Bombeiros")
                stg_type = st.selectbox("Tipo da Etapa*", [
                    ('execucao', 'Execução Física em Canteiro'),
                    ('orgao_publico', 'Tramitação em Órgão Público'),
                    ('documental', 'Elaboração Documental & Projetos'),
                    ('vistoria', 'Vistoria Técnica')
                ], format_func=lambda x: x[1])
                stg_order = st.number_input("Ordem na Sequência", min_value=1, value=1, step=1)
            with s2:
                stg_agency = st.text_input("Órgão Responsável (se aplicável)", placeholder="ex: Prefeitura de SP / Corpo de Bombeiros")
                stg_prot = st.text_input("Número do Protocolo", placeholder="ex: PROT-2026/001")
                stg_start = st.date_input("Início Previsto", value=datetime.date.today())
                stg_end = st.date_input("Término Previsto", value=datetime.date.today() + datetime.timedelta(days=30))

            stg_desc = st.text_area("Descrição da Etapa", placeholder="Detalhes dos requisitos ou serviços a serem cumpridos...")

            submit_stage = st.form_submit_button("Adicionar Etapa ao Cronograma ➔", use_container_width=True)

            if submit_stage:
                if not stg_name:
                    st.warning("⚠️ Informe o nome da etapa.")
                else:
                    new_sid = execute_insert(
                        '''INSERT INTO schedule_stages (project_id, stage_name, stage_type, description, agency_name, protocol_number, start_date, end_date, progress_percent, status, order_index)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0.0, 'a_iniciar', ?)''',
                        (selected_proj['id'], stg_name, stg_type[0], stg_desc, stg_agency, stg_prot, stg_start.strftime('%Y-%m-%d'), stg_end.strftime('%Y-%m-%d'), stg_order)
                    )
                    log_audit(user['id'], user['name'], user['role'], 'STAGE_CREATE', 'schedule_stages', str(new_sid), f"Etapa criada: {stg_name} no projeto {selected_proj['id']}")
                    st.success("✅ Etapa adicionada com sucesso ao cronograma!")
                    st.rerun()
