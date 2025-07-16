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

# Make sure cron is configured correctly

# Garante que o diretório de cron existe
mkdir -p /etc/cron.d

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

# Create docker marker file to help detection
touch /app/.docker_environment
log "Docker environment marker file created"

# Stop any existing cron processes to avoid conflicts
log "Stopping any existing cron processes"
pkill -f cron || true
pkill -f crond || true
sleep 2

# Remove any existing cron PID files
log "Cleaning up cron PID files"
rm -f /var/run/crond.pid
rm -f /run/crond.pid
rm -f /var/run/cron.pid

# Make sure /var/run directory has proper permissions
chmod 755 /var/run

log "Entrypoint script complete, executing main command: $@"

# Executa o comando original (supervisord)
exec "$@"