#!/bin/bash
# Script limpo de comandos Docker/docker-compose

RASPBERRY_IP="192.168.1.205"
RASPBERRY_USER="george"
PROJECT_DIR="whatsapp-summarizer"

# Exibir mensagem de início
echo "🚀 Iniciando processo de implantação para Raspberry Pi ($RASPBERRY_IP)"

# Etapa 1: Criar diretório de projeto no Raspberry Pi
echo "📁 Criando diretório de projeto no Raspberry Pi..."
ssh $RASPBERRY_USER@$RASPBERRY_IP "mkdir -p ~/$PROJECT_DIR"

# Etapa 2: Copiar arquivos necessários para o Raspberry Pi
echo "📤 Transferindo arquivos para o Raspberry Pi..."
scp pyproject.toml uv.lock $RASPBERRY_USER@$RASPBERRY_IP:~/$PROJECT_DIR/
scp -r app.py group*.py groups_util.py message_sandeco.py send_sandeco.py summary*.py task_scheduler.py $RASPBERRY_USER@$RASPBERRY_IP:~/$PROJECT_DIR/
scp -r pages $RASPBERRY_USER@$RASPBERRY_IP:~/$PROJECT_DIR/

echo "✅ Implantação concluída (sem Docker)."
