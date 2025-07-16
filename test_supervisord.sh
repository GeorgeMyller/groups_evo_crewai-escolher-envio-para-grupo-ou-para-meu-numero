#!/bin/bash

echo "=== TESTE DE CONFIGURAÇÃO SUPERVISORD ==="
echo "Data: $(date)"
echo

# Teste 1: Verificar sintaxe do supervisord.conf
echo "1. Verificando sintaxe do supervisord.conf..."
if command -v supervisord &> /dev/null; then
    supervisord -c supervisord.conf -t
    if [ $? -eq 0 ]; then
        echo "✅ Sintaxe do supervisord.conf está correta"
    else
        echo "❌ Erro na sintaxe do supervisord.conf"
    fi
else
    echo "⚠️  supervisord não está instalado localmente, pulando teste de sintaxe"
fi

# Teste 2: Verificar se o docker-entrypoint.sh tem permissões corretas
echo
echo "2. Verificando permissões do docker-entrypoint.sh..."
if [ -x "docker-entrypoint.sh" ]; then
    echo "✅ docker-entrypoint.sh tem permissões de execução"
else
    echo "❌ docker-entrypoint.sh não tem permissões de execução"
    echo "Corrigindo..."
    chmod +x docker-entrypoint.sh
fi

# Teste 3: Verificar se o docker-compose.yml existe
echo
echo "3. Verificando docker-compose.yml..."
if [ -f "docker-compose.yml" ]; then
    echo "✅ docker-compose.yml encontrado"
    echo "Conteúdo:"
    cat docker-compose.yml
else
    echo "❌ docker-compose.yml não encontrado"
fi

# Teste 4: Rebuildar o container
echo
echo "4. Rebuilding container..."
echo "Parando containers existentes..."
docker-compose down

echo "Removendo imagens antigas..."
docker-compose build --no-cache

echo "Iniciando containers..."
docker-compose up -d

echo
echo "=== VERIFICAÇÃO DOS LOGS ==="
echo "Aguardando 10 segundos para os serviços iniciarem..."
sleep 10

echo "Logs do supervisord:"
docker-compose logs --tail=20

echo
echo "=== TESTE CONCLUÍDO ==="
