# WhatsApp Group Manager and Summarizer 🚀

Sistema automatizado para gerenciamento e sumarização de grupos do WhatsApp usando Evolution API e CrewAI para análise inteligente de mensagens.

## 📋 Sobre o Projeto

Este projeto oferece uma solução completa para:
- **Gerenciamento de grupos** do WhatsApp via Evolution API
- **Sumarização inteligente** de mensagens usando CrewAI
- **Interface web** para configuração e monitoramento
- **Agendamento automático** de resumos
- **Exportação de dados** para análise

## Como Executar com Docker 🐳

Este projeto inclui suporte completo para execução via Docker e Docker Compose, facilitando a configuração e o deploy do ambiente Streamlit.

### Requisitos Específicos
- **Python 3.12** (a imagem base é `python:3.12.10-slim`)
- Todas as dependências são instaladas automaticamente via `pyproject.toml` durante o build da imagem Docker usando `uv`
- Docker e Docker Compose instalados

### Variáveis de Ambiente Obrigatórias
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```env
EVO_BASE_URL=<sua_base_url>
EVO_API_TOKEN=<seu_api_token>
EVO_INSTANCE_NAME=<seu_instance_name>
EVO_INSTANCE_TOKEN=<seu_instance_token>
```

### Como Executar com Docker Compose

1. **Construa e inicie o serviço:**
    ```sh
    docker compose up --build
    ```
    Isso irá:
    - Construir a imagem Docker com todas as dependências do projeto
    - Iniciar o serviço `app` executando Streamlit na porta padrão
    - Configurar volumes para persistência de dados

2. **Acesse a interface:**
    - O Streamlit estará disponível em [http://localhost:8501](http://localhost:8501)

### Configurações Especiais
- O serviço roda com suporte a cron para tarefas agendadas
- Volumes configurados para persistir dados entre reinicializações
- Timezone configurado para Europe/Lisbon
- Supervisord para gerenciar múltiplos processos
- Apenas a porta **8501** é exposta (padrão do Streamlit)

---

## Execução Local (sem Docker) 💻

### Requisitos
- Python 3.12.7 ou superior
- uv (recomendado) ou pip

### Instalação
```bash
# Clone o repositório
git clone <repository-url>
cd groups_evo_crewai-escolher-envio-para-grupo-ou-para-meu-numero

# Instale as dependências usando uv (recomendado)
uv pip install .

# Ou usando pip
pip install .

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### Executar a Aplicação
```bash
# Interface Streamlit principal
uv run streamlit run src/whatsapp_manager/ui/main_app.py

# Ou use as tasks configuradas no VS Code
# Task: "Start Streamlit App"
```

## 🛠️ Funcionalidades Principais

- **Gerenciamento de Grupos**: Listar, filtrar e selecionar grupos do WhatsApp
- **Sumarização Inteligente**: Análise de mensagens usando CrewAI
- **Agendamento**: Configurar resumos automáticos por grupo
- **Interface Web**: Dashboard intuitivo para todas as operações
- **Exportação**: Dados dos grupos em formato CSV
- **Logs Detalhados**: Monitoramento completo das operações

## 📁 Estrutura do Projeto

```
src/whatsapp_manager/
├── core/           # Lógica principal do negócio
├── infrastructure/ # Integrações externas (APIs)
├── presentation/   # Camada de apresentação
├── shared/         # Utilitários compartilhados
├── ui/            # Interface Streamlit
└── utils/         # Utilitários gerais
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente Opcionais
```env
# OpenAI para CrewAI (opcional)
OPENAI_API_KEY=<sua_chave_openai>

# Configurações de log
LOG_LEVEL=INFO
DEBUG=false

# Configurações específicas
WHATSAPP_NUMBER=<seu_numero_whatsapp>
```

## 📖 Documentação

Para documentação completa, consulte:
- [Documentação da API](docs/api/evolution-api.md)
- [Guia de Uso CLI](docs/guides/cli-usage.md)
- [Arquitetura do Sistema](docs/architecture/README.md)
- [Guia de Deploy](docs/deployment/README.md)

## 🤝 Contribuindo

Consulte [CONTRIBUTING.md](CONTRIBUTING.md) para guidelines de contribuição.

## 📄 Licença

Este projeto está licenciado sob [LICENSE](LICENSE).

---

## How to Run with Docker 🐳

This project provides full support for running via Docker and Docker Compose, making it easy to set up the Streamlit environment.

### Specific Requirements
- **Python 3.12** (the base image is `python:3.12.10-slim`)
- All dependencies are installed automatically from `pyproject.toml` during the Docker image build using `uv`
- Docker and Docker Compose installed

### Required Environment Variables
Create a `.env` file in the project root with the following variables:
```env
EVO_BASE_URL=<your_base_url>
EVO_API_TOKEN=<your_api_token>
EVO_INSTANCE_NAME=<your_instance_name>
EVO_INSTANCE_TOKEN=<your_instance_token>
```

### How to Run with Docker Compose
1. **Build and start the service:**
    ```sh
    docker compose up --build
    ```
    This will:
    - Build the Docker image with all project dependencies
    - Start the `app` service running Streamlit on the default port
    - Configure volumes for data persistence

2. **Access the interface:**
    - Streamlit will be available at [http://localhost:8501](http://localhost:8501)

### Special Configuration
- The service runs with cron support for scheduled tasks
- Volumes configured for data persistence between restarts
- Timezone set to Europe/Lisbon
- Supervisord for managing multiple processes
- Only **port 8501** is exposed (Streamlit default)
