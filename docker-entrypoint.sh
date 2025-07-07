#!/bin/bash
set -e  # Exit on error

# Function for logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ENTRYPOINT] $1"
}

log "Starting Docker entrypoint script"

# Garante que os diretórios necessários existam
log "Creating necessary directories"
mkdir -p /app/data
mkdir -p /app/data/cache
mkdir -p /app/data/logs
mkdir -p /var/spool/cron/crontabs
touch /var/spool/cron/crontabs/root
chmod 600 /var/spool/cron/crontabs/root
chmod -R 777 /app/data  # Ensure full write permissions

# Garante que o arquivo CSV existe com permissões corretas
log "Setting up group_summary.csv"
touch /app/data/group_summary.csv
chmod 666 /app/data/group_summary.csv

# Verify crontab is set up correctly
log "Checking crontab setup"
crontab -l > /tmp/current_crontab || echo "" > /tmp/current_crontab
cat /tmp/current_crontab

# Stop cron if it's already running
log "Stopping cron if running"
service cron stop || true

# Make sure cron is configured correctly
log "Configuring cron"
echo "SHELL=/bin/bash" > /etc/cron.d/app-cron
echo "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" >> /etc/cron.d/app-cron
echo "PYTHONPATH=/app:/app/src" >> /etc/cron.d/app-cron
echo "DOCKER_ENV=true" >> /etc/cron.d/app-cron
echo "" >> /etc/cron.d/app-cron

# Set permissions for cron
log "Setting cron file permissions"
chmod 0644 /etc/cron.d/app-cron
chown root:root /etc/cron.d/app-cron

# Create a simple test task to verify cron works
echo "* * * * * root echo \"Cron is working\" >> /app/data/cron_test.log 2>&1" > /etc/cron.d/cron-test
chmod 0644 /etc/cron.d/cron-test

# Start cron with full logging
log "Starting cron"
service cron start
sleep 2

# Verify cron status
log "Checking cron status"
service cron status || { log "ERROR: Failed to start cron service"; }

# Exibir status dos serviços
log "=== STATUS DOS SERVIÇOS ==="
log "Cron:"
service cron status || log "ERROR: Cron not running"

log "=== VERIFICAÇÃO DE ARQUIVOS ==="
log "Diretório /app/data:"
ls -la /app/data
log "Arquivo group_summary.csv:"
ls -la /app/data/group_summary.csv

# Create docker marker file to help detection
touch /app/.docker_environment
log "Docker environment marker file created"

log "Entrypoint script complete, executing main command: $@"

# Executa o comando original (supervisord)
exec "$@"