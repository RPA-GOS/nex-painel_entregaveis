"""
Serviço de processamento de dados e cálculo de KPIs.
Transforma dados brutos em informações úteis para o dashboard.
"""

import pandas as pd
from typing import List, Dict, Any
from models.kpi import KPI
from utils.constants import AREAS_MAP, TIPO_FALHA_MAP, TIPO_FALHA_NAO_CLASSIFICADO, ERRO_VERBA_INSUFICIENTE


class DataService:
    """Processa dados de entregáveis e calcula KPIs"""

    @staticmethod
    def process_raw_data(raw_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Processa dados brutos da API e retorna DataFrame tratado.

        Args:
            raw_data: Lista de dicionários com dados brutos

        Returns:
            DataFrame processado e enriquecido
        """
        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(raw_data)

        df = DataService._filter_production_only(df)

        if df.empty:
            return df

        df = DataService._identify_area(df)
        df = DataService._parse_dates(df)
        df = DataService._normalize_numeric_fields(df)
        df = DataService._identify_failure_type(df)

        return df

    @staticmethod
    def _filter_production_only(df: pd.DataFrame) -> pd.DataFrame:
        """Filtra apenas processos em produção"""
        if 'em_producao' not in df.columns:
            return df
        return df[df['em_producao'] == True].copy()

    @staticmethod
    def _identify_area(df: pd.DataFrame) -> pd.DataFrame:
        """Identifica e adiciona coluna de área"""
        if 'nome_processo' in df.columns:
            df['sigla'] = df['nome_processo'].str.split('-').str[0].str.lower()
            df['area_nome'] = df['sigla'].map(AREAS_MAP).fillna('Outros')
        return df

    @staticmethod
    def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
        """Converte campos de data para datetime"""
        if 'data_inicio' in df.columns:
            df['data_inicio_dt'] = pd.to_datetime(
                df['data_inicio'],
                errors='coerce'
            ).dt.tz_localize(None)
        return df

    @staticmethod
    def _normalize_numeric_fields(df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza campos numéricos"""
        if 'resultado_entregue' in df.columns:
            df['resultado_entregue'] = pd.to_numeric(
                df['resultado_entregue'],
                errors='coerce'
            ).fillna(0)
        return df

    @staticmethod
    def _identify_failure_type(df: pd.DataFrame) -> pd.DataFrame:
        """Traduz o código de tipo_falha (S/H/P) em descrição legível"""
        if 'tipo_falha' not in df.columns:
            return df

        df['tipo_falha_desc'] = df['tipo_falha'].map(TIPO_FALHA_MAP)

        if 'status' in df.columns:
            eh_falha = df['status'].str.lower() == 'falha'
            df.loc[eh_falha & df['tipo_falha_desc'].isna(), 'tipo_falha_desc'] = TIPO_FALHA_NAO_CLASSIFICADO

        return df

    @staticmethod
    def calculate_kpis(df: pd.DataFrame) -> KPI:
        """
        Calcula KPIs a partir do DataFrame.

        Args:
            df: DataFrame com dados processados

        Returns:
            Objeto KPI com métricas calculadas
        """
        total_disparos = len(df)

        mask_verba = DataService._mask_verba_insuficiente(df)
        verba_insuficiente = int(mask_verba.sum())

        # Exclui verba de todos os cálculos de saúde e volumetria
        df_sem_verba = df[~mask_verba]
        total_efetivo = len(df_sem_verba)

        execucoes_concluidas = len(
            df_sem_verba[df_sem_verba['status'].str.lower() == 'concluído']
        ) if 'status' in df_sem_verba.columns and total_efetivo > 0 else 0

        health_score = (
            (execucoes_concluidas / total_efetivo * 100)
            if total_efetivo > 0 else 0
        )

        volume_entregue = (
            df_sem_verba['resultado_entregue'].sum()
            if 'resultado_entregue' in df_sem_verba.columns else 0
        )

        resultado_esperado_total = (
            df_sem_verba['resultado_esperado'].sum()
            if 'resultado_esperado' in df_sem_verba.columns else 0
        )

        resultado_entregue_total = volume_entregue

        percentual_atingimento = (
            (resultado_entregue_total / resultado_esperado_total * 100)
            if resultado_esperado_total > 0 else 0
        )

        return KPI(
            total_disparos=total_disparos,
            execucoes_concluidas=execucoes_concluidas,
            verba_insuficiente=verba_insuficiente,
            health_score=health_score,
            volume_entregue=int(volume_entregue),
            resultado_esperado_total=int(resultado_esperado_total),
            resultado_entregue_total=int(resultado_entregue_total),
            percentual_atingimento=percentual_atingimento
        )

    @staticmethod
    def filter_by_area(df: pd.DataFrame, area_nome: str) -> pd.DataFrame:
        """Filtra DataFrame por área específica"""
        if df.empty or 'area_nome' not in df.columns:
            return pd.DataFrame()
        return df[df['area_nome'] == area_nome].copy()

    @staticmethod
    def get_area_counts(df: pd.DataFrame) -> Dict[str, int]:
        """Retorna contagem de execuções por área"""
        if df.empty or 'area_nome' not in df.columns:
            return {}
        return df['area_nome'].value_counts().to_dict()

    @staticmethod
    def _mask_verba_insuficiente(df: pd.DataFrame) -> pd.Series:
        """Retorna máscara booleana para registros de Verba Insuficiente"""
        if 'erros' not in df.columns:
            return pd.Series(False, index=df.index)
        return df['erros'].str.contains(ERRO_VERBA_INSUFICIENTE, case=False, na=False)

    @staticmethod
    def prepare_verba_insuficiente_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Retorna registros com erro de Verba Insuficiente para exibição separada.

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame apenas com registros de Verba Insuficiente
        """
        if df.empty:
            return pd.DataFrame()
        mask = DataService._mask_verba_insuficiente(df)
        return df[mask].copy()

    @staticmethod
    def prepare_comparison_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para gráfico de comparação esperado vs entregue.
        Registros de Verba Insuficiente são separados em coluna própria
        e excluídos do Esperado/Entregue para não distorcer o gráfico.

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame agrupado por processo com coluna resultado_verba_insuficiente
        """
        if df.empty:
            return pd.DataFrame()

        required_cols = ['nome_processo', 'resultado_esperado', 'resultado_entregue']
        if not all(col in df.columns for col in required_cols):
            return pd.DataFrame()

        mask_verba = DataService._mask_verba_insuficiente(df)

        # Linhas normais (sem verba)
        df_normal = df[~mask_verba]
        if df_normal.empty:
            return pd.DataFrame()

        df_comparacao = df_normal.groupby('nome_processo').agg({
            'resultado_esperado': 'sum',
            'resultado_entregue': 'sum'
        }).reset_index()

        # Linhas de verba: agrega esperado como "volume bloqueado por verba"
        df_verba = df[mask_verba]
        if not df_verba.empty:
            df_verba_grouped = df_verba.groupby('nome_processo').agg(
                resultado_verba_insuficiente=('resultado_esperado', 'sum')
            ).reset_index()
            df_comparacao = df_comparacao.merge(
                df_verba_grouped, on='nome_processo', how='left'
            )
            df_comparacao['resultado_verba_insuficiente'] = (
                df_comparacao['resultado_verba_insuficiente'].fillna(0).astype(int)
            )
        else:
            df_comparacao['resultado_verba_insuficiente'] = 0

        return df_comparacao.sort_values(by='resultado_esperado', ascending=True)

    @staticmethod
    def get_failure_breakdown(df: pd.DataFrame) -> pd.DataFrame:
        """
        Conta as execuções com falha por tipo (Sistema/Humana/Desenvolvimento/Não Classificado).

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame com colunas ['tipo_falha_desc', 'quantidade']
        """
        if df.empty or 'status' not in df.columns or 'tipo_falha_desc' not in df.columns:
            return pd.DataFrame(columns=['tipo_falha_desc', 'quantidade'])

        df_falhas = df[df['status'].str.lower() == 'falha']
        if df_falhas.empty:
            return pd.DataFrame(columns=['tipo_falha_desc', 'quantidade'])

        contagem = df_falhas['tipo_falha_desc'].value_counts().reset_index()
        contagem.columns = ['tipo_falha_desc', 'quantidade']

        return contagem.sort_values(by='quantidade', ascending=True)

    @staticmethod
    def prepare_table_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara dados para exibição em tabela.

        Args:
            df: DataFrame filtrado

        Returns:
            DataFrame formatado para exibição
        """
        if df.empty:
            return pd.DataFrame()

        # Ordenar primeiro, antes de filtrar colunas
        if 'data_inicio_dt' in df.columns:
            df = df.sort_values(by='data_inicio_dt', ascending=False)

        display_columns = [
            'nome_processo',
            'horarios_disparo',
            'tipo_fluxo',
            'data_inicio',
            'data_fim',
            'duracao',
            'status',
            'tipo_falha_desc',
            'erros'
        ]

        df_table = df[[col for col in display_columns if col in df.columns]].copy()

        if 'data_inicio' in df_table.columns:
            df_table['data_inicio'] = pd.to_datetime(
                df_table['data_inicio'],
                errors='coerce'
            ).dt.strftime('%d/%m/%Y %H:%M:%S')

        if 'data_fim' in df_table.columns:
            df_table['data_fim'] = pd.to_datetime(
                df_table['data_fim'],
                errors='coerce'
            ).dt.strftime('%d/%m/%Y %H:%M:%S')

        column_rename = {
            'nome_processo': 'Processo',
            'horarios_disparo': 'Horário',
            'tipo_fluxo': 'Tipo Fluxo',
            'data_inicio': 'Data Início',
            'data_fim': 'Data Fim',
            'duracao': 'Duração',
            'status': 'Status',
            'tipo_falha_desc': 'Tipo de Falha',
            'erros': 'Erros'
        }

        df_table = df_table.rename(columns=column_rename)
        df_table = df_table.reset_index(drop=True)
        df_table.index = df_table.index + 1

        return df_table
