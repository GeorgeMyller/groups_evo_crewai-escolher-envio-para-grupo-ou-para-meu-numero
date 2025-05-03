# syntax=docker/dockerfile:1

FROM python:3.12-alpine AS builder
WORKDIR /app

# Instala dependências de compilação necessárias (inclui Rust/Cargo para chromadb/CrewAI)
RUN apk add --no-cache gcc musl-dev python3-dev libffi-dev rust cargo

# Copia só os arquivos de dependências
COPY requirements-prod.txt ./

# Cria ambiente virtual e instala com flags para otimizar tamanho
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements-prod.txt \
    # Limpa cache e arquivos temporários logo após a instalação
    && find /opt/venv -name "*.pyc" -delete \
    && find /opt/venv -name "__pycache__" -type d -exec rm -rf {} +

# Apenas agora copiamos o código da aplicação
COPY . .

# Imagem final muito menor
FROM python:3.12-alpine AS final
WORKDIR /app

# Cria usuário não-root
RUN adduser -D appuser

# Apenas os binários e bibliotecas essenciais
RUN apk add --no-cache libffi

# Copia apenas venv e código do app real (sem arquivos temporários)
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app /app

# Remove todos os arquivos desnecessários de uma vez
RUN rm -rf /opt/venv/lib/python*/site-packages/pip* \
    && rm -rf /opt/venv/lib/python*/site-packages/setuptools* \
    && rm -rf /opt/venv/lib/python*/site-packages/wheel* \
    && find /opt/venv -name "*.pyc" -delete \
    && find /opt -name "__pycache__" -type d -exec rm -rf {} + \
    && find /app -name "__pycache__" -type d -exec rm -rf {} +

USER appuser
ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
