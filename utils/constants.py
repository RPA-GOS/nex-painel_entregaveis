"""
Constantes utilizadas em todo o projeto.
Centraliza definições para facilitar manutenção.
"""

AREAS_MAP = {
    'bko': 'BackOffice',
    'ctb': 'Contabilidade',
    'fcs': 'Facilities',
    'fin': 'Financeiro',
    'i3d': 'Impressão 3D',
    'mnt': 'Manutenção',
    'nex': 'Núcleo de Excelência',
    'npe': 'Núcleo de Pessoas',
    'sti': 'Tecnologia',
    'jur': 'Setor Jurídico',
    'nia': 'Núcleo de IA',
    'nti': 'Núcleo de TI',
    'sup': 'Suprimentos'
}

COLORS_DARK = {
    "primary": "#EF7D1E",
    "secondary": "#000000",
    "background": "#0A0A0A",
    "card": "#1A1A1A",
    "text": "#FFFFFF",
    "text_secondary": "#CCCCCC",
    "success": "#27AE60",
    "error": "#E74C3C",
    "info": "#3498DB",
    "border": "#2A2A2A",
    "sidebar": "#0A0A0A"
}

COLORS_LIGHT = {
    "primary": "#EF7D1E",
    "secondary": "#000000",
    "background": "#FFFFFF",
    "card": "#F8F8F8",
    "text": "#1A1A1A",
    "text_secondary": "#666666",
    "success": "#27AE60",
    "error": "#E74C3C",
    "info": "#3498DB",
    "border": "#E0E0E0",
    "sidebar": "#FAFAFA"
}

CACHE_TTL_SECONDS = 300
REQUEST_TIMEOUT_SECONDS = 15

TIPO_FALHA_MAP = {
    'S': 'Indisponibilidade de Sistema',
    'H': 'Falha Humana',
    'P': 'Falha de Desenvolvimento',
}
TIPO_FALHA_NAO_CLASSIFICADO = 'Não Classificado'

FAILURE_COLORS = {
    'Indisponibilidade de Sistema': '#3498DB',
    'Falha Humana': '#F39C12',
    'Falha de Desenvolvimento': '#9B59B6',
    'Não Classificado': '#7F8C8D',
}

ERRO_VERBA_INSUFICIENTE = 'Verba insuficiente'
