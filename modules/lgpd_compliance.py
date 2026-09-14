# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import json
import datetime
from database.connection import execute_query, execute_one
from utils.ui_components import COMPANY_NAME, COMPANY_CNPJ

def render_lgpd_compliance(user: dict):
    st.subheader("🛡️ Segurança, Privacidade & Conformidade LGPD")
    st.caption("Gestão de privacidade de dados, transparência e trilha auditável de acessos (Lei Geral de Proteção de Dados - Lei nº 13.709/2018).")

    is_admin = user['role'] == 'admin'

    tab_terms, tab_rights, tab_audit = st.tabs([
        "📜 Termos & Política de Privacidade",
        "👤 Direitos do Titular (Art. 18)",
        "🔍 Trilha de Auditoria & Acessos"
    ])

    # 1. Termos de Privacidade
    with tab_terms:
        st.markdown(f"### 📄 Política de Privacidade e Proteção de Dados • {COMPANY_NAME}")
        st.markdown(f"""
        **Controlador dos Dados:** {COMPANY_NAME} • CNPJ: {COMPANY_CNPJ}  
        **Encarregado pelo Tratamento de Dados (DPO):** dpo@metrocon.com.br

        ---
        #### 1. Finalidade do Tratamento
        Os dados pessoais cadastrados nesta plataforma têm como finalidade exclusiva:
        - A identificação e autenticação segura do cliente no portal;
        - O acompanhamento em tempo real de obras, reformas e processos administrativos de legalização;
        - A disponibilização de documentos técnicos, plantas, contratos e relatórios diários;
        - A comunicação formal e rastreável entre as partes contratantes;
        - O cumprimento de obrigações legais e regulatórias perante órgãos públicos (Prefeituras, CREA/CAU, Corpo de Bombeiros).

        #### 2. Segurança e Armazenamento
        - Todas as senhas são criptografadas utilizando hash criptográfico seguro (PBKDF2 com Salt aleatório).
        - Os documentos e registros fotográficos são armazenados em diretórios restritos e particionados.
        - Toda e qualquer visualização, download ou alteração no sistema é registrada em log de auditoria permanente.

        #### 3. Compartilhamento de Dados
        A Metrocon Engenharia não comercializa nem compartilha dados de clientes com terceiros, exceto quando estritamente necessário para a tramitação de protocolos em órgãos públicos e cumprimento de exigências regulatórias.
        """)

        st.success(f"🔒 Seu consentimento aos termos foi registrado em: **{user['lgpd_consent_date'] or 'Primeiro acesso'}**.")

    # 2. Direitos do Titular
    with tab_rights:
        st.markdown("### 👤 Exercício dos Direitos do Titular de Dados")
        st.markdown("Nos termos do Art. 18 da LGPD, você pode solicitar a confirmação de tratamento, acesso, retificação ou exportação dos seus dados:")

        st.markdown("#### 📦 Exportação de Dados Cadastrais")
        user_data = {
            "id": user['id'],
            "nome_completo": user['name'],
            "email_cadastrado": user['email'],
            "perfil_acesso": user['role'],
            "telefone": user['phone'],
            "empresa_imovel": user['company'],
            "data_consentimento_lgpd": user['lgpd_consent_date'],
            "data_extracao": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "controlador": COMPANY_NAME,
            "cnpj": COMPANY_CNPJ
        }

        json_str = json.dumps(user_data, indent=4, ensure_ascii=False)
        st.download_button(
            label="⬇️ Baixar Relatório dos Meus Dados Pessoais (JSON)",
            data=json_str.encode('utf-8'),
            file_name=f"dados_pessoais_lgpd_user_{user['id']}.json",
            mime="application/json",
            use_container_width=True
        )

        st.markdown("""
        ---
        **Canais de Atendimento ao Titular:**  
        Para solicitar retificação, anonimização ou exclusão de dados desnecessários, entre em contato diretamente com o nosso Encarregado de Dados: `dpo@metrocon.com.br`.
        """)

    # 3. Trilha de Auditoria (Audit Logs)
    with tab_audit:
        if is_admin:
            st.markdown("### 🔍 Trilha Completa de Auditoria do Sistema")
            st.caption("Visão gerencial e jurídica de todas as operações realizadas na plataforma.")
            
            logs = execute_query('SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 200')
        else:
            st.markdown("### 🔍 Seu Histórico de Acessos e Operações")
            st.caption("Registros das operações realizadas pelo seu usuário.")
            
            logs = execute_query('SELECT * FROM audit_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 100', (user['id'],))

        if not logs:
            st.info("Nenhum registro de auditoria encontrado.")
        else:
            df_logs = pd.DataFrame([dict(l) for l in logs])
            
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_action = st.multiselect("Filtrar por Tipo de Ação", options=df_logs['action'].unique().tolist(), default=[])
            with col_f2:
                st.metric("Total de Registros Localizados", len(df_logs))

            if filter_action:
                df_logs = df_logs[df_logs['action'].isin(filter_action)]

            st.dataframe(
                df_logs,
                use_container_width=True,
                column_config={
                    'timestamp': 'Data/Hora',
                    'user_name': 'Usuário',
                    'user_role': 'Perfil',
                    'action': 'Ação Realizada',
                    'resource_type': 'Recurso',
                    'details': 'Detalhamento Técnico',
                    'ip_or_session': 'Sessão/IP'
                }
            )

            csv_bytes = df_logs.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="⬇️ Exportar Trilha de Auditoria para CSV / Excel",
                data=csv_bytes,
                file_name=f"trilha_auditoria_lgpd_{datetime.date.today()}.csv",
                mime="text/csv"
            )
