# 🐳 Deployment Guide

## Overview

This guide covers different deployment options for the WhatsApp Group Manager system.

## Prerequisites

- Docker and Docker Compose
- Git
- Network access to Evolution API

## Quick Start (Docker)

### 1. Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd whatsapp-group-manager

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

### 2. Required Environment Variables

```env
# Evolution API Configuration
EVO_API_TOKEN=your_evolution_api_token
EVO_INSTANCE_NAME=your_instance_name
EVO_BASE_URL=http://evolution-api-url:port

# WhatsApp Configuration
WHATSAPP_NUMBER=your_whatsapp_number

# AI Configuration (optional)
OPENAI_API_KEY=your_openai_api_key
```

### 3. Deploy with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Application

- **Web Interface**: http://localhost:8501
- **API Health**: Check Evolution API connectivity
- **Logs**: `docker-compose logs whatsapp-manager`

## Production Deployment

### Environment Setup

```bash
# Production environment file
cp .env.example .env.production

# Configure production settings
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export DEBUG=false
```

### Docker Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  whatsapp-manager:
    build: .
    restart: unless-stopped
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    ports:
      - "8501:8501"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Security Considerations

1. **Environment Variables**
   - Use Docker secrets in production
   - Never commit `.env` files
   - Rotate API keys regularly

2. **Network Security**
   - Use internal Docker networks
   - Implement proper firewall rules
   - Enable HTTPS in production

3. **Data Protection**
   - Regular backups of data directory
   - Secure file permissions
   - Monitor access logs

## Scaling Options

### Horizontal Scaling

```yaml
# docker-compose.scale.yml
version: '3.8'
services:
  whatsapp-manager:
    build: .
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

### Load Balancing

```yaml
# Add nginx load balancer
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - whatsapp-manager
```

## Monitoring & Logging

### Centralized Logging

```yaml
# Add logging service
logging:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  volumes:
    - loki-data:/loki

# Configure app logging
whatsapp-manager:
  logging:
    driver: loki
    options:
      loki-url: "http://localhost:3100/loki/api/v1/push"
```

### Health Monitoring

```bash
# Health check script
#!/bin/bash
HEALTH_URL="http://localhost:8501"
if curl -f $HEALTH_URL > /dev/null 2>&1; then
    echo "✅ Service healthy"
    exit 0
else
    echo "❌ Service unhealthy"
    exit 1
fi
```

## Backup & Recovery

### Data Backup

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Create backup
docker run --rm \
  -v $(pwd)/data:/source \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/whatsapp-manager-$DATE.tar.gz -C /source .

echo "Backup created: whatsapp-manager-$DATE.tar.gz"
```

### Restore Process

```bash
#!/bin/bash
# restore.sh
BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh backup-file.tar.gz"
    exit 1
fi

# Stop services
docker-compose down

# Restore data
docker run --rm \
  -v $(pwd)/data:/target \
  -v /backups:/backup \
  alpine tar xzf /backup/$BACKUP_FILE -C /target

# Restart services
docker-compose up -d
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   # Check logs
   docker-compose logs whatsapp-manager
   
   # Check environment
   docker-compose config
   ```

2. **API Connection Issues**
   ```bash
   # Test connectivity
   docker exec whatsapp-manager curl -v $EVO_BASE_URL
   
   # Check environment variables
   docker exec whatsapp-manager env | grep EVO_
   ```

3. **Permission Issues**
   ```bash
   # Fix data directory permissions
   sudo chown -R 1000:1000 ./data
   sudo chmod -R 755 ./data
   ```

### Debug Mode

```bash
# Enable debug logging
docker-compose down
export DEBUG=true
export LOG_LEVEL=DEBUG
docker-compose up -d

# View detailed logs
docker-compose logs -f whatsapp-manager
```

## Performance Tuning

### Resource Limits

```yaml
# docker-compose.yml
services:
  whatsapp-manager:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Optimization Tips

1. **Memory Usage**
   - Monitor container memory usage
   - Adjust Python memory settings
   - Clean up old logs regularly

2. **CPU Usage**
   - Monitor during AI processing
   - Consider CPU limits for stable performance
   - Scale horizontally for high loads

3. **Storage**
   - Regular log rotation
   - Archive old data
   - Monitor disk usage

## Update Procedures

### Rolling Updates

```bash
# Pull latest version
git pull origin main

# Build new image
docker-compose build --no-cache

# Rolling update
docker-compose up -d --no-deps whatsapp-manager
```

### Rollback Procedure

```bash
# Tag current version before update
docker tag whatsapp-manager:latest whatsapp-manager:backup

# Rollback if needed
docker-compose down
docker tag whatsapp-manager:backup whatsapp-manager:latest
docker-compose up -d
```

---

*For additional deployment scenarios or custom configurations, please refer to the [Docker debugging guide](docker-debugging.md) or open an issue on GitHub.*
