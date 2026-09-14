# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from database.connection import execute_query, execute_one, execute_update, execute_insert
from utils.ui_components import render_status_pill
from modules.auth import log_audit

def render_schedule(project: dict, user: dict):
    st.subheader("📅 Cronograma Físico & Visual de Etapas")
    st.caption("Visão integrada de prazos, marcos contratuais e andamento em órgãos públicos.")

    can_edit = user['role'] in ('admin', 'engineer')

    stages = execute_query(
        '''SELECT * FROM schedule_stages 
        WHERE project_id = ? 
        ORDER BY order_index ASC, start_date ASC''',
        (project['id'],)
    )

    if not stages:
        st.info("Nenhuma etapa cadastrada no cronograma deste projeto.")
        if can_edit:
            st.info("Utilize a ferramenta de administração para cadastrar as etapas.")
        return

    # 1. Gráfico de Gantt Interativo (Plotly)
    df_stages = []
    for s in stages:
        s_date = s['start_date'] or datetime.date.today().strftime('%Y-%m-%d')
        e_date = s['end_date'] or s_date
        df_stages.append({
            'Etapa': s['stage_name'],
            'Início': s_date,
            'Término': e_date,
            'Progresso (%)': s['progress_percent'],
            'Status': s['status'].replace('_', ' ').title(),
            'Tipo': s['stage_type'].title()
        })

    df = pd.DataFrame(df_stages)

    try:
        fig = px.timeline(
            df,
            x_start="Início",
            x_end="Término",
            y="Etapa",
            color="Status",
            color_discrete_map={
                'Concluido': '#10B981',
                'Em Andamento': '#3B82F6',
                'Em Analise Orgao': '#F59E0B',
                'A Iniciar': '#9CA3AF',
                'Atrasado': '#EF4444'
            },
            title=f"Linha do Tempo de Execução • {project['title']}",
            hover_data=['Progresso (%)', 'Tipo']
        )
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            height=320 + (len(stages) * 25),
            margin=dict(l=20, r=20, t=50, b=20),
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor="#FAFAFA",
            paper_bgcolor="#FFFFFF"
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Não foi possível gerar a linha do tempo gráfica: {e}")

    st.markdown("---")

    # 2. Detalhamento de cada Etapa
    st.markdown("### 📌 Detalhamento e Status por Etapa")

    for s in stages:
        with st.container():
            st_pill = render_status_pill(s['status'])
            prog = float(s['progress_percent'] or 0.0)

            agency_info = ""
            if s['agency_name'] or s['protocol_number']:
                agency_info = f"🏛️ <strong>Órgão:</strong> {s['agency_name'] or 'N/A'} • 📄 <strong>Protocolo:</strong> <code>{s['protocol_number'] or 'N/A'}</code> • "

            st.html(f"""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px; padding: 1rem; margin-bottom: 0.8rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <strong style="color: #0F2D59; font-size: 1.05rem;">{s['order_index']}. {s['stage_name']}</strong>
                    </div>
                    <div>
                        {st_pill}
                    </div>
                </div>
                <div style="font-size: 0.82rem; color: #64748B; margin-top: 4px;">
                    {agency_info}📅 <strong>Período:</strong> {s['start_date']} até {s['end_date']}
                </div>
                <div style="margin-top: 6px; font-size: 0.86rem; color: #334155;">
                    {s['description'] or 'Sem descrição detalhada.'}
                </div>
            </div>
            """)

            st.progress(prog / 100.0)

            # Se for Engenheiro ou Admin, permitir atualização rápida
            if can_edit:
                with st.expander(f"✏️ Atualizar Etapa: {s['stage_name']}", expanded=False):
                    with st.form(f"form_stage_{s['id']}"):
                        sc1, sc2 = st.columns(2)
                        with sc1:
                            new_prog = st.slider("Percentual de Conclusão (%)", 0.0, 100.0, prog, 5.0, key=f"prog_{s['id']}")
                            new_status = st.selectbox(
                                "Status da Etapa",
                                [
                                    ('a_iniciar', 'A Iniciar'),
                                    ('em_andamento', 'Em Andamento'),
                                    ('em_analise_orgao', 'Em Análise no Órgão'),
                                    ('concluido', 'Concluído'),
                                    ('atrasado', 'Atrasado')
                                ],
                                index=['a_iniciar', 'em_andamento', 'em_analise_orgao', 'concluido', 'atrasado'].index(s['status']),
                                format_func=lambda x: x[1],
                                key=f"stt_{s['id']}"
                            )
                        with sc2:
                            new_st_date = st.date_input("Data de Início", value=datetime.datetime.strptime(s['start_date'], '%Y-%m-%d').date() if s['start_date'] else datetime.date.today(), key=f"std_{s['id']}")
                            new_end_date = st.date_input("Data de Término", value=datetime.datetime.strptime(s['end_date'], '%Y-%m-%d').date() if s['end_date'] else datetime.date.today(), key=f"endd_{s['id']}")

                        btn_update = st.form_submit_button("Salvar Alterações na Etapa", use_container_width=True)
                        if btn_update:
                            execute_update(
                                '''UPDATE schedule_stages 
                                SET progress_percent = ?, status = ?, start_date = ?, end_date = ? 
                                WHERE id = ?''',
                                (new_prog, new_status[0], new_st_date.strftime('%Y-%m-%d'), new_end_date.strftime('%Y-%m-%d'), s['id'])
                            )
                            
                            all_stages = execute_query('SELECT progress_percent FROM schedule_stages WHERE project_id = ?', (project['id'],))
                            if all_stages:
                                avg_prog = round(sum([stg['progress_percent'] for stg in all_stages]) / len(all_stages), 1)
                                execute_update('UPDATE projects SET progress_percent = ? WHERE id = ?', (avg_prog, project['id']))

                            log_audit(user['id'], user['name'], user['role'], 'SCHEDULE_UPDATE', 'schedule_stages', str(s['id']), f"Atualizada etapa '{s['stage_name']}' para {new_prog}% ({new_status[0]})")
                            st.success("✅ Etapa atualizada com sucesso!")
                            st.rerun()
