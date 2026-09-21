"""
Controller principal da aplicação.
Orquestra a comunicação entre serviços e a view.
"""

import streamlit as st
import pandas as pd
from services.api_service import APIService
from services.data_service import DataService
from utils.constants import CACHE_TTL_SECONDS


class MainController:
    """Orquestra a lógica de negócio da aplicação"""

    def __init__(self):
        self.api_service = APIService()
        self.data_service = DataService()

    @st.cache_data(ttl=CACHE_TTL_SECONDS)
    def load_data(_self) -> pd.DataFrame:
        """
        Carrega e processa dados da API.

        Returns:
            DataFrame processado
        """
        raw_data = _self.api_service.fetch_entregaveis()
        return _self.data_service.process_raw_data(raw_data)

    def get_area_data(self, df: pd.DataFrame, area_nome: str) -> pd.DataFrame:
        """
        Filtra dados por área.

        Args:
            df: DataFrame completo
            area_nome: Nome da área

        Returns:
            DataFrame filtrado
        """
        return self.data_service.filter_by_area(df, area_nome)

    def get_area_counts(self, df: pd.DataFrame) -> dict:
        """
        Obtém contagem de execuções por área.

        Args:
            df: DataFrame completo

        Returns:
            Dicionário com contagens
        """
        return self.data_service.get_area_counts(df)

    def calculate_kpis(self, df: pd.DataFrame):
        """
        Calcula KPIs do DataFrame.

        Args:
            df: DataFrame filtrado

        Returns:
            Objeto KPI
        """
        return self.data_service.calculate_kpis(df)

    def get_verba_insuficiente_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna registros de Verba Insuficiente para exibição separada.

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame com registros de Verba Insuficiente
        """
        return self.data_service.prepare_verba_insuficiente_data(df)

    def prepare_comparison_chart_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para gráfico de comparação.

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame agrupado
        """
        return self.data_service.prepare_comparison_data(df)

    def get_failure_breakdown(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Obtém contagem de falhas por tipo (Sistema/Humana/Desenvolvimento).

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame com contagem por tipo de falha
        """
        return self.data_service.get_failure_breakdown(df)

    def prepare_display_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para tabela de exibição.

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame formatado
        """
        return self.data_service.prepare_table_data(df)

    def apply_filters(
        self,
        df: pd.DataFrame,
        processos: list = None,
        tipos_fluxo: list = None,
        status: list = None,
        tipos_falha: list = None,
        periodo: tuple = None
    ) -> pd.DataFrame:
        """
        Aplica filtros ao DataFrame.

        Args:
            df: DataFrame a ser filtrado
            processos: Lista de processos selecionados
            tipos_fluxo: Lista de tipos de fluxo selecionados
            status: Lista de status selecionados
            tipos_falha: Lista de tipos de falha selecionados
            periodo: Tupla com datas (inicio, fim)

        Returns:
            DataFrame filtrado
        """
        df_filtered = df.copy()

        if processos:
            df_filtered = df_filtered[df_filtered['nome_processo'].isin(processos)]

        if tipos_fluxo and 'tipo_fluxo' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['tipo_fluxo'].isin(tipos_fluxo)]

        if status and 'status' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['status'].isin(status)]

        if tipos_falha and 'tipo_falha_desc' in df_filtered.columns:
            df_filtered = df_filtered[df_filtered['tipo_falha_desc'].isin(tipos_falha)]

        if periodo and 'data_inicio_dt' in df_filtered.columns:
            if isinstance(periodo, (list, tuple)) and len(periodo) == 2:
                df_filtered = df_filtered[
                    (df_filtered['data_inicio_dt'].dt.date >= periodo[0]) &
                    (df_filtered['data_inicio_dt'].dt.date <= periodo[1])
                ]

        return df_filtered

    def prepare_excel_export(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara DataFrame para exportação Excel.

        Args:
            df: DataFrame a ser exportado

        Returns:
            DataFrame limpo
        """
        return df.drop(columns=['sigla', 'area_nome', 'data_inicio_dt'], errors='ignore')

    @staticmethod
    def clear_cache():
        """Limpa o cache de dados"""
        st.cache_data.clear()
