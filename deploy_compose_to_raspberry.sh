#!/bin/bash
# deploy_compose_to_raspberry.sh - Script para implantar usando docker-compose no Raspberry Pi

# Configurações
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
scp Dockerfile docker-compose.yml pyproject.toml uv.lock $RASPBERRY_USER@$RASPBERRY_IP:~/$PROJECT_DIR/
scp -r app.py group*.py groups_util.py message_sandeco.py send_sandeco.py summary*.py task_scheduler.py $RASPBERRY_USER@$RASPBERRY_IP:~/$PROJECT_DIR/
scp -r pages $RASPBERRY_USER@$RASPBERRY_IP:~/$PROJECT_DIR/

# Etapa 3: Configurar e executar docker-compose no Raspberry Pi
echo "🔄 Configurando e executando no Raspberry Pi..."
ssh $RASPBERRY_USER@$RASPBERRY_IP << EOF
    cd ~/$PROJECT_DIR
    
    # Criar diretório de dados
    mkdir -p data
    
    # Copiar arquivo .env (se existir) ou criar um modelo
    if [ -f ~/.whatsapp_env ]; then
        cp ~/.whatsapp_env .env
    fi
    
    # Executar com docker-compose
    docker-compose up -d --build
EOF

if [ $? -ne 0 ]; then
    echo "❌ Falha ao executar comandos no Raspberry Pi"
    exit 1
fi

echo "✅ Implantação concluída com sucesso!"
echo "📱 Acesse a aplicação em: http://$RASPBERRY_IP:8501"
echo ""
echo "🔍 Para ver os logs do container:"
echo "   ssh $RASPBERRY_USER@$RASPBERRY_IP \"cd ~/$PROJECT_DIR && docker-compose logs -f\""
