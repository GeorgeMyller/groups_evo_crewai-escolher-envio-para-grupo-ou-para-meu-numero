#!/bin/bash

# Script de diagnóstico rápido para problemas com agendamento
# Quick diagnostic script for scheduling problems

echo "🔧 Diagnóstico Rápido - WhatsApp Manager"
echo "======================================="

CONTAINER_NAME="groups-evo-crewai"

# Verificar se container está rodando
if ! docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "❌ PROBLEMA: Container não está rodando"
    echo "   SOLUÇÃO: Execute 'docker-compose up -d'"
    exit 1
fi

echo "✅ Container está rodando"

# Verificar se o Streamlit está acessível
echo ""
echo "🌐 Testando acesso ao Streamlit..."
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Streamlit acessível na porta 8501"
else
    echo "❌ PROBLEMA: Streamlit não acessível"
    echo "   Verifique os logs: docker logs $CONTAINER_NAME"
fi

# Verificar crontab
echo ""
echo "⏰ Verificando agendamentos..."
cron_output=$(docker exec "$CONTAINER_NAME" crontab -l 2>/dev/null)
if [ -n "$cron_output" ]; then
    echo "✅ Tarefas agendadas encontradas:"
    echo "$cron_output" | grep "ResumoGrupo" | wc -l | xargs echo "   Quantidade:"
else
    echo "⚠️  ATENÇÃO: Nenhuma tarefa agendada encontrada"
    echo "   Agende tarefas através do Streamlit"
fi

# Verificar arquivo .env
echo ""
echo "🔧 Verificando configuração..."
env_check=$(docker exec "$CONTAINER_NAME" test -f /app/.env && echo "existe" || echo "não existe")
if [ "$env_check" = "existe" ]; then
    echo "✅ Arquivo .env encontrado"
    
    # Verificar variáveis críticas
    docker exec "$CONTAINER_NAME" bash -c '
        source /app/.env
        missing=0
        
        if [ -z "$WHATSAPP_NUMBER" ]; then
            echo "❌ WHATSAPP_NUMBER não definido"
            missing=1
        fi
        
        if [ -z "$EVO_BASE_URL" ]; then
            echo "❌ EVO_BASE_URL não definido"
            missing=1
        fi
        
        if [ -z "$EVO_INSTANCE_NAME" ]; then
            echo "❌ EVO_INSTANCE_NAME não definido"
            missing=1
        fi
        
        if [ -z "$EVO_API_TOKEN" ]; then
            echo "❌ EVO_API_TOKEN não definido"
            missing=1
        fi
        
        if [ -z "$EVO_INSTANCE_TOKEN" ]; then
            echo "❌ EVO_INSTANCE_TOKEN não definido"
            missing=1
        fi
        
        if [ $missing -eq 0 ]; then
            echo "✅ Todas as variáveis necessárias estão definidas"
        fi
    '
else
    echo "❌ PROBLEMA CRÍTICO: Arquivo .env não encontrado"
    echo "   SOLUÇÃO: Crie o arquivo .env na raiz do projeto"
fi

# Verificar conectividade da API
echo ""
echo "🌐 Testando conectividade da API..."
api_test=$(docker exec "$CONTAINER_NAME" timeout 10 python3 -c "
import sys
sys.path.insert(0, '/app/src')

try:
    from whatsapp_manager.infrastructure.api.evolution_client import EvolutionClientWrapper
    import os
    
    client = EvolutionClientWrapper(
        base_url=os.getenv('EVO_BASE_URL'),
        api_token=os.getenv('EVO_API_TOKEN'),
        instance_id=os.getenv('EVO_INSTANCE_NAME'),
        instance_token=os.getenv('EVO_INSTANCE_TOKEN')
    )
    
    if client.ping_api():
        print('API_OK')
    else:
        print('API_FAIL')
        
except Exception as e:
    print(f'API_ERROR:{str(e)}')
" 2>/dev/null)

case $api_test in
    "API_OK")
        echo "✅ API acessível e funcionando"
        ;;
    "API_FAIL")
        echo "❌ PROBLEMA: API acessível mas não funcional"
        echo "   Verifique os tokens e configurações"
        ;;
    API_ERROR:*)
        echo "❌ PROBLEMA: Erro na API - ${api_test#API_ERROR:}"
        ;;
    *)
        echo "❌ PROBLEMA: Não foi possível testar a API"
        echo "   Verifique as configurações de rede"
        ;;
esac

# Verificar logs recentes
echo ""
echo "📋 Últimos logs de execução..."
if docker exec "$CONTAINER_NAME" test -f /app/data/cron_execution.log; then
    echo "✅ Log de execução encontrado:"
    docker exec "$CONTAINER_NAME" tail -3 /app/data/cron_execution.log
else
    echo "⚠️  Nenhum log de execução encontrado ainda"
fi

# Verificar diretórios de dados
echo ""
echo "📁 Verificando estrutura de dados..."
data_structure=$(docker exec "$CONTAINER_NAME" ls -la /app/data/ 2>/dev/null)
if [ -n "$data_structure" ]; then
    echo "✅ Diretório de dados existe"
    csv_exists=$(echo "$data_structure" | grep -q "group_summary.csv" && echo "sim" || echo "não")
    echo "   group_summary.csv: $csv_exists"
else
    echo "❌ PROBLEMA: Diretório de dados não encontrado"
fi

echo ""
echo "🎯 RESUMO DO DIAGNÓSTICO"
echo "======================="
echo "Para monitorar em tempo real:"
echo "  ./tools/monitor_docker_logs.sh"
echo ""
echo "Para testar execução manual:"
echo "  ./tools/test_manual_execution.sh"
echo ""
echo "Para ver logs do container:"
echo "  docker logs -f $CONTAINER_NAME"
