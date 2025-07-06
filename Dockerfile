FROM python:3.12.10-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN curl -Ls https://astral.sh/uv/install.sh | sh && \
    export PATH="/root/.local/bin:$PATH" && \
    uv pip install --system .

FROM python:3.12.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    supervisor \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Create necessary directories for logs and data
RUN mkdir -p /app/data/logs && \
    chmod 755 /app/data && \
    chmod 755 /app/data/logs

# Copy supervisord.conf to the correct location
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy and setup the environment loader script for cron tasks
COPY load_env.sh /usr/local/bin/load_env.sh
RUN chmod +x /usr/local/bin/load_env.sh

EXPOSE 8501

# Start supervisord which will manage both cron and streamlit
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]