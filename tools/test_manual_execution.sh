#!/bin/bash

# Script para testar manualmente a execução de tarefas de resumo
# Script to manually test summary task execution

echo "🧪 Teste Manual de Execução de Tarefa / Manual Task Execution Test"
echo "=================================================================="

# Verificar se o container está rodando
CONTAINER_NAME="groups-evo-crewai"

if ! docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container '$CONTAINER_NAME' não está rodando!"
    echo "   Execute: docker-compose up -d"
    exit 1
fi

echo "✅ Container '$CONTAINER_NAME' encontrado"
echo ""

# Função para listar grupos disponíveis
list_groups() {
    echo "📋 Buscando grupos disponíveis no CSV..."
    docker exec "$CONTAINER_NAME" python3 -c "
import sys
sys.path.insert(0, '/app/src')

try:
    from whatsapp_manager.core.group_controller import GroupController
    import pandas as pd
    import os
    
    # Verificar se o arquivo group_summary.csv existe
    csv_path = '/app/data/group_summary.csv'
    if not os.path.exists(csv_path):
        print('❌ Arquivo group_summary.csv não encontrado')
        print(f'   Procurado em: {csv_path}')
        sys.exit(1)
    
    # Carregar dados
    df = pd.read_csv(csv_path)
    
    if df.empty:
        print('⚠️  Nenhum grupo encontrado no CSV')
    else:
        print(f'✅ {len(df)} grupos encontrados:')
        print('=' * 50)
        for idx, row in df.iterrows():
            status = '🟢 Habilitado' if row.get('enabled', False) else '🔴 Desabilitado'
            print(f'{idx + 1:2d}. ID: {row[\"group_id\"]} | {status}')
            print(f'    Horário: {row.get(\"time\", \"N/A\")}')
            print(f'    Min. mensagens: {row.get(\"min_messages_summary\", \"N/A\")}')
            print()
            
except Exception as e:
    print(f'❌ Erro ao listar grupos: {str(e)}')
    import traceback
    traceback.print_exc()
" 2>/dev/null || echo "❌ Erro ao executar listagem de grupos"
}

# Função para executar tarefa manualmente
execute_task() {
    local group_id=$1
    local task_name="ResumoGrupo_${group_id}"
    
    echo "🚀 Executando tarefa manualmente..."
    echo "   Grupo ID: $group_id"
    echo "   Task Name: $task_name"
    echo ""
    
    # Criar arquivo de log específico para este teste
    local test_log="/app/data/manual_test_$(date +%Y%m%d_%H%M%S).log"
    
    echo "📝 Logs serão salvos em: $test_log"
    echo ""
    
    # Executar a tarefa usando o mesmo método que o cron
    docker exec "$CONTAINER_NAME" bash -c "
        echo 'Iniciando teste manual em $(date)' > $test_log
        echo 'Diretório atual: $(pwd)' >> $test_log
        echo 'Usuário: $(whoami)' >> $test_log
        echo 'Variáveis de ambiente:' >> $test_log
        env | grep -E '(WHATSAPP|EVO_|PYTHONPATH)' >> $test_log
        echo '=========================' >> $test_log
        
        # Executar com o mesmo script que o cron usa
        /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name $task_name 2>&1 | tee -a $test_log
        echo 'Código de saída: \$?' >> $test_log
    "
    
    echo ""
    echo "✅ Execução finalizada. Verificando logs..."
    
    # Mostrar os últimos logs
    docker exec "$CONTAINER_NAME" tail -20 "$test_log"
}

# Função para verificar logs de execuções anteriores
check_execution_logs() {
    echo "📋 Verificando logs de execuções do cron..."
    echo "==========================================="
    
    # Verificar log do cron
    if docker exec "$CONTAINER_NAME" test -f /app/data/cron_execution.log; then
        echo "📁 Log de execuções do cron:"
        docker exec "$CONTAINER_NAME" tail -20 /app/data/cron_execution.log
    else
        echo "⚠️  Log de execuções do cron não encontrado"
    fi
    
    echo ""
    
    # Verificar logs específicos de tarefas
    docker exec "$CONTAINER_NAME" find /app/data -name "*.log" -type f | while read log_file; do
        echo "📁 $log_file:"
        docker exec "$CONTAINER_NAME" tail -5 "$log_file"
        echo ""
    done
}

# Menu principal
show_menu() {
    echo "Escolha uma opção / Choose an option:"
    echo "1) 📋 Listar grupos disponíveis / List available groups"
    echo "2) 🚀 Executar tarefa manualmente / Execute task manually"
    echo "3) 📋 Verificar logs de execução / Check execution logs"
    echo "4) 🔍 Diagnóstico de ambiente / Environment diagnosis"
    echo "5) 🚪 Sair / Exit"
    echo ""
    read -p "Digite sua escolha (1-5): " choice
}

# Diagnóstico de ambiente
environment_diagnosis() {
    echo "🔍 DIAGNÓSTICO DO AMBIENTE:"
    echo "=========================="
    
    docker exec "$CONTAINER_NAME" bash -c '
        echo "📂 Estrutura de diretórios:"
        ls -la /app/src/whatsapp_manager/core/ | grep summary
        echo ""
        
        echo "🐍 Teste de importação:"
        cd /app
        python3 -c "
import sys
sys.path.insert(0, \"/app/src\")
try:
    from whatsapp_manager.core.summary import *
    print(\"✅ Importação de summary.py: OK\")
except Exception as e:
    print(f\"❌ Erro na importação: {e}\")

try:
    from whatsapp_manager.core.group_controller import GroupController
    print(\"✅ Importação de GroupController: OK\")
except Exception as e:
    print(f\"❌ Erro na importação: {e}\")
"
        echo ""
        
        echo "📋 Arquivos de dados:"
        ls -la /app/data/ 2>/dev/null || echo "Diretório /app/data não encontrado"
    '
}

# Loop principal
while true; do
    show_menu
    
    case $choice in
        1)
            list_groups
            ;;
        2)
            echo ""
            read -p "Digite o Group ID para testar: " group_id
            if [ -n "$group_id" ]; then
                execute_task "$group_id"
            else
                echo "❌ Group ID não pode estar vazio"
            fi
            ;;
        3)
            check_execution_logs
            ;;
        4)
            environment_diagnosis
            ;;
        5)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida. Tente novamente."
            ;;
    esac
    
    echo ""
    read -p "Pressione Enter para continuar..."
    echo ""
done
