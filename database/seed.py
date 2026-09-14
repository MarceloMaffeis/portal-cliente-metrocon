# -*- coding: utf-8 -*-
import os
import datetime
from database.connection import get_db, init_db, execute_insert, execute_query
from utils.security import hash_password
from utils.ui_components import create_sample_pdf, create_sample_image

UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')

def run_seed():
    init_db()
    existing = execute_query('SELECT COUNT(*) as count FROM users')
    if existing and existing[0]['count'] > 0:
        print('Banco já contém dados.')
        return

    print('Carga inicial de dados Metrocon Engenharia...')
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    padm, sadm = hash_password('Admin@123456')
    peng, seng = hash_password('Eng@123456')
    pcli1, scli1 = hash_password('Cliente@123456')
    pcli2, scli2 = hash_password('Cliente@123456')

    admin_id = execute_insert(
        'INSERT INTO users (name, email, password_hash, salt, role, phone, company, lgpd_consent_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('Diretoria Técnica Metrocon', 'admin@metrocon.com.br', padm, sadm, 'admin', '(11) 98765-4321', 'METROCON ENGENHARIA E CONSTRUÇÕES', now_str)
    )

    eng_id = execute_insert(
        'INSERT INTO users (name, email, password_hash, salt, role, phone, company, lgpd_consent_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('Eng. Carlos Eduardo (CREA/SP 506123456)', 'engenharia@metrocon.com.br', peng, seng, 'engineer', '(11) 99888-7766', 'METROCON ENGENHARIA E CONSTRUÇÕES', now_str)
    )

    cli1_id = execute_insert(
        'INSERT INTO users (name, email, password_hash, salt, role, phone, company, lgpd_consent_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('Dr. Roberto Albuquerque', 'cliente.reserva@gmail.com', pcli1, scli1, 'client', '(11) 97123-4567', 'Residencial Reserva Imperial', now_str)
    )

    cli2_id = execute_insert(
        'INSERT INTO users (name, email, password_hash, salt, role, phone, company, lgpd_consent_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        ('Dra. Juliana Mendes', 'diretoria@inovaempreendimentos.com.br', pcli2, scli2, 'client', '(11) 98234-5678', 'Inova Empreendimentos Imobiliários', now_str)
    )

    # 2. Projetos
    p1_id = execute_insert(
        '''INSERT INTO projects (client_id, title, type, category_label, description, address_or_agency, protocol_number, status, progress_percent, start_date, end_date_estimated, responsible_name, responsible_phone, responsible_email, technical_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (cli1_id, 'Construção Residencial Reserva Imperial - Casa 42', 'obra', 'Residencial Unifamiliar de Alto Padrão (540 m²)', 'Construção completa de residência em 3 pavimentos com área gourmet, piscina e automação residencial.', 'Alameda dos Ipês, 42 - Condomínio Reserva Imperial, Santana de Parnaíba/SP', 'ALV-2026/004128', 'em_andamento', 68.0, '2026-02-15', '2026-12-20', 'Eng. Carlos Eduardo', '(11) 99888-7766', 'engenharia@metrocon.com.br', 'Obra em fase de acabamentos e instalações elétricas/hidráulicas. Cronograma dentro da margem de segurança prevista.')
    )

    p2_id = execute_insert(
        '''INSERT INTO projects (client_id, title, type, category_label, description, address_or_agency, protocol_number, status, progress_percent, start_date, end_date_estimated, responsible_name, responsible_phone, responsible_email, technical_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (cli2_id, 'Regularização Imobiliária & Habite-se Comercial - Alpha Tower', 'administrativo', 'Aprovação em Órgãos Públicos & Legalização Predial', 'Processo completo de regularização de área ampliada (3.200 m²), projeto legal, PPCI/AVCB Bombeiros e emissão de Habite-se comercial.', 'Prefeitura Municipal de São Paulo (SMUL) & Corpo de Bombeiros SP', 'PMSP-2026/089412-ADM', 'em_aprovacao_orgao', 75.0, '2026-01-10', '2026-10-30', 'Eng. Carlos Eduardo', '(11) 99888-7766', 'engenharia@metrocon.com.br', 'Análise técnica da Prefeitura concluída com deferimento preliminar. Vistoria do Corpo de Bombeiros agendada para expedição do AVCB final.')
    )

    p3_id = execute_insert(
        '''INSERT INTO projects (client_id, title, type, category_label, description, address_or_agency, protocol_number, status, progress_percent, start_date, end_date_estimated, responsible_name, responsible_phone, responsible_email, technical_notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (cli2_id, 'Retrofit Corporativo & Reforma Geral - 8º Andar Metrocon Office', 'reforma', 'Reforma Corporativa Comercial (600 m²)', 'Retrofit integral de layout open-space, climatização VRF, cabeamento estruturado e piso elevado.', 'Av. Paulista, 1500 - 8º Andar, Bela Vista, São Paulo/SP', 'REF-2026/0119', 'em_andamento', 35.0, '2026-06-01', '2026-11-15', 'Eng. Carlos Eduardo', '(11) 99888-7766', 'engenharia@metrocon.com.br', 'Demolições e infraestrutura de dutos concluídas. Início da montagem de divisórias acústicas e drywall.')
    )

    # 3. Documentos
    docs_data = [
        (p1_id, eng_id, 'projetos', 'Projeto Arquitetônico Executivo', 'Projeto_Arquitetonico_Executivo_v2.0.pdf', '2.0', 'Revisão com ampliação da suíte master e área gourmet.'),
        (p1_id, eng_id, 'projetos', 'Projeto Estrutural de Concreto Armado', 'Projeto_Estrutural_Calculo_v1.0.pdf', '1.0', 'Memória de cálculo e detalhamento de armaduras.'),
        (p1_id, admin_id, 'contratos', 'Contrato de Empreitada Global', 'Contrato_Prestacao_Servicos_Metrocon.pdf', '1.0', 'Contrato formal assinado com cronograma físico-financeiro.'),
        (p1_id, eng_id, 'documentos_legais', 'ART de Execução de Obra - CREA-SP', 'ART_Execucao_Obra_CREA_SP.pdf', '1.0', 'Anotação de Responsabilidade Técnica devidamente quitada.'),
        (p1_id, eng_id, 'aprovacoes', 'Alvará de Construção Municipal', 'Alvara_Construcao_Prefeitura.pdf', '1.0', 'Alvará expedido pela Secretaria de Obras.'),
        (p2_id, eng_id, 'projetos', 'Planta Baixa de Regularização As-Built', 'Planta_AsBuilt_Regularizacao_v2.0.pdf', '2.0', 'Levantamento cadastral com todas as alterações físicas.'),
        (p2_id, admin_id, 'contratos', 'Contrato de Assessoria Técnica e Legalização', 'Contrato_Legalizacao_AlphaTower.pdf', '1.0', 'Contrato de serviços técnicos de tramitação.'),
        (p2_id, eng_id, 'documentos_legais', 'Laudo de Estabilidade Estrutural e Segurança', 'Laudo_Estabilidade_Estrutural.pdf', '1.0', 'Laudo pericial com ART registrada.'),
        (p2_id, eng_id, 'aprovacoes', 'Protocolo Geral de Aprovação PMSP', 'Protocolo_Prefeitura_Regularizacao.pdf', '1.0', 'Comprovante de protocolo e tramitação inicial.'),
        (p2_id, eng_id, 'aprovacoes', 'Projeto Técnico de Combate a Incêndio (PPCI)', 'Projeto_Combate_Incendio_AVCB.pdf', '1.0', 'Projeto aprovado preliminarmente pelo Corpo de Bombeiros.')
    ]

    for pid, uid, cat, title, fname, ver, notes in docs_data:
        fpath = os.path.join(UPLOADS_DIR, fname)
        create_sample_pdf(fpath, title, cat.upper(), f'Projeto {pid}', today_str)
        size_kb = round(os.path.getsize(fpath) / 1024.0, 1)
        execute_insert(
            'INSERT INTO documents (project_id, user_id, category, title, file_name, file_path, file_size_kb, version, is_current, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (pid, uid, cat, title, fname, fpath, size_kb, ver, 1, notes)
        )

    # 4. Diários de Obra e Processo (RDO / RDP)
    rdo1_id = execute_insert(
        'INSERT INTO daily_logs (project_id, author_id, log_date, title, description, weather_conditions, team_count, highlight_activities, occurrences) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (p1_id, eng_id, '2026-09-12', 'Conclusão do contrapiso e tubulação hidráulica', 'Dia produtivo com equipe completa. Concluída a concretagem do contrapiso no piso superior e teste de estanqueidade na rede de esgoto e água quente.', 'Ensolarado (26°C)', 14, '- Finalização da regularização de piso nos quartos e banheiros;\n- Instalação dos conduítes de automação residencial;\n- Teste de pressão hidráulica aprovado sem vazamentos.', 'Nenhuma ocorrência de segurança ou desvio.')
    )
    img1_path = os.path.join(UPLOADS_DIR, 'foto_obra_casa42_rdo1_1.jpg')
    create_sample_image(img1_path, 'Tubulação Hidráulica e Contrapiso', 'Pavimento Superior - Concluído com sucesso', (15, 45, 85))
    execute_insert('INSERT INTO daily_log_photos (daily_log_id, file_path, file_name, caption) VALUES (?, ?, ?, ?)',
                   (rdo1_id, img1_path, 'foto_obra_casa42_rdo1_1.jpg', 'Execução da tubulação e teste de pressão hidrostática'))

    img2_path = os.path.join(UPLOADS_DIR, 'foto_obra_casa42_rdo1_2.jpg')
    create_sample_image(img2_path, 'Vista Geral da Fachada e Alvenaria', 'Alvenaria de vedação 100% finalizada', (35, 75, 55))
    execute_insert('INSERT INTO daily_log_photos (daily_log_id, file_path, file_name, caption) VALUES (?, ?, ?, ?)',
                   (rdo1_id, img2_path, 'foto_obra_casa42_rdo1_2.jpg', 'Fachada frontal pronta para início do emboço e reboco'))

    rdo2_id = execute_insert(
        'INSERT INTO daily_logs (project_id, author_id, log_date, title, description, weather_conditions, team_count, highlight_activities, occurrences) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (p1_id, eng_id, '2026-09-08', 'Assentamento de revestimentos no espaço gourmet e piscina', 'Avanço na área de lazer externa. Início do assentamento de porcelanato acetinado e preparação do deck da piscina.', 'Parcialmente Nublado (23°C)', 12, '- Impermeabilização da laje do gourmet com manta asfáltica;\n- Assentamento de porcelanatos 120x120cm;\n- Chegada das esquadrias de alumínio.', 'Entrega de materiais realizada dentro do prazo programado.')
    )
    img3_path = os.path.join(UPLOADS_DIR, 'foto_obra_casa42_rdo2_1.jpg')
    create_sample_image(img3_path, 'Espaço Gourmet e Piscina', 'Impermeabilização e assentamento de porcelanato', (80, 40, 20))
    execute_insert('INSERT INTO daily_log_photos (daily_log_id, file_path, file_name, caption) VALUES (?, ?, ?, ?)',
                   (rdo2_id, img3_path, 'foto_obra_casa42_rdo2_1.jpg', 'Área externa gourmet com piso impermeabilizado'))

    rdp1_id = execute_insert(
        'INSERT INTO daily_logs (project_id, author_id, log_date, title, description, weather_conditions, team_count, highlight_activities, occurrences) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (p2_id, eng_id, '2026-09-10', 'Protocolo de Atendimento a Comunique-se da Prefeitura e AVCB', 'Comparecimento à Secretaria de Urbanismo e Licenciamento. Protocolado documento complementar com ART corrigida e laudo de acessibilidade NBR 9050.', 'Tramitação Presencial / Digital', 2, '- Protocolo SEI nº 6012.2026/004921-8;\n- Agendamento da vistoria presencial do Corpo de Bombeiros;\n- Parecer positivo do auditor fiscal.', 'Exigência da Prefeitura cumprida 10 dias antes do prazo fatal.')
    )
    img_rdp1 = os.path.join(UPLOADS_DIR, 'comprovante_protocolo_rdp1.jpg')
    create_sample_image(img_rdp1, 'Comprovante Oficial de Protocolo SEI', 'Processo SEI nº 6012.2026/004921-8 - Deferido', (20, 60, 90))
    execute_insert('INSERT INTO daily_log_photos (daily_log_id, file_path, file_name, caption) VALUES (?, ?, ?, ?)',
                   (rdp1_id, img_rdp1, 'comprovante_protocolo_rdp1.jpg', 'Comprovante de atendimento a exigência municipal anexado'))

    # 5. Etapas de Cronograma
    p1_stages = [
        ('Fundação e Sondagem', 'execucao', 'Estacas escavadas e blocos de coroamento', None, None, '2026-02-15', '2026-03-30', 100.0, 'concluido', 1),
        ('Estrutura de Concreto Armado', 'execucao', 'Pilares, vigas e lajes dos 3 pavimentos', None, None, '2026-04-01', '2026-05-31', 100.0, 'concluido', 2),
        ('Alvenaria de Vedação e Telhado', 'execucao', 'Paredes internas/externas e cobertura termoacústica', None, None, '2026-06-01', '2026-07-15', 100.0, 'concluido', 3),
        ('Instalações Elétricas, Hidráulicas e Automação', 'execucao', 'Tubulações, fiação, quadros e infra de ar condicionado', None, None, '2026-07-16', '2026-09-30', 80.0, 'em_andamento', 4),
        ('Revestimentos, Pisos e Azulejos', 'execucao', 'Porcelanatos, pastilhas, bancadas de granito e louças', None, None, '2026-09-01', '2026-10-31', 45.0, 'em_andamento', 5),
        ('Pintura, Esquadrias e Vidraçaria', 'execucao', 'Pintura interna/externa, esquadrias de alumínio e vidros laminados', None, None, '2026-10-15', '2026-11-30', 0.0, 'a_iniciar', 6),
        ('Vistoria Final, Limpeza e Entrega das Chaves', 'vistoria', 'Vistoria detalhada com cliente e entrega do manual do proprietário', None, None, '2026-12-01', '2026-12-20', 0.0, 'a_iniciar', 7)
    ]
    for s_name, s_type, s_desc, ag_name, prot, st_date, end_date, prog, stt, idx in p1_stages:
        execute_insert(
            'INSERT INTO schedule_stages (project_id, stage_name, stage_type, description, agency_name, protocol_number, start_date, end_date, progress_percent, status, order_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (p1_id, s_name, s_type, s_desc, ag_name, prot, st_date, end_date, prog, stt, idx)
        )

    p2_stages = [
        ('Levantamento Topográfico & As-Built', 'documental', 'Medição in-loco e plantas cadastrais completas', 'Empresa Topografia', 'TOP-9912', '2026-01-10', '2026-02-10', 100.0, 'concluido', 1),
        ('Elaboração do Projeto Legal e Memoriais', 'documental', 'Desenhos técnicos de acordo com Código de Obras', 'Prefeitura Municipal', 'PL-2026/01', '2026-02-11', '2026-03-15', 100.0, 'concluido', 2),
        ('Protocolo de Aprovação na Prefeitura', 'orgao_publico', 'Abertura do processo administrativo na PMSP', 'PMSP - SMUL', 'PMSP-2026/089412-ADM', '2026-03-16', '2026-06-30', 100.0, 'concluido', 3),
        ('Vistoria e Emissão do AVCB (Bombeiros)', 'orgao_publico', 'Inspeção dos equipamentos de combate a incêndio', 'Corpo de Bombeiros SP', 'CB-AVCB-449102', '2026-07-01', '2026-09-30', 70.0, 'em_analise_orgao', 4),
        ('Emissão do Auto de Conclusão (Habite-se)', 'orgao_publico', 'Certificado final de conclusão de obra e regularização', 'PMSP - SMUL', 'HAB-2026/099', '2026-10-01', '2026-10-20', 0.0, 'a_iniciar', 5),
        ('Averbação no Cartório de Registro de Imóveis', 'documental', 'Atualização da matrícula com a nova área construída', '15º Cartório de Registro de Imóveis', 'MATR-94812', '2026-10-21', '2026-10-30', 0.0, 'a_iniciar', 6)
    ]
    for s_name, s_type, s_desc, ag_name, prot, st_date, end_date, prog, stt, idx in p2_stages:
        execute_insert(
            'INSERT INTO schedule_stages (project_id, stage_name, stage_type, description, agency_name, protocol_number, start_date, end_date, progress_percent, status, order_index) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (p2_id, s_name, s_type, s_desc, ag_name, prot, st_date, end_date, prog, stt, idx)
        )

    # 6. Atas de Reunião
    execute_insert(
        'INSERT INTO meeting_minutes (project_id, title, meeting_date, location_or_link, participants, summary_topics, decisions, action_items) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (p1_id, 'Ata de Alinhamento de Revestimentos e Pontos de Iluminação', '2026-08-28 15:00', 'Canteiro de Obras - Casa 42', 'Dr. Roberto Albuquerque (Cliente), Eng. Carlos Eduardo (Metrocon), Arq. Beatriz Lima (Arquitetura)', '1. Escolha dos padrões de revestimentos;\n2. Definição dos pontos extras de iluminação em LED;\n3. Cronograma de marcenaria e marmoraria.', '- Aprovado porcelanato Calacatta Gold 120x120cm para living e gourmet;\n- Ajustado o posicionamento da coifa central da ilha;\n- Prazo final mantido para dezembro/2026.', '- Metrocon: Enviar cotação de pontos elétricos extras até 05/09 (Concluído);\n- Cliente: Confirmar modelo da banheira de hidromassagem até 10/09 (Concluído).')
    )

    execute_insert(
        'INSERT INTO meeting_minutes (project_id, title, meeting_date, location_or_link, participants, summary_topics, decisions, action_items) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (p2_id, 'Ata de Alinhamento sobre Exigências do Corpo de Bombeiros', '2026-09-02 10:30', 'Reunião Virtual (Google Meet)', 'Dra. Juliana Mendes (Inova), Eng. Carlos Eduardo (Metrocon), Tenente Brandão (Consultor PPCI)', '1. Revisão das rotas de fuga no subsolo do Alpha Tower;\n2. Instalação de sinalização de emergência fotoluminescente;\n3. Agendamento da vistoria final.', '- Decidido instalar 8 novas luminárias de emergência autônomas no subsolo;\n- Liberado orçamento complementar de R$ 3.800 para hidrantes.', '- Metrocon: Finalizar instalação de sinalizações até 18/09;\n- Metrocon: Agendar presença de vistoriador do Corpo de Bombeiros para 25/09.')
    )

    # 7. Mensagens Formais
    execute_insert(
        'INSERT INTO messages (project_id, sender_id, recipient_id, subject, content, is_read) VALUES (?, ?, ?, ?, ?, ?)',
        (p1_id, cli1_id, eng_id, 'Dúvida sobre especificação do piso da garagem', 'Olá Eng. Carlos, gostaria de confirmar se o piso da rampa de acesso à garagem terá acabamento antiderrapante conforme conversamos. Um abraço!', 1)
    )

    execute_insert(
        'INSERT INTO messages (project_id, sender_id, recipient_id, subject, content, is_read) VALUES (?, ?, ?, ?, ?, ?)',
        (p1_id, eng_id, cli1_id, 'Re: Dúvida sobre especificação do piso da garagem', 'Olá Dr. Roberto! Perfeito. Conforme definido em ata, o acabamento será em Fulget resinado cinza médio, 100% antiderrapante e de alta resistência a tráfego de veículos. A aplicação está programada para o início de novembro.', 1)
    )

    execute_insert(
        'INSERT INTO messages (project_id, sender_id, recipient_id, subject, content, is_read) VALUES (?, ?, ?, ?, ?, ?)',
        (p2_id, cli2_id, eng_id, 'Confirmação de Protocolo e Previsão do Habite-se', 'Prezado Carlos, recebemos a notificação da atualização do diário de processo. Poderia nos enviar uma previsão estimada para a averbação final em cartório após a conclusão do AVCB?', 0)
    )

    # 8. LGPD Audit Logs
    audit_samples = [
        (cli1_id, 'Dr. Roberto Albuquerque', 'client', 'LOGIN', 'auth', 'user_session', 'Login bem-sucedido no Portal do Cliente', '189.102.45.12'),
        (cli1_id, 'Dr. Roberto Albuquerque', 'client', 'DOCUMENT_DOWNLOAD', 'documents', '1', 'Download do documento: Projeto_Arquitetonico_Executivo_v2.0.pdf', '189.102.45.12'),
        (cli1_id, 'Dr. Roberto Albuquerque', 'client', 'LGPD_CONSENT', 'privacy_policy', 'terms_v1', 'Aceite formal dos Termos de Privacidade e Proteção de Dados', '189.102.45.12'),
        (cli2_id, 'Dra. Juliana Mendes', 'client', 'LOGIN', 'auth', 'user_session', 'Login bem-sucedido no Portal do Cliente', '201.86.110.55'),
        (cli2_id, 'Dra. Juliana Mendes', 'client', 'DOCUMENT_DOWNLOAD', 'documents', '8', 'Download do documento: Laudo_Estabilidade_Estrutural.pdf', '201.86.110.55'),
        (eng_id, 'Eng. Carlos Eduardo', 'engineer', 'DAILY_LOG_CREATE', 'daily_logs', '1', 'Publicação do Diário de Obra - RDO Casa 42', '177.18.90.201'),
        (admin_id, 'Diretoria Técnica Metrocon', 'admin', 'SYSTEM_AUDIT_VIEW', 'audit_logs', 'all', 'Consulta gerencial aos logs de conformidade LGPD', '177.18.90.100')
    ]
    for uid, uname, urole, act, rtype, rid, det, ip in audit_samples:
        execute_insert(
            'INSERT INTO audit_logs (user_id, user_name, user_role, action, resource_type, resource_id, details, ip_or_session) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (uid, uname, urole, act, rtype, rid, det, ip)
        )

    print('Seed finalizado com sucesso!')

if __name__ == '__main__':
    run_seed()
