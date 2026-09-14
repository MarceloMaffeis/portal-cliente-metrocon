# -*- coding: utf-8 -*-
import streamlit as st
import os
from PIL import Image, ImageDraw

COMPANY_NAME = "METROCON ENGENHARIA E CONSTRUÇÕES LTDA"
COMPANY_CNPJ = "07.427.908/0001-25"
COMPANY_CREA = "CREA-SP 0742790-PJ"
COMPANY_PHONE = "(11) 3456-7800 / (11) 98765-4321"
COMPANY_EMAIL = "contato@metrocon.com.br"

def apply_custom_css():
    st.html("""
    <style>
        .metrocon-header {
            background: linear-gradient(135deg, #0A192F 0%, #172A46 50%, #0F2D59 100%);
            color: #FFFFFF;
            padding: 1.25rem 1.6rem;
            border-radius: 12px;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }
        .metrocon-title {
            font-size: 1.35rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin: 0;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .metrocon-badge {
            background-color: #E65100;
            color: white;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metrocon-sub {
            font-size: 0.82rem;
            color: #CBD5E1;
            margin-top: 4px;
        }
        .metric-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 10px;
            padding: 1.1rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.03);
            transition: transform 0.15s ease, box-shadow 0.15s ease;
            height: 100%;
        }
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.06);
            border-color: #CBD5E1;
        }
        .metric-label {
            font-size: 0.8rem;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }
        .metric-value {
            font-size: 1.45rem;
            font-weight: 800;
            color: #0F2D59;
            margin-bottom: 4px;
        }
        .metric-sub {
            font-size: 0.78rem;
            color: #475569;
        }
        .status-pill {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }
        .status-em_andamento { background-color: #DBEAFE; color: #1E40AF; border: 1px solid #BFDBFE; }
        .status-em_aprovacao_orgao { background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .status-em_analise_orgao { background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }
        .status-concluido { background-color: #D1FAE5; color: #065F46; border: 1px solid #A7F3D0; }
        .status-planejamento { background-color: #F1F5F9; color: #475569; border: 1px solid #E2E8F0; }
        .status-pausado { background-color: #FEE2E2; color: #991B1B; border: 1px solid #FECACA; }
        .status-atrasado { background-color: #FEE2E2; color: #B91C1C; border: 1px solid #FCA5A5; }
        .status-a_iniciar { background-color: #F3F4F6; color: #374151; border: 1px solid #E5E7EB; }
        .type-pill {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.3px;
        }
        .type-obra { background-color: #E0E7FF; color: #3730A3; }
        .type-reforma { background-color: #EDE9FE; color: #5B21B6; }
        .type-administrativo { background-color: #FEF3C7; color: #78350F; }
        .metrocon-footer {
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid #E2E8F0;
            text-align: center;
            font-size: 0.78rem;
            color: #94A3B8;
        }
    </style>
    """)

def render_header(project=None, user=None):
    apply_custom_css()
    role_labels = {'admin': 'Administrador / Diretoria', 'engineer': 'Engenheiro Responsável', 'client': 'Portal do Cliente'}
    user_role_label = role_labels.get(user['role'] if user else 'client', 'Usuário')
    user_name = user['name'] if user else 'Convidado'
    project_html = ""
    if project:
        t_cls = f"type-{project['type']}"
        s_cls = f"status-{project['status']}"
        s_dict = {'planejamento': 'Planejamento', 'em_andamento': 'Em Andamento', 'em_aprovacao_orgao': 'Em Aprovação no Órgão', 'concluido': 'Concluído', 'pausado': 'Pausado'}
        s_txt = s_dict.get(project['status'], project['status'])
        t_dict = {'obra': 'Construção Civil', 'reforma': 'Reforma & Retrofit', 'administrativo': 'Processo Administrativo'}
        t_txt = t_dict.get(project['type'], project['type'])
        project_html = f"""
        <div style="margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.15);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
            <div><strong style="color:#FFF;font-size:1.05rem;">📍 {project['title']}</strong><span class="type-pill {t_cls}" style="margin-left:8px;">{t_txt}</span></div>
            <div style="display:flex;align-items:center;gap:8px;"><span style="font-size:0.8rem;color:#CBD5E1;">Status:</span><span class="status-pill {s_cls}">{s_txt}</span></div>
        </div>
        """

    html = f"""
    <div class="metrocon-header">
        <div style="flex:1;">
            <div class="metrocon-title">🏢 {COMPANY_NAME}<span class="metrocon-badge">Portal do Cliente</span></div>
            <div class="metrocon-sub">CNPJ: {COMPANY_CNPJ} • {COMPANY_CREA} • Canal Oficial e Seguro</div>
            {project_html}
        </div>
        <div style="text-align:right;min-width:170px;">
            <div style="font-size:0.85rem;font-weight:700;color:#FFF;">👤 {user_name}</div>
            <div style="font-size:0.75rem;color:#CBD5E1;">{user_role_label}</div>
        </div>
    </div>
    """
    st.html(html)

