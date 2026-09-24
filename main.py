"""
Painel de Gestão de Entregáveis RPA - Grupo Odilon Santos
View Layer (Interface do Usuário)
"""

import streamlit as st
import pandas as pd
import io
import calendar
from datetime import datetime, timedelta

from controllers.main_controller import MainController
from utils.constants import AREAS_MAP, COLORS_DARK, COLORS_LIGHT
from utils.helpers import setup_locale
from utils.styles import get_custom_css
from utils.ui_components import (
    render_logo,
    render_logo_centered,
    render_kpi_cards,
    render_comparison_chart,
    render_health_donut,
    render_failure_breakdown,
    render_overview_table,
    render_overview_chart,
)

setup_locale()

st.set_page_config(
    page_title="RPA Analytics | Grupo Odilon Santos",
    layout="wide"
)

if 'tema_escuro' not in st.session_state:
    st.session_state.tema_escuro = True

if 'area_atual' not in st.session_state:
    st.session_state.area_atual = None

if 'visao_geral' not in st.session_state:
    st.session_state.visao_geral = False

COLORS = COLORS_DARK if st.session_state.tema_escuro else COLORS_LIGHT

st.markdown(get_custom_css(COLORS, st.session_state.tema_escuro), unsafe_allow_html=True)

controller = MainController()


def render_home_screen():
    """Renderiza tela inicial com grid de seleção de áreas"""
    col_logo, col_title, col_theme = st.columns([1, 5, 1])

    with col_logo:
        render_logo('assets/osac.jpg', 80, COLORS)

    with col_title:
        st.markdown(
            f"<h1 style='color:{COLORS['primary']}; margin-bottom:10px; margin-top:10px;'>"
            "Sensor de Eficiência RPA</h1>",
            unsafe_allow_html=True
        )

    with col_theme:
        tema_icon = "☀️" if st.session_state.tema_escuro else "🌙"
        tema_label = "Claro" if st.session_state.tema_escuro else "Escuro"
        if st.button(f"{tema_icon} {tema_label}", use_container_width=True, key="toggle_theme_home"):
            st.session_state.tema_escuro = not st.session_state.tema_escuro
            st.rerun()

    st.markdown(
        f"<p style='text-align:center; font-size:18px; color:{COLORS['text_secondary']};'>"
        "Selecione a área para monitorar a saúde e a qualidade das entregas</p>",
        unsafe_allow_html=True
    )
    st.write("---")

    with st.spinner("Carregando dados..."):
        df_rpa = controller.load_data()
    contagem_por_area = controller.get_area_counts(df_rpa)

    # Filtrar apenas áreas com execuções (valor > 0)
    areas_com_dados = {
        sigla: nome_area
        for sigla, nome_area in AREAS_MAP.items()
        if contagem_por_area.get(nome_area, 0) > 0
    }

    if not areas_com_dados:
        st.warning("Nenhuma área com execuções encontrada no momento.")
        return

    if st.button("Visão Geral — Todas as Áreas", use_container_width=True, key="btn_visao_geral"):
        st.session_state.visao_geral = True
        st.rerun()

    st.write("")

    cols = st.columns(3)
    for idx, (sigla, nome_area) in enumerate(areas_com_dados.items()):
        with cols[idx % 3]:
            qtd_execucoes = contagem_por_area.get(nome_area, 0)
            label = f"{nome_area} ({qtd_execucoes})"

            if st.button(label, use_container_width=True, key=f"btn_{sigla}"):
                st.session_state.area_atual = nome_area
                st.rerun()


