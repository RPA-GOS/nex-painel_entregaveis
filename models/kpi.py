"""
Modelo de dados para KPIs (Key Performance Indicators).
Representa métricas calculadas a partir dos entregáveis.
"""

from dataclasses import dataclass


@dataclass
class KPI:
    """Representa os indicadores-chave de performance"""

    total_disparos: int
    execucoes_concluidas: int
    verba_insuficiente: int
    health_score: float
    volume_entregue: int
    resultado_esperado_total: int
    resultado_entregue_total: int
    percentual_atingimento: float

    @property
    def execucoes_falhadas(self) -> int:
        """Calcula falhas reais (exclui Verba Insuficiente, que não é erro de execução)"""
        return max(0, self.total_disparos - self.execucoes_concluidas - self.verba_insuficiente)

    @property
    def taxa_sucesso(self) -> float:
        """Retorna a taxa de sucesso das execuções"""
        return self.health_score

    def to_dict(self) -> dict:
        """Converte KPI para dicionário"""
        return {
            'total_disparos': self.total_disparos,
            'execucoes_concluidas': self.execucoes_concluidas,
            'execucoes_falhadas': self.execucoes_falhadas,
            'verba_insuficiente': self.verba_insuficiente,
            'health_score': round(self.health_score, 1),
            'volume_entregue': self.volume_entregue,
            'resultado_esperado_total': self.resultado_esperado_total,
            'resultado_entregue_total': self.resultado_entregue_total,
            'percentual_atingimento': round(self.percentual_atingimento, 1),
            'taxa_sucesso': round(self.taxa_sucesso, 1)
        }
