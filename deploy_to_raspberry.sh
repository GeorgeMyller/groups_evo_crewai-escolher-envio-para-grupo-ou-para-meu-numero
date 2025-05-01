#!/bin/bash
# deploy_to_raspberry.sh - Script para construir e implantar o projeto no Raspberry Pi

# Configurações
RASPBERRY_IP="192.168.1.205"
RASPBERRY_USER="george"
IMAGE_NAME="whatsapp-group-summarizer"
IMAGE_TAG="latest"
CONTAINER_NAME="whatsapp-summarizer"

# Exibir mensagem de início
echo "🚀 Iniciando processo de implantação para Raspberry Pi ($RASPBERRY_IP)"

# Etapa 1: Construir a imagem Docker localmente
echo "🏗️  Construindo imagem Docker..."
docker build -t $IMAGE_NAME:$IMAGE_TAG .

if [ $? -ne 0 ]; then
    echo "❌ Falha ao construir a imagem Docker"
    exit 1
fi

# Etapa 2: Salvar a imagem como arquivo tar
echo "💾 Salvando imagem Docker como arquivo..."
docker save $IMAGE_NAME:$IMAGE_TAG | gzip > ${IMAGE_NAME}.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ Falha ao salvar a imagem Docker"
    exit 1
fi

# Etapa 3: Transferir a imagem para o Raspberry Pi
echo "📤 Transferindo imagem para o Raspberry Pi..."
scp ${IMAGE_NAME}.tar.gz $RASPBERRY_USER@$RASPBERRY_IP:~

if [ $? -ne 0 ]; then
    echo "❌ Falha ao transferir a imagem para o Raspberry Pi"
    exit 1
fi

# Etapa 4: Carregar a imagem no Docker do Raspberry Pi e executar o container
echo "🔄 Carregando e executando o container no Raspberry Pi..."
ssh $RASPBERRY_USER@$RASPBERRY_IP << EOF
    echo "📦 Carregando imagem Docker..."
    docker load < ~/${IMAGE_NAME}.tar.gz
    
    echo "🛑 Parando e removendo container existente (se houver)..."
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    echo "▶️  Iniciando novo container..."
    docker run -d \
        --name $CONTAINER_NAME \
        --restart unless-stopped \
        -p 8501:8501 \
        --env-file ~/.env \
        --env-file "${REMOTE_PATH}.env" \
        --restart unless-stopped ${IMAGE_NAME}:${IMAGE_TAG}

    echo "🧹 Limpando arquivo de imagem..."
    rm ~/${IMAGE_NAME}.tar.gz
EOF

if [ $? -ne 0 ]; then
    echo "❌ Falha ao executar comandos no Raspberry Pi"
    exit 1
fi

# Etapa 5: Limpeza local
echo "🧹 Removendo arquivo de imagem local..."
rm ${IMAGE_NAME}.tar.gz

echo "✅ Implantação concluída com sucesso!"
echo "📱 Acesse a aplicação em: http://$RASPBERRY_IP:8501"
