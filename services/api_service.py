"""
Serviço de comunicação com a API BPMS.
Responsável por buscar dados dos entregáveis.
"""

import requests
from typing import List, Dict, Any
from config.settings import settings
from utils.constants import REQUEST_TIMEOUT_SECONDS


class APIService:
    """Gerencia comunicação com a API de entregáveis"""

    def __init__(self):
        self.api_url = settings.API_URL
        self.api_token = settings.API_TOKEN
        self._session = requests.Session()

    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisição"""
        if self.api_token:
            return {'Authorization': f'Bearer {self.api_token}'}
        return {}

    def fetch_entregaveis(self) -> List[Dict[str, Any]]:
        """
        Busca dados de entregáveis da API.

        Returns:
            Lista de dicionários com dados dos entregáveis
        """
        try:
            response = self._session.get(
                self.api_url,
                headers=self._get_headers(),
                timeout=REQUEST_TIMEOUT_SECONDS
            )

            if response.status_code == 200:
                json_data = response.json()
                return self._extract_data(json_data)

            print(f"Erro na API: Status {response.status_code}")
            return []

        except requests.RequestException as e:
            print(f"Falha na conexão com a API: {e}")
            return []

    def _extract_data(self, json_data: Any) -> List[Dict[str, Any]]:
        """
        Extrai dados da resposta JSON.

        Args:
            json_data: Resposta JSON da API

        Returns:
            Lista de entregáveis
        """
        if isinstance(json_data, list):
            return json_data

        if isinstance(json_data, dict):
            for key in ['data', 'results', 'items']:
                if key in json_data and isinstance(json_data[key], list):
                    return json_data[key]

        return []
