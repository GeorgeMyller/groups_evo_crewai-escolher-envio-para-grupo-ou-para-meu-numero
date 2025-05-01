## Como Executar com Docker 🐳

Este projeto inclui suporte completo para execução via Docker e Docker Compose, facilitando a configuração e o deploy do ambiente Streamlit.

### Requisitos Específicos
- **Python 3.12** (a imagem base é `python:3.12-alpine`)
- Todas as dependências são instaladas automaticamente via `requirements.txt` durante o build da imagem Docker.

### Variáveis de Ambiente Obrigatórias
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```env
EVO_BASE_URL=<sua_base_url>
EVO_API_TOKEN=<seu_api_token>
EVO_INSTANCE_NAME=<seu_instance_name>
EVO_INSTANCE_TOKEN=<seu_instance_token>
```

### Como Executar com Docker Compose

#### Versão Completa (com CrewAI)
1. **Construa e inicie o serviço completo:**
    ```sh
    docker compose --profile full up --build
    ```
    - Tamanho da imagem: aproximadamente 3.12GB
    - Inclui suporte completo a CrewAI e IA avançada para sumarização

#### Versão Leve (sem CrewAI)
1. **Construa e inicie a versão otimizada sem CrewAI:**
    ```sh
    docker compose --profile slim up --build
    ```
    - Tamanho da imagem: aproximadamente 669MB (78% menor)
    - Usa uma versão simplificada da sumarização sem dependência de LLMs

2. **Acesse a interface:**
    - O Streamlit estará disponível em [http://localhost:8501](http://localhost:8501)

### Configurações Especiais
- O serviço roda como usuário não-root para maior segurança.
- Não há volumes ou serviços externos necessários.
- Apenas a porta **8501** é exposta (padrão do Streamlit).

---

## How to Run with Docker 🐳

This project provides full support for running via Docker and Docker Compose, making it easy to set up the Streamlit environment.

### Specific Requirements
- **Python 3.12** (the base image is `python:3.12-slim`)
- All dependencies are installed automatically from `pyproject.toml` during the Docker image build.

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
    - Start the `python-app` service running Streamlit on the default port

2. **Access the interface:**
    - Streamlit will be available at [http://localhost:8501](http://localhost:8501)

### Special Configuration
- The service runs as a non-root user for security.
- No volumes or external services are required.
- Only **port 8501** is exposed (Streamlit default).
