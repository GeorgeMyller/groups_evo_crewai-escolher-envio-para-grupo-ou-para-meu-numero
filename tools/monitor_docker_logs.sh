#!/bin/bash

# Script para monitorar logs do WhatsApp Manager no Docker
# Script to monitor WhatsApp Manager logs in Docker

echo "🔍 WhatsApp Manager - Monitor de Logs / Log Monitor"
echo "=================================================="

# Verificar se o container está rodando
CONTAINER_NAME="groups-evo-crewai"

if ! docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container '$CONTAINER_NAME' não está rodando!"
    echo "   Execute: docker-compose up -d"
    exit 1
fi

echo "✅ Container '$CONTAINER_NAME' encontrado"
echo ""

# Função para mostrar logs em tempo real
show_logs() {
    echo "📋 Monitorando logs do container..."
    echo "   Pressione Ctrl+C para parar"
    echo ""
    docker logs -f "$CONTAINER_NAME"
}

# Função para verificar crontab
check_crontab() {
    echo "⏰ Verificando tarefas agendadas (crontab):"
    echo "=========================================="
    docker exec "$CONTAINER_NAME" crontab -l 2>/dev/null || echo "Nenhuma tarefa agendada encontrada"
    echo ""
}

# Função para verificar arquivos de log internos
check_internal_logs() {
    echo "📄 Verificando logs internos do sistema:"
    echo "========================================"
    
    # Verificar se existem logs
    docker exec "$CONTAINER_NAME" find /app/data -name "*.log" -type f 2>/dev/null | while read log_file; do
        echo "📁 Log encontrado: $log_file"
        echo "   Últimas 10 linhas:"
        docker exec "$CONTAINER_NAME" tail -10 "$log_file" 2>/dev/null || echo "   Erro ao ler arquivo"
        echo ""
    done
    
    # Verificar log_summary.txt
    if docker exec "$CONTAINER_NAME" test -f /app/data/log_summary.txt; then
        echo "📁 Log tradicional: /app/data/log_summary.txt"
        echo "   Últimas 5 linhas:"
        docker exec "$CONTAINER_NAME" tail -5 /app/data/log_summary.txt
        echo ""
    else
        echo "⚠️  Log tradicional não encontrado: /app/data/log_summary.txt"
    fi
}

# Função para verificar processos dentro do container
check_processes() {
    echo "🔧 Verificando processos no container:"
    echo "====================================="
    docker exec "$CONTAINER_NAME" ps aux
    echo ""
}

# Função para verificar variáveis de ambiente
check_environment() {
    echo "🌍 Verificando variáveis de ambiente críticas:"
    echo "=============================================="
    docker exec "$CONTAINER_NAME" bash -c '
        echo "WHATSAPP_NUMBER: ${WHATSAPP_NUMBER:-[NÃO DEFINIDO]}"
        echo "EVO_BASE_URL: ${EVO_BASE_URL:-[NÃO DEFINIDO]}"
        echo "EVO_INSTANCE_NAME: ${EVO_INSTANCE_NAME:-[NÃO DEFINIDO]}"
        echo "EVO_API_TOKEN: ${EVO_API_TOKEN:+[DEFINIDO]}"
        echo "EVO_INSTANCE_TOKEN: ${EVO_INSTANCE_TOKEN:+[DEFINIDO]}"
        echo "PYTHONPATH: ${PYTHONPATH:-[NÃO DEFINIDO]}"
        echo "Working Directory: $(pwd)"
    '
    echo ""
}

# Função para testar conectividade da API
test_api_connectivity() {
    echo "🌐 Testando conectividade da API:"
    echo "================================="
    docker exec "$CONTAINER_NAME" python3 -c "
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
        print('✅ API acessível')
        status = client.check_connection_status()
        print(f'   Status da instância: {status.get(\"state\", \"unknown\")}')
        print(f'   Conectado: {status.get(\"connected\", False)}')
    else:
        print('❌ API não acessível')
        
except Exception as e:
    print(f'❌ Erro ao testar API: {str(e)}')
" 2>/dev/null || echo "❌ Erro ao executar teste de conectividade"
    echo ""
}

# Menu principal
show_menu() {
    echo "Escolha uma opção / Choose an option:"
    echo "1) 📋 Logs em tempo real / Real-time logs"
    echo "2) ⏰ Verificar crontab / Check crontab" 
    echo "3) 📄 Verificar logs internos / Check internal logs"
    echo "4) 🔧 Verificar processos / Check processes"
    echo "5) 🌍 Verificar ambiente / Check environment"
    echo "6) 🌐 Testar API / Test API"
    echo "7) 🔍 Diagnóstico completo / Full diagnosis"
    echo "8) 🚪 Sair / Exit"
    echo ""
    read -p "Digite sua escolha (1-8): " choice
}

# Loop principal
while true; do
    show_menu
    
    case $choice in
        1)
            show_logs
            ;;
        2)
            check_crontab
            ;;
        3)
            check_internal_logs
            ;;
        4)
            check_processes
            ;;
        5)
            check_environment
            ;;
        6)
            test_api_connectivity
            ;;
        7)
            echo "🔍 DIAGNÓSTICO COMPLETO:"
            echo "======================="
            check_environment
            check_crontab
            check_processes
            test_api_connectivity
            check_internal_logs
            echo "✅ Diagnóstico completo finalizado"
            echo ""
            ;;
        8)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida. Tente novamente."
            ;;
    esac
    
    if [ "$choice" != "1" ]; then
        echo ""
        read -p "Pressione Enter para continuar..."
        echo ""
    fi
done
