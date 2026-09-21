# Painel de Entregáveis RPA - Grupo Odilon Santos

Sistema de monitoramento e gestão de fluxos RPA (Robotic Process Automation) desenvolvido com arquitetura MVC.

## 🎯 Funcionalidades

- **Monitoramento por Área**: Visualização organizada por departamentos
- **Métricas em Tempo Real**: Indicadores de qualidade e performance
- **Gestão de Falhas**: Análise e controle de erros
- **Filtros Avançados**: Busca por processo, tipo, status e período
- **Modo Escuro/Claro**: Alternância de temas
- **Exportação Excel**: Download de relatórios completos

## 📋 Requisitos

- Python 3.8+
- Dependências em `requirements.txt`

## 🚀 Instalação

1. Clone o repositório

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` na pasta `config/`:
```bash
cp config/.env.example config/.env
```

Edite `config/.env` com suas credenciais:
```env
API_URL=https://integra.odilonsantos.com/api/Bpms/tabentregaveisprod
API_TOKEN=seu_token_aqui
HOST=0.0.0.0
PORT=8501
```

## 🎮 Execução

### Windows
```bash
run.bat
```

### Linux/Mac
```bash
./run.sh
```

Ou diretamente:
```bash
streamlit run main.py
```

## 📁 Estrutura do Projeto

```
nex-painel_entregaveis/
├── main.py                    # Aplicação principal (View Layer)
├── requirements.txt           # Dependências Python
├── run.bat                    # Script Windows
├── run.sh                     # Script Linux/Mac
│
├── config/                    # Configurações
│   ├── .env                   # Variáveis de ambiente
│   ├── .env.example           # Template
│   ├── settings.py            # Carregador de configurações
│   └── __init__.py
│
├── controllers/               # Camada de controle
│   ├── __init__.py
│   └── main_controller.py     # Orquestração da aplicação
│
├── models/                    # Modelos de dados
│   ├── __init__.py
│   ├── entregavel.py          # Modelo Entregável
│   └── kpi.py                 # Modelo KPI
│
├── services/                  # Camada de serviços
│   ├── __init__.py
│   ├── api_service.py         # Comunicação com API BPMS
│   └── data_service.py        # Processamento de dados e KPIs
│
├── utils/                     # Utilitários
│   ├── __init__.py
│   ├── constants.py           # Constantes do projeto
│   ├── helpers.py             # Funções auxiliares
│   ├── styles.py              # Estilos CSS
│   └── ui_components.py       # Componentes de UI
│
├── tests/                     # Testes unitários
│   ├── __init__.py
│   └── test_data_service.py   # Testes do DataService
│
├── docs/                      # Documentação
│   ├── README.md              # Este arquivo
│   └── technical_details.md   # Detalhes técnicos
│
├── assets/                    # Recursos estáticos
│   └── osac.jpg               # Logo
│
└── .streamlit/                # Configurações Streamlit
    └── config.toml            # Tema e servidor
```

## 🏗️ Arquitetura

### Padrão MVC

- **Model** (`models/`): Estruturas de dados
- **View** (`main.py`, `utils/ui_components.py`): Interface do usuário
- **Controller** (`controllers/`): Lógica de negócio

### Camada de Serviços

- **APIService**: Comunicação com API externa
- **DataService**: Processamento e transformação de dados

### Princípios Aplicados

- **DRY**: Código não repetido, constantes centralizadas
- **Responsabilidade Única**: Cada classe tem uma função específica
- **KISS**: Código simples e direto

## 🎨 Áreas Mapeadas

- BackOffice (bko)
- Contabilidade (ctb)
- Facilities (fcs)
- Financeiro (fin)
- Impressão 3D (i3d)
- Manutenção (mnt)
- Núcleo de Excelência (nex)
- Núcleo de Pessoas (npe)
- Tecnologia (sti)
- Setor Jurídico (jur)
- Núcleo de IA (nia)
- Núcleo de TI (nti)
- Suprimentos (sup)

## 🧪 Testes

Execute os testes:
```bash
python tests/test_data_service.py
```

## 🔒 Segurança

- Não versione o arquivo `.env`
- Mantenha o token de API em sigilo
- Apenas processos com `em_producao: true` são exibidos

## 🛠️ Tecnologias

- **Streamlit**: Framework web
- **Pandas**: Manipulação de dados
- **Plotly**: Visualizações interativas
- **Python-dotenv**: Gerenciamento de ambiente
- **Requests**: Consumo de API REST

## 📝 Notas

- Cache de dados: 5 minutos
- Identificação de área por prefixo (ex: "ctb-" → Contabilidade)

## 📖 Documentação Adicional

- [Detalhes Técnicos](docs/technical_details.md)

---

**Desenvolvido para o Grupo Odilon Santos**
