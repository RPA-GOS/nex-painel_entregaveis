"""
Componentes reutilizáveis de UI.
"""

import streamlit as st
import base64
import plotly.graph_objects as go
import pandas as pd
from utils.helpers import format_number_br
from utils.constants import FAILURE_COLORS, TIPO_FALHA_NAO_CLASSIFICADO


def render_logo(image_path: str, size: int, colors: dict):
    """Renderiza logo com círculo"""
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()

    st.markdown(f'''
        <div class="logo-circle">
            <img src="data:image/jpeg;base64,{img_b64}" width="{size}">
        </div>
    ''', unsafe_allow_html=True)


def render_logo_centered(image_path: str, size: int, colors: dict):
    """Renderiza logo centralizada"""
    with open(image_path, 'rb') as f:
        img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()

    st.markdown(f'''
        <div class="logo-sidebar-center">
            <div class="logo-circle">
                <img src="data:image/jpeg;base64,{img_b64}" width="{size}">
            </div>
        </div>
    ''', unsafe_allow_html=True)


def _kpi_card_html(colors: dict, shadow: str, border_color: str, label: str, value) -> str:
    """Monta o HTML de um card de KPI em uma única linha (sem quebras/indentação)"""
    return (
        f'<div style="background-color: {colors["card"]}; padding: 20px; border-radius: 12px; '
        f'border-left: 5px solid {border_color}; box-shadow: 0 4px 15px {shadow}; min-width: 150px;">'
        f'<div style="color: {colors["text_secondary"]}; font-weight: 600; font-size: 14px;">{label}</div>'
        f'<div style="color: {colors["text"]}; font-size: 2rem; font-weight: 700;">{value}</div>'
        f'</div>'
    )


