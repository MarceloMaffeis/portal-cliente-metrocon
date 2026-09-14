# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
from database.connection import execute_query, execute_one, execute_update, execute_insert
from utils.ui_components import render_status_pill
from modules.auth import log_audit

def render_schedule(project: dict, user: dict):
    st.subheader("📅 Cronograma Físico & Visual de Etapas")
    st.caption("Acompanhamento integrado de prazos, marcos contratuais e tramitações em órgãos públicos.")

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
            st.info("Utilize a aba de Gestão Administrativa para cadastrar as etapas.")
        return

    # 1. Resumo em Métricas no Topo
    total_stages = len(stages)
    completed_stages = sum(1 for s in stages if s['status'] == 'concluido')
    in_progress_stages = sum(1 for s in stages if s['status'] in ('em_andamento', 'em_analise_orgao'))
    pending_stages = sum(1 for s in stages if s['status'] == 'a_iniciar')
    
    # Calcular dias restantes até a entrega
    end_date_str = project.get('end_date_estimated')
    days_left_txt = "N/A"
    if end_date_str:
        try:
            end_d = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            diff = (end_d - datetime.date.today()).days
            days_left_txt = f"{diff} dias" if diff >= 0 else f"{abs(diff)} dias em atraso"
        except Exception:
            pass

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Total de Etapas", f"{total_stages} fases")
    with k2:
        st.metric("Etapas Concluídas", f"{completed_stages} de {total_stages}", f"{(completed_stages/total_stages)*100:.0f}% concluído")
    with k3:
        st.metric("Em Andamento / Análise", f"{in_progress_stages} fases")
    with k4:
        st.metric("Prazo Restante", days_left_txt, f"Entrega: {end_date_str}")

    st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

    # 2. Gráfico de Gantt Interativo e Otimizado para Qualquer Tema (Dark e Light)
    df_stages = []
    status_labels = {
        'concluido': 'Concluído (100%)',
        'em_andamento': 'Em Andamento',
        'em_analise_orgao': 'Em Análise no Órgão',
        'a_iniciar': 'A Iniciar',
        'atrasado': 'Atrasado'
    }

    color_map = {
        'Concluído (100%)': '#10B981',     # Verde Esmeralda
        'Em Andamento': '#3B82F6',         # Azul Safira
        'Em Análise no Órgão': '#F59E0B',  # Âmbar Dourado
        'A Iniciar': '#64748B',            # Cinza Ardósia
        'Atrasado': '#EF4444'              # Vermelho Alerta
    }

    for s in stages:
        s_date = s['start_date'] or datetime.date.today().strftime('%Y-%m-%d')
        e_date = s['end_date'] or s_date
        stt_label = status_labels.get(s['status'], s['status'].title())
        prog_val = float(s['progress_percent'] or 0.0)
        
        # Formatar texto da barra
        bar_text = f" {prog_val:.0f}%" if prog_val > 0 else " 0%"
        
        df_stages.append({
            'ID': s['id'],
            'Ordem': s['order_index'],
            'Etapa': f"{s['order_index']}. {s['stage_name']}",
            'NomePuro': s['stage_name'],
            'Início': s_date,
            'Término': e_date,
            'Progresso': f"{prog_val:.0f}%",
            'ProgressoNum': prog_val,
            'Status': stt_label,
            'Tipo': s['stage_type'].title(),
            'Órgão': s['agency_name'] or 'Canteiro / Interno',
            'Protocolo': s['protocol_number'] or 'N/A',
            'TextoBarra': f"{s['stage_name']} ({prog_val:.0f}%)"
        })

    df = pd.DataFrame(df_stages)

    try:
        fig = px.timeline(
            df,
            x_start="Início",
            x_end="Término",
            y="Etapa",
            color="Status",
            color_discrete_map=color_map,
            hover_data={
                'Etapa': False,
                'Início': True,
                'Término': True,
                'Progresso': True,
                'Status': True,
                'Tipo': True,
                'Órgão': True,
                'Protocolo': True
            },
            text="Progresso"
        )
        
        fig.update_yaxes(
            autorange="reversed",
            title=None,
            tickfont=dict(size=12, color="#E2E8F0"),
            gridcolor="rgba(148, 163, 184, 0.15)"
        )
        
        fig.update_xaxes(
            title=None,
            tickfont=dict(size=11, color="#E2E8F0"),
            gridcolor="rgba(148, 163, 184, 0.15)",
            showgrid=True
        )

        fig.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(color="#FFFFFF", size=11, family="Arial Black, Arial, sans-serif"),
            marker=dict(line=dict(width=1, color="rgba(255,255,255,0.3)"))
        )

        fig.update_layout(
            height=280 + (len(stages) * 35),
            margin=dict(l=10, r=20, t=30, b=20),
            font=dict(family="Arial, sans-serif", size=12, color="#E2E8F0"),
            plot_bgcolor="rgba(15, 23, 42, 0.6)",
            paper_bgcolor="rgba(15, 23, 42, 0.85)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(size=11, color="#E2E8F0"),
                bgcolor="rgba(15, 23, 42, 0.5)",
                bordercolor="rgba(148, 163, 184, 0.3)",
                borderwidth=1
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Erro ao renderizar gráfico Gantt: {e}")

    st.markdown("---")

    # 3. Detalhamento e Atualização das Etapas
    st.markdown("### 📌 Detalhamento de Cada Etapa & Ações")

    for s in stages:
        with st.container():
            st_pill = render_status_pill(s['status'])
            prog = float(s['progress_percent'] or 0.0)

            agency_info = ""
            if s['agency_name'] or s['protocol_number']:
                agency_info = f"🏛️ <strong>Órgão:</strong> {s['agency_name'] or 'N/A'} • 📄 <strong>Protocolo:</strong> <code>{s['protocol_number'] or 'N/A'}</code> • "

            st.html(f"""
            <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid #334155; border-radius: 8px; padding: 1.1rem; margin-bottom: 0.8rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div>
                        <strong style="color: #FFFFFF; font-size: 1.05rem;">{s['order_index']}. {s['stage_name']}</strong>
                    </div>
                    <div>
                        {st_pill}
                    </div>
                </div>
                <div style="font-size: 0.82rem; color: #94A3B8; margin-top: 6px;">
                    {agency_info}📅 <strong>Período Previsto:</strong> {s['start_date']} até {s['end_date']}
                </div>
                <div style="margin-top: 6px; font-size: 0.88rem; color: #CBD5E1;">
                    {s['description'] or 'Sem descrição complementar.'}
                </div>
            </div>
            """)

            st.progress(prog / 100.0)

            if can_edit:
                with st.expander(f"✏️ Atualizar Progresso: {s['stage_name']}", expanded=False):
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
