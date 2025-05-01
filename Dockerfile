# --- Multi-stage build com Alpine ---

# --- Multi-stage build com python:3.12-slim ---
FROM python:3.12-slim AS builder
WORKDIR /app

# Instala dependências de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia arquivos de dependências
COPY pyproject.toml uv.lock ./

# Instala uv
RUN pip install --no-cache-dir uv

# Instala dependências do projeto no diretório temporário
RUN uv pip install --no-cache-dir --prefix=/install .

# Copia código fonte
COPY app.py group_controller.py group.py groups_util.py message_sandeco.py send_sandeco.py summary_crew.py summary.py task_scheduler.py ./
COPY pages/ ./pages/

# --- Stage final ---
FROM python:3.12-slim
WORKDIR /app

# Copia dependências instaladas do builder
COPY --from=builder /install /usr/local

# Copia código fonte
COPY app.py group_controller.py group.py groups_util.py message_sandeco.py send_sandeco.py summary_crew.py summary.py task_scheduler.py ./
COPY pages/ ./pages/

# Instala o cron
RUN apt-get update && apt-get install -y cron

# Expondo porta do Streamlit
EXPOSE 8501

ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
