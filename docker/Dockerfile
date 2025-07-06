FROM python:3.12.10-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN curl -Ls https://astral.sh/uv/install.sh | sh && \
    export PATH="/root/.local/bin:$PATH" && \
    uv pip install --system .

COPY . .

FROM python:3.12.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app


# Copy supervisord.conf to the correct location
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create a test script for cron
RUN echo '#!/bin/bash\necho "Cron job executed" >> /tmp/cron_test.log' > /tmp/cron_test.sh && chmod +x /tmp/cron_test.sh

# Add cron job
RUN touch /etc/cron.d/tasks_app && \
    chmod 0644 /etc/cron.d/tasks_app && \
    echo "/tmp/cron_test.sh" >> /etc/cron.d/tasks_app

EXPOSE 8501

# Run the Streamlit app when the container launches
CMD ["streamlit", "run", "src/whatsapp_manager/ui/main_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]