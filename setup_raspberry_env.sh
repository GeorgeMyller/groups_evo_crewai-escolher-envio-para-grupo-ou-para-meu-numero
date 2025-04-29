#!/bin/bash
# setup_raspberry_env.sh - Configura as variáveis de ambiente no Raspberry Pi

# Configurações
RASPBERRY_IP="192.168.1.205"
RASPBERRY_USER="george"

# Exibir mensagem de início
echo "🔧 Configurando ambiente no Raspberry Pi ($RASPBERRY_IP)"

# Criar arquivo de variáveis de ambiente no Raspberry Pi
ssh $RASPBERRY_USER@$RASPBERRY_IP << 'EOF'
cat > ~/.whatsapp_env << 'ENVFILE'
# Configurações da API Evolution
EVO_BASE_URL=http://your-evolution-api-url:8080
EVO_API_TOKEN=your-api-token
EVO_INSTANCE_NAME=your-instance-name
EVO_INSTANCE_TOKEN=your-instance-token

# Número do WhatsApp (opcional - para envios pessoais)
WHATSAPP_NUMBER=your-number-with-country-code
ENVFILE

echo "⚠️  Edite o arquivo ~/.whatsapp_env com seus dados reais!"
echo "📝 Use o comando: nano ~/.whatsapp_env"
EOF

if [ $? -ne 0 ]; then
    echo "❌ Falha ao configurar variáveis de ambiente no Raspberry Pi"
    exit 1
fi

echo "✅ Arquivo de configuração criado no Raspberry Pi"
echo "⚠️  Importante: Conecte-se ao Raspberry Pi e edite o arquivo com seus dados reais:"
echo "   ssh $RASPBERRY_USER@$RASPBERRY_IP"
echo "   nano ~/.whatsapp_env"
