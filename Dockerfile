FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de dependências
COPY pyproject.toml uv.lock ./

# Instalar uv para gerenciamento de pacotes
RUN pip install --no-cache-dir uv

# Instalar dependências do projeto
RUN uv pip install --system --no-cache-dir .

# Copiar o código-fonte
COPY . .

# Expor a porta do Streamlit
EXPOSE 8501

# Configurar ambiente
ENV PYTHONUNBUFFERED=1

# Comando para executar a aplicação
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