def render_kpi_cards(kpi, area_nome: str, colors: dict, is_dark: bool, df_falhas: pd.DataFrame = None):
    """Renderiza cards de KPI com scroll horizontal, incluindo a contagem por tipo de falha"""
    shadow = 'rgba(0,0,0,0.3)' if is_dark else 'rgba(0,0,0,0.1)'

    kpi_dict = kpi.to_dict()
    volume_fmt = format_number_br(kpi_dict['volume_entregue'])
    esperado_fmt = format_number_br(kpi_dict['resultado_esperado_total'])
    entregue_fmt = format_number_br(kpi_dict['resultado_entregue_total'])

    cards = [
        _kpi_card_html(colors, shadow, colors['primary'], 'Total de Disparos', kpi_dict['total_disparos']),
        _kpi_card_html(colors, shadow, colors['primary'], f'Volume ({area_nome})', volume_fmt),
        _kpi_card_html(colors, shadow, colors['primary'], 'Health Score', f"{kpi_dict['health_score']}%"),
        _kpi_card_html(colors, shadow, colors['primary'], '% Atingimento', f"{kpi_dict['percentual_atingimento']}%"),
        _kpi_card_html(colors, shadow, colors['primary'], 'Esperado', esperado_fmt),
        _kpi_card_html(colors, shadow, colors['primary'], 'Entregue', entregue_fmt),
    ]

    if df_falhas is not None and not df_falhas.empty:
        total_falhas = int(df_falhas['quantidade'].sum())
        cards.append(_kpi_card_html(colors, shadow, colors['error'], 'Total de Falhas', total_falhas))

        df_ordenado = df_falhas.copy()
        df_ordenado['_nao_classificado'] = df_ordenado['tipo_falha_desc'].eq(TIPO_FALHA_NAO_CLASSIFICADO)
        df_ordenado = df_ordenado.sort_values(by=['_nao_classificado', 'quantidade'], ascending=[True, False])

        for _, row in df_ordenado.iterrows():
            tipo = row['tipo_falha_desc']
            quantidade = int(row['quantidade'])
            cards.append(_kpi_card_html(colors, shadow, colors['error'], tipo, quantidade))

    st.markdown(f'<div class="kpi-scroll-wrapper">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_comparison_chart(df_comparacao: pd.DataFrame, colors: dict):
    """Renderiza gráfico de comparação esperado vs entregue"""
    if df_comparacao.empty:
        st.info("Nenhum dado disponível para comparação")
        return

    fig = go.Figure()

    tem_verba = (
        'resultado_verba_insuficiente' in df_comparacao.columns
        and df_comparacao['resultado_verba_insuficiente'].sum() > 0
    )

    fig.add_trace(go.Bar(
        y=df_comparacao['nome_processo'],
        x=df_comparacao['resultado_esperado'],
        name='Esperado',
        orientation='h',
        marker_color=colors['info'],
        text=df_comparacao['resultado_esperado'],
        textposition='outside',
        textfont=dict(size=18, color=colors['text']),
    ))

    fig.add_trace(go.Bar(
        y=df_comparacao['nome_processo'],
        x=df_comparacao['resultado_entregue'],
        name='Entregue',
        orientation='h',
        marker_color=colors['success'],
        text=df_comparacao['resultado_entregue'],
        textposition='outside',
        textfont=dict(size=18, color=colors['text']),
    ))

    if tem_verba:
        fig.add_trace(go.Bar(
            y=df_comparacao['nome_processo'],
            x=df_comparacao['resultado_verba_insuficiente'],
            name='Verba Insuficiente',
            orientation='h',
            marker_color='#EF7D1E',
            text=[str(v) if v > 0 else '' for v in df_comparacao['resultado_verba_insuficiente']],
            textposition='outside',
            textfont=dict(size=18, color=colors['text']),
        ))

    barras_por_processo = 3 if tem_verba else 2
    altura_grafico = max(500, len(df_comparacao) * barras_por_processo * 40)

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text'], size=16),
        xaxis_title="Quantidade",
        yaxis_title="",
        margin=dict(t=20, b=20, l=10, r=80),
        height=altura_grafico,
        bargap=0.25,
        bargroupgap=0.08,
        xaxis=dict(
            title=dict(font=dict(color=colors['text'], size=20)),
            tickfont=dict(color=colors['text'], size=18)
        ),
        yaxis=dict(
            tickfont=dict(color=colors['text'], size=18)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=colors['text'], size=18)
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def render_failure_breakdown(df_falhas: pd.DataFrame, colors: dict):
    """Renderiza gráfico de barras com a distribuição de falhas por tipo (S/H/P)"""
    if df_falhas.empty:
        st.info("Nenhuma falha registrada no período/filtro selecionado.")
        return

    bar_colors = [
        FAILURE_COLORS.get(tipo, colors['text_secondary'])
        for tipo in df_falhas['tipo_falha_desc']
    ]

    fig = go.Figure(go.Bar(
        y=df_falhas['tipo_falha_desc'],
        x=df_falhas['quantidade'],
        orientation='h',
        marker_color=bar_colors,
        text=df_falhas['quantidade'],
        textposition='outside',
        textfont=dict(size=18, color=colors['text']),
        cliponaxis=False,
    ))

    maior_valor = int(df_falhas['quantidade'].max())

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text'], size=14),
        xaxis_title="Quantidade de Falhas",
        yaxis_title="",
        margin=dict(t=20, b=20, l=10, r=60),
        height=max(220, len(df_falhas) * 70),
        showlegend=False,
        xaxis=dict(
            title=dict(font=dict(color=colors['text'], size=16)),
            tickfont=dict(color=colors['text'], size=14),
            range=[0, maior_valor * 1.2],
        ),
        yaxis=dict(
            tickfont=dict(color=colors['text'], size=15)
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    total_falhas = int(df_falhas['quantidade'].sum())
    linha_nc = df_falhas.loc[df_falhas['tipo_falha_desc'] == TIPO_FALHA_NAO_CLASSIFICADO, 'quantidade']
    nao_classificado = int(linha_nc.sum())

    if nao_classificado > 0:
        percentual = nao_classificado / total_falhas * 100
        st.caption(
            f"⚠️ {nao_classificado} de {total_falhas} falhas ({percentual:.0f}%) são "
            "**Não Classificadas** — sem tipo de falha preenchido."
        )


def render_verba_insuficiente_section(df_verba: pd.DataFrame, colors: dict):
    """Renderiza seção destacada para registros de Verba Insuficiente"""
    if df_verba.empty:
        return

    total_ocorrencias = len(df_verba)

    st.markdown(
        f"""
        <div style="
            background-color: rgba(239, 125, 30, 0.10);
            border: 2px solid #EF7D1E;
            border-radius: 12px;
            padding: 18px 24px;
            margin-bottom: 10px;
        ">
            <div style="font-size: 16px; font-weight: 700; color: #EF7D1E; margin-bottom: 10px;">
                Verba Insuficiente
            </div>
            <div>
                <div style="color: {colors['text_secondary']}; font-size: 13px; font-weight: 600;">Ocorrências</div>
                <div style="color: {colors['text']}; font-size: 1.8rem; font-weight: 700;">{total_ocorrencias}</div>
            </div>
            <div style="color: {colors['text_secondary']}; font-size: 12px; margin-top: 10px;">
                Esses registros <strong>não contam como falha de entrega</strong>.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_health_donut(kpi, colors: dict):
    """Renderiza gráfico donut de saúde"""
    kpi_dict = kpi.to_dict()

    labels = ['Sucesso (Concluído)', 'Verba Insuficiente', 'Falhas/Atenção']
    values = [
        kpi_dict['execucoes_concluidas'],
        kpi_dict['verba_insuficiente'],
        kpi_dict['execucoes_falhadas']
    ]
    marker_colors = [colors['success'], '#EF7D1E', colors['error']]

    # Remove fatias zeradas para não poluir a legenda
    filtered = [(l, v, c) for l, v, c in zip(labels, values, marker_colors) if v > 0]
    if filtered:
        labels, values, marker_colors = zip(*filtered)

    fig = go.Figure(go.Pie(
        labels=list(labels),
        values=list(values),
        hole=.65,
        marker_colors=list(marker_colors)
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text'], size=13),
        showlegend=True,
        margin=dict(t=30, b=10, l=10, r=10),
        height=350,
        legend=dict(
            font=dict(color=colors['text'], size=13)
        )
    )

    st.plotly_chart(fig, use_container_width=True)