def render_sidebar(df_area: pd.DataFrame):
    """Renderiza sidebar com filtros"""
    with st.sidebar:
        render_logo_centered('assets/osac.jpg', 50, COLORS)

        st.markdown(
            f"<h2 style='color:{COLORS['primary']}; text-align:center; margin-top:5px; margin-bottom:3px;'>"
            "Gestão de Entregáveis</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='color:{COLORS['text']}; text-align:center; margin-top:0px; margin-bottom:8px;'>"
            f"{st.session_state.area_atual}</h3>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<h4 style='color:{COLORS['primary']}; margin-top:3px; margin-bottom:8px;'>Filtros</h4>",
            unsafe_allow_html=True
        )

        if st.button("🔄 Atualizar", use_container_width=True, key="refresh_data"):
            controller.clear_cache()
            st.rerun()

        lista_processos = sorted(df_area['nome_processo'].unique())
        fluxos_selecionados = st.multiselect(
            "Fluxo / Processo",
            options=lista_processos,
            placeholder="Todos"
        )

        tipos_selecionados = []
        if 'tipo_fluxo' in df_area.columns:
            lista_tipos = sorted(df_area['tipo_fluxo'].unique())
            tipos_selecionados = st.multiselect(
                "Tipo de Fluxo",
                options=lista_tipos,
                placeholder="Todos"
            )

        status_selecionados = []
        if 'status' in df_area.columns:
            lista_status = sorted(df_area['status'].unique())
            status_selecionados = st.multiselect(
                "Status",
                options=lista_status,
                placeholder="Todos"
            )

        falhas_selecionadas = []
        if 'tipo_falha_desc' in df_area.columns and df_area['tipo_falha_desc'].notna().any():
            lista_falhas = sorted(df_area['tipo_falha_desc'].dropna().unique())
            falhas_selecionadas = st.multiselect(
                "Tipo de Falha",
                options=lista_falhas,
                placeholder="Todos"
            )

        periodo = None
        if 'data_inicio_dt' in df_area.columns and not df_area['data_inicio_dt'].isna().all():
            data_minima = df_area['data_inicio_dt'].min().date()
            data_maxima = df_area['data_inicio_dt'].max().date()

            hoje = datetime.now().date()
            inicio_mes_atual = hoje.replace(day=1)
            default_inicio = min(max(inicio_mes_atual, data_minima), data_maxima)
            default_fim = max(min(hoje, data_maxima), data_minima)

            periodo = st.date_input(
                "Período",
                [default_inicio, default_fim],
                min_value=data_minima,
                max_value=data_maxima,
                format="DD/MM/YYYY"
            )

        st.markdown(
            f"<h4 style='color:{COLORS['primary']}; margin-top:10px; margin-bottom:8px;'>Relatório</h4>",
            unsafe_allow_html=True
        )

    return fluxos_selecionados, tipos_selecionados, status_selecionados, falhas_selecionadas, periodo


