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


def render_overview_table(df_resumo: pd.DataFrame, periodo_str: str, colors: dict, is_dark: bool):
    """Renderiza tabela HTML estilizada com o resumo mensal por área"""
    shadow = 'rgba(0,0,0,0.3)' if is_dark else 'rgba(0,0,0,0.1)'
    row_alt = 'rgba(255,255,255,0.04)' if is_dark else 'rgba(0,0,0,0.03)'

    def pct_color(pct: float) -> str:
        if pct >= 95:
            return colors['success']
        if pct >= 80:
            return '#F39C12'
        return colors['error']

    header = (
        f'<tr style="background-color:{colors["primary"]}; color:#FFFFFF;">'
        '<th style="padding:12px 16px; text-align:left; font-size:14px;">Área</th>'
        '<th style="padding:12px 16px; text-align:center; font-size:14px;">Período</th>'
        '<th style="padding:12px 16px; text-align:right; font-size:14px;">Esperado</th>'
        '<th style="padding:12px 16px; text-align:right; font-size:14px;">Entregue</th>'
        '<th style="padding:12px 16px; text-align:right; font-size:14px;">% Atingimento</th>'
        '</tr>'
    )

    rows_html = ''
    for i, row in df_resumo.iterrows():
        is_total = row['area_nome'] == 'Total'
        bg = colors['card'] if is_total else (row_alt if i % 2 == 0 else 'transparent')
        font_weight = '700' if is_total else '400'
        font_size = '15px' if is_total else '14px'
        pct = float(row['percentual'])
        cor_pct = colors['primary'] if is_total else pct_color(pct)

        rows_html += (
            f'<tr style="background-color:{bg}; font-weight:{font_weight}; font-size:{font_size};">'
            f'<td style="padding:10px 16px; color:{colors["text"]};">{row["area_nome"]}</td>'
            f'<td style="padding:10px 16px; text-align:center; color:{colors["text_secondary"]};">{periodo_str}</td>'
            f'<td style="padding:10px 16px; text-align:right; color:{colors["text"]};">{format_number_br(row["esperado"])}</td>'
            f'<td style="padding:10px 16px; text-align:right; color:{colors["text"]};">{format_number_br(row["entregue"])}</td>'
            f'<td style="padding:10px 16px; text-align:right; color:{cor_pct}; font-weight:700;">{pct:.2f}%</td>'
            '</tr>'
        )

    tabela_html = (
        f'<div style="overflow-x:auto; border-radius:12px; box-shadow:0 4px 15px {shadow};">'
        f'<table style="width:100%; border-collapse:collapse;">'
        f'<thead>{header}</thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table></div>'
    )

    st.markdown(tabela_html, unsafe_allow_html=True)


def render_overview_chart(df_resumo: pd.DataFrame, colors: dict):
    """Renderiza gráfico de barras comparando esperado vs entregue por área (sem linha Total)"""
    df_chart = df_resumo[df_resumo['area_nome'] != 'Total'].copy()
    if df_chart.empty:
        st.info("Nenhum dado disponível para o gráfico.")
        return

    df_chart = df_chart.sort_values('esperado', ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_chart['area_nome'],
        x=df_chart['esperado'],
        name='Esperado',
        orientation='h',
        marker_color=colors['info'],
        text=df_chart['esperado'].apply(lambda v: format_number_br(v)),
        textposition='outside',
        textfont=dict(size=14, color=colors['text']),
    ))

    fig.add_trace(go.Bar(
        y=df_chart['area_nome'],
        x=df_chart['entregue'],
        name='Entregue',
        orientation='h',
        marker_color=colors['success'],
        text=df_chart['entregue'].apply(lambda v: format_number_br(v)),
        textposition='outside',
        textfont=dict(size=14, color=colors['text']),
    ))

    altura = max(400, len(df_chart) * 70)

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text'], size=14),
        xaxis_title="Quantidade",
        yaxis_title="",
        margin=dict(t=20, b=20, l=10, r=80),
        height=altura,
        bargap=0.25,
        bargroupgap=0.08,
        xaxis=dict(
            title=dict(font=dict(color=colors['text'], size=16)),
            tickfont=dict(color=colors['text'], size=13),
        ),
        yaxis=dict(tickfont=dict(color=colors['text'], size=14)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=colors['text'], size=14)
        )
    )

    st.plotly_chart(fig, use_container_width=True)


def render_overview_failure_chart(df_falhas: pd.DataFrame, colors: dict):
    """
    Gráfico de barras empilhadas horizontais mostrando volume de falhas
    por tipo em cada área — para justificar o não atingimento na visão geral.
    """
    if df_falhas.empty:
        st.info("Nenhuma falha registrada no período selecionado.")
        return

    tipos = df_falhas['tipo_falha_desc'].dropna().unique().tolist()
    areas = sorted(df_falhas['area_nome'].unique().tolist())

    fig = go.Figure()

    for tipo in tipos:
        cor = FAILURE_COLORS.get(tipo, colors['text_secondary'])
        valores = []
        textos = []
        for area in areas:
            mask = (df_falhas['area_nome'] == area) & (df_falhas['tipo_falha_desc'] == tipo)
            qtd = int(df_falhas.loc[mask, 'quantidade'].sum())
            valores.append(qtd)
            textos.append(str(qtd) if qtd > 0 else '')

        fig.add_trace(go.Bar(
            name=tipo,
            y=areas,
            x=valores,
            orientation='h',
            marker_color=cor,
            text=textos,
            textposition='inside',
            insidetextanchor='middle',
            textfont=dict(size=13, color='#FFFFFF'),
        ))

    total_por_area = df_falhas.groupby('area_nome')['quantidade'].sum()
    altura = max(350, len(areas) * 55)

    fig.update_layout(
        barmode='stack',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text'], size=13),
        xaxis_title="Quantidade de Falhas",
        yaxis_title="",
        margin=dict(t=20, b=20, l=10, r=20),
        height=altura,
        bargap=0.3,
        xaxis=dict(
            title=dict(font=dict(color=colors['text'], size=15)),
            tickfont=dict(color=colors['text'], size=13),
        ),
        yaxis=dict(tickfont=dict(color=colors['text'], size=14)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color=colors['text'], size=13)
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    total_geral = int(df_falhas['quantidade'].sum())
    st.caption(f"Total de falhas no período: **{total_geral}**")


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
