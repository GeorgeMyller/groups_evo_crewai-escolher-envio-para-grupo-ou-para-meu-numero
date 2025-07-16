FROM python:3.12-slim AS builder

RUN apt-get update -o Acquire::Check-Valid-Until=false && apt-get install -y --no-install-recommends --allow-unauthenticated \
    cron \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN curl -Ls https://astral.sh/uv/install.sh | sh && \
    export PATH="/root/.local/bin:$PATH" && \
    export UV_HTTP_TIMEOUT=120 && \
    uv pip install --system .

FROM python:3.12-slim

RUN apt-get update -o Acquire::Check-Valid-Until=false && apt-get install -y --no-install-recommends --allow-unauthenticated \
    cron \
    supervisor \
    procps \
    curl \
    nano \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# Create necessary directories for logs and data with proper permissions
RUN mkdir -p /app/data/logs && \
    mkdir -p /app/data/cache && \
    mkdir -p /var/run && \
    chmod 755 /var/run && \
    chmod 777 /app/data && \
    chmod 777 /app/data/logs && \
    chmod 777 /app/data/cache && \
    touch /app/data/group_summary.csv && \
    chmod 666 /app/data/group_summary.csv

# Copy supervisord.conf to the correct location
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy and setup the environment loader script for cron tasks
COPY load_env.sh /usr/local/bin/load_env.sh
RUN chmod +x /usr/local/bin/load_env.sh

# Copy the entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 8501

# Use entrypoint script to setup environment and then run supervisord
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]