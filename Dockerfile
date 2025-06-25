# Multi-stage build for smaller final image
FROM python:3.12.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all necessary files for package installation
COPY pyproject.toml uv.lock* README.md ./
COPY src/ ./src/

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and the package
RUN export PATH="/root/.local/bin:$PATH" && \
    uv pip install --system .

# Copy additional resources
COPY data/ ./data/

# Production stage
FROM python:3.12.10-slim

# Create non-root user for security
RUN useradd --create-home --home-dir /home/appuser --shell /bin/bash --system appuser

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    supervisor \
    tini \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copy Python packages and binaries from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src
COPY --from=builder /app/scripts ./scripts
COPY --from=builder /app/data ./data

# Copy configuration files
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create directories and set permissions
RUN mkdir -p /tmp/logs /app/logs && \
    chown -R appuser:appuser /app /tmp/logs

# Configure cron
RUN echo '#!/bin/bash\necho "$(date): Cron job executed" >> /tmp/logs/cron.log' > /tmp/cron_test.sh && \
    chmod +x /tmp/cron_test.sh && \
    echo "*/5 * * * * root /tmp/cron_test.sh" > /etc/cron.d/tasks_app && \
    chmod 0644 /etc/cron.d/tasks_app && \
    crontab /etc/cron.d/tasks_app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose port
EXPOSE 8501

# Use tini as PID 1 to handle signals properly
ENTRYPOINT ["/usr/bin/tini", "--"]

# Use supervisor to manage multiple processes
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]