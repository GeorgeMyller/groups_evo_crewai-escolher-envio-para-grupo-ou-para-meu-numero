# Dockerfile otimizado para Raspberry Pi (arm64) usando uv
FROM python:3.12-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Instala o uv (gerenciador de dependências ultrarrápido da Astral)
RUN pip install --upgrade pip && pip install uv

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . .

# Instala dependências do pyproject.toml usando uv
RUN uv pip install --system .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando padrão para rodar o Streamlit
CMD ["streamlit", "run", "WhatsApp_Group_Resumer.py", "--server.port=8501", "--server.address=0.0.0.0"]