def render_dashboard_screen():
    """Renderiza dashboard detalhado da área"""
    with st.spinner("Carregando dados..."):
        df_rpa = controller.load_data()
    df_area = controller.get_area_data(df_rpa, st.session_state.area_atual)

    head_left, head_mid, head_right = st.columns([4, 1, 1])
    head_left.title(f"Gestão de Entregáveis — {st.session_state.area_atual}")

    with head_mid:
        tema_icon = "☀️" if st.session_state.tema_escuro else "🌙"
        tema_label = "Claro" if st.session_state.tema_escuro else "Escuro"
        if st.button(f"{tema_icon} {tema_label}", use_container_width=True, key="toggle_theme_dashboard"):
            st.session_state.tema_escuro = not st.session_state.tema_escuro
            st.rerun()

    if head_right.button("Voltar", use_container_width=True):
        st.session_state.area_atual = None
        st.rerun()

    st.write("---")

    if df_area.empty:
        st.warning(
            f"Nenhum processo em produção encontrado para a área "
            f"{st.session_state.area_atual} no momento."
        )

        with st.expander("🔍 Informações de Debug"):
            st.write(f"Total de registros carregados: {len(df_rpa)}")
            if not df_rpa.empty:
                st.write(f"Áreas disponíveis: {df_rpa['area_nome'].unique().tolist()}")
                st.write("Total por área:")
                st.write(df_rpa['area_nome'].value_counts())
        return

    fluxos_sel, tipos_sel, status_sel, falhas_sel, periodo = render_sidebar(df_area)

    df_filtrado = controller.apply_filters(
        df_area,
        processos=fluxos_sel,
        tipos_fluxo=tipos_sel,
        status=status_sel,
        tipos_falha=falhas_sel,
        periodo=periodo
    )

    kpi = controller.calculate_kpis(df_filtrado)
    df_falhas = controller.get_failure_breakdown(df_filtrado)
    render_kpi_cards(kpi, st.session_state.area_atual, COLORS, st.session_state.tema_escuro, df_falhas)

    st.write("##")

    st.markdown(
        f"<h4 style='color:{COLORS['primary']};'>Comparação: Esperado vs Entregue por Processo</h4>",
        unsafe_allow_html=True
    )
    df_comparacao = controller.prepare_comparison_chart_data(df_filtrado)
    render_comparison_chart(df_comparacao, COLORS)

    st.write("##")
    col_saude, col_falhas = st.columns(2)

    with col_saude:
        st.markdown(
            f"<h4 style='color:{COLORS['primary']};'>Saúde e Qualidade de Entrega</h4>",
            unsafe_allow_html=True
        )
        render_health_donut(kpi, COLORS)

    with col_falhas:
        st.markdown(
            f"<h4 style='color:{COLORS['primary']};'>Tipos de Falha</h4>",
            unsafe_allow_html=True
        )
        render_failure_breakdown(df_falhas, COLORS)

    st.write("---")
    st.markdown(
        f"<h3 style='color:{COLORS['primary']};'>Detalhamento das Execuções</h3>",
        unsafe_allow_html=True
    )

    df_exibir = controller.prepare_display_table(df_filtrado)
    st.dataframe(df_exibir, use_container_width=True, height=400)
    st.caption(f"Total de {len(df_exibir)} execuções exibidas")

    if not df_filtrado.empty:
        with st.sidebar:
            df_excel = controller.prepare_excel_export(df_filtrado)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_excel.to_excel(writer, index=False, sheet_name='Entregas RPA')

            st.download_button(
                label="📥 Baixar Relatório Excel",
                data=buffer.getvalue(),
                file_name=f"RPA_{st.session_state.area_atual.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )


MESES_PT = {
    1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
    5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
    9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
}


def render_overview_screen():
    """Renderiza tela de visão geral mensal consolidada por área"""
    col_logo, col_title, col_theme, col_back = st.columns([1, 4, 1, 1])

    with col_logo:
        render_logo('assets/osac.jpg', 80, COLORS)

    with col_title:
        st.markdown(
            f"<h1 style='color:{COLORS['primary']}; margin-bottom:10px; margin-top:10px;'>"
            "Visão Geral — Todas as Áreas</h1>",
            unsafe_allow_html=True
        )

    with col_theme:
        tema_icon = "☀️" if st.session_state.tema_escuro else "🌙"
        tema_label = "Claro" if st.session_state.tema_escuro else "Escuro"
        if st.button(f"{tema_icon} {tema_label}", use_container_width=True, key="toggle_theme_overview"):
            st.session_state.tema_escuro = not st.session_state.tema_escuro
            st.rerun()

    with col_back:
        if st.button("Voltar", use_container_width=True, key="back_overview"):
            st.session_state.visao_geral = False
            st.rerun()

    st.write("---")

    # Período padrão: mês anterior
    hoje = datetime.now()
    primeiro_dia_mes_atual = hoje.replace(day=1)
    ultimo_dia_mes_passado = primeiro_dia_mes_atual - timedelta(days=1)
    mes_default = ultimo_dia_mes_passado.month
    ano_default = ultimo_dia_mes_passado.year

    col_mes, col_ano, col_refresh = st.columns([2, 2, 1])

    with col_mes:
        mes_selecionado = st.selectbox(
            "Mês",
            options=list(MESES_PT.keys()),
            format_func=lambda m: MESES_PT[m],
            index=mes_default - 1,
            key="overview_mes"
        )

    with col_ano:
        anos_disponiveis = list(range(2024, hoje.year + 1))
        ano_selecionado = st.selectbox(
            "Ano",
            options=anos_disponiveis,
            index=anos_disponiveis.index(ano_default) if ano_default in anos_disponiveis else len(anos_disponiveis) - 1,
            key="overview_ano"
        )

    with col_refresh:
        st.markdown("<div style='margin-top:28px;'></div>", unsafe_allow_html=True)
        if st.button("Atualizar", use_container_width=True, key="refresh_overview"):
            controller.clear_cache()
            st.rerun()

    with st.spinner("Carregando dados..."):
        df_rpa = controller.load_data()

    df_resumo = controller.get_monthly_overview(df_rpa, ano_selecionado, mes_selecionado)

    if df_resumo.empty:
        st.warning(
            f"Nenhum dado encontrado para {MESES_PT[mes_selecionado]}/{ano_selecionado}. "
            "Verifique se há execuções registradas neste período."
        )
        return

    ultimo_dia = calendar.monthrange(ano_selecionado, mes_selecionado)[1]
    periodo_str = f"01/{mes_selecionado:02d} a {ultimo_dia:02d}/{mes_selecionado:02d}/{ano_selecionado}"

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    render_overview_table(df_resumo, periodo_str, COLORS, st.session_state.tema_escuro)

    st.write("##")

    st.markdown(
        f"<h4 style='color:{COLORS['primary']};'>Comparação: Esperado vs Entregue por Área</h4>",
        unsafe_allow_html=True
    )
    render_overview_chart(df_resumo, COLORS)


if st.session_state.visao_geral:
    render_overview_screen()
elif st.session_state.area_atual is None:
    render_home_screen()
else:
    render_dashboard_screen()