def render_status_pill(status: str) -> str:
    s_dict = {'planejamento': 'Planejamento', 'em_andamento': 'Em Andamento', 'em_aprovacao_orgao': 'Em Aprovação no Órgão', 'em_analise_orgao': 'Em Análise no Órgão', 'concluido': 'Concluído', 'pausado': 'Pausado', 'atrasado': 'Atrasado', 'a_iniciar': 'A Iniciar'}
    label = s_dict.get(status, status)
    return f'<span class="status-pill status-{status}">{label}</span>'

def render_type_pill(p_type: str) -> str:
    t_dict = {'obra': 'Construção', 'reforma': 'Reforma', 'administrativo': 'Administrativo'}
    label = t_dict.get(p_type, p_type)
    return f'<span class="type-pill type-{p_type}">{label}</span>'

def render_footer():
    st.html(f'<div class="metrocon-footer"><p><strong>{COMPANY_NAME}</strong> • CNPJ: {COMPANY_CNPJ}</p><p>Segurança e Privacidade: Todos os acessos e downloads são registrados em conformidade com a LGPD (Lei 13.709/2018).</p><p>Suporte Técnico: {COMPANY_EMAIL} • {COMPANY_PHONE}</p></div>')

def create_sample_image(output_path: str, title: str, subtitle: str, bg_color=(23, 42, 70)):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = Image.new('RGB', (800, 500), color=bg_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([(15, 15), (785, 485)], outline=(230, 81, 0), width=3)
    draw.text((35, 50), "METROCON ENGENHARIA E CONSTRUCOES", fill=(255, 255, 255))
    draw.text((35, 90), f"REGISTRO FOTOGRAFICO: {title.upper()}", fill=(255, 220, 150))
    draw.text((35, 140), subtitle, fill=(210, 225, 245))
    draw.text((35, 430), "DOCUMENTO OFICIAL • PORTAL DO CLIENTE METROCON", fill=(180, 190, 205))
    img.save(output_path, 'JPEG', quality=90)

def create_sample_pdf(output_path: str, title: str, doc_type: str, project_name: str, date_str: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    pdf_content = (
        b'%PDF-1.4\n'
        b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
        b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n'
        b'4 0 obj\n<< /Length 320 >>\nstream\n'
        b'BT /F1 16 Tf 50 720 Td (METROCON ENGENHARIA E CONSTRUCOES) Tj ET\n'
        b'BT /F1 12 Tf 50 690 Td (CNPJ: 07.427.908/0001-25 - CREA-SP 0742790-PJ) Tj ET\n'
        b'BT /F1 13 Tf 50 640 Td (DOCUMENTO: ' + title.encode('ascii', 'replace') + b') Tj ET\n'
        b'BT /F1 11 Tf 50 610 Td (Projeto: ' + project_name.encode('ascii', 'replace') + b') Tj ET\n'
        b'BT /F1 10 Tf 50 580 Td (Data: ' + date_str.encode('ascii', 'replace') + b') Tj ET\n'
        b'BT /F1 9 Tf 50 540 Td (Documento oficial registrado no Portal do Cliente Metrocon.) Tj ET\n'
        b'endstream\nendobj\n'
        b'xref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000276 00000 n \n'
        b'trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n650\n%%EOF\n'
    )
    with open(output_path, 'wb') as f:
        f.write(pdf_content)
