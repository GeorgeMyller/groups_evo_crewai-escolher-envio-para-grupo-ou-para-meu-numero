#!/bin/bash

# Script específico para testar execução do summary.py no Docker
# Specific script to test summary.py execution in Docker

echo "🧪 Teste Específico: summary.py no Docker"
echo "========================================="

CONTAINER_NAME="groups-evo-crewai"

if ! docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container não está rodando"
    exit 1
fi

echo "🔍 Verificando arquivos no Docker..."

# Verificar se os arquivos existem
docker exec "$CONTAINER_NAME" bash -c "
    echo '=== VERIFICAÇÃO DE ARQUIVOS ==='
    echo 'Diretório atual:' \$(pwd)
    echo ''
    
    echo 'Arquivo summary.py:'
    if [ -f /app/src/whatsapp_manager/core/summary.py ]; then
        echo '✅ summary.py existe'
        echo \"   Tamanho: \$(wc -c < /app/src/whatsapp_manager/core/summary.py) bytes\"
        echo \"   Permissões: \$(ls -la /app/src/whatsapp_manager/core/summary.py)\"
    else
        echo '❌ summary.py NÃO existe'
        echo 'Procurando arquivos similares:'
        find /app -name '*summary*' -type f
    fi
    
    echo ''
    echo 'Arquivo load_env.sh:'
    if [ -f /usr/local/bin/load_env.sh ]; then
        echo '✅ load_env.sh existe'
        echo \"   Tamanho: \$(wc -c < /usr/local/bin/load_env.sh) bytes\"
        echo \"   Permissões: \$(ls -la /usr/local/bin/load_env.sh)\"
        echo \"   Primeiras linhas:\"
        head -3 /usr/local/bin/load_env.sh
    else
        echo '❌ load_env.sh NÃO existe'
    fi
    
    echo ''
    echo 'Arquivo .env:'
    if [ -f /app/.env ]; then
        echo '✅ .env existe'
        echo \"   Tamanho: \$(wc -c < /app/.env) bytes\"
    else
        echo '❌ .env NÃO existe'
    fi
"

echo ""
echo "🧪 Teste direto do Python no Docker..."

# Testar Python diretamente
docker exec "$CONTAINER_NAME" bash -c "
    echo '=== TESTE DIRETO DO PYTHON ==='
    cd /app
    
    # Carregar variáveis de ambiente
    source /app/.env 2>/dev/null
    export PYTHONPATH='/app/src:\$PYTHONPATH'
    
    echo 'PYTHONPATH:' \$PYTHONPATH
    echo ''
    
    echo 'Testando importações:'
    python3 -c \"
import sys
sys.path.insert(0, '/app/src')

try:
    import whatsapp_manager
    print('✅ Pacote whatsapp_manager importado')
except Exception as e:
    print(f'❌ Erro ao importar pacote: {e}')

try:
    from whatsapp_manager.core.group_controller import GroupController
    print('✅ GroupController importado')
except Exception as e:
    print(f'❌ Erro ao importar GroupController: {e}')

try:
    from whatsapp_manager.core.summary_crew import SummaryCrew
    print('✅ SummaryCrew importado')
except Exception as e:
    print(f'❌ Erro ao importar SummaryCrew: {e}')

try:
    from whatsapp_manager.core.send_sandeco import SendSandeco
    print('✅ SendSandeco importado')
except Exception as e:
    print(f'❌ Erro ao importar SendSandeco: {e}')
\"
"

echo ""
echo "🚀 Teste de execução com método alternativo..."

# Tentar executar de forma alternativa
docker exec "$CONTAINER_NAME" bash -c "
    echo '=== EXECUÇÃO ALTERNATIVA ==='
    cd /app
    source /app/.env 2>/dev/null
    export PYTHONPATH='/app/src'
    
    # Buscar um group_id válido
    group_id=''
    if [ -f /app/data/group_summary.csv ]; then
        group_id=\$(head -2 /app/data/group_summary.csv | tail -1 | cut -d',' -f1)
        echo \"Group ID encontrado: \$group_id\"
    else
        echo 'CSV não encontrado, usando ID de teste'
        group_id='120363400095683544@g.us'
    fi
    
    echo \"Executando com group_id: \$group_id\"
    echo ''
    
    # Método 1: Execução direta com python3
    echo '--- Método 1: Python direto ---'
    python3 /app/src/whatsapp_manager/core/summary.py --task_name \"ResumoGrupo_\$group_id\" 2>&1 || echo 'Falhou método 1'
    
    echo ''
    echo '--- Método 2: Com bash wrapper ---'
    bash -c \"
        source /app/.env
        export PYTHONPATH='/app/src'
        python3 /app/src/whatsapp_manager/core/summary.py --task_name ResumoGrupo_\$group_id
    \" 2>&1 || echo 'Falhou método 2'
"

echo ""
echo "📋 Verificando logs gerados..."

# Verificar se foram gerados logs
docker exec "$CONTAINER_NAME" bash -c "
    echo '=== LOGS GERADOS ==='
    
    if [ -f /app/data/cron_execution.log ]; then
        echo 'Log de execução:'
        tail -5 /app/data/cron_execution.log
    else
        echo 'Nenhum log de execução encontrado'
    fi
    
    echo ''
    echo 'Outros logs na pasta data:'
    ls -la /app/data/*.log 2>/dev/null || echo 'Nenhum arquivo .log encontrado'
"

echo ""
echo "💡 ANÁLISE DOS RESULTADOS:"
echo "========================="
echo "- Se 'summary.py NÃO existe' → problema na cópia do arquivo"
echo "- Se 'exec format error' → problema no shebang do load_env.sh"
echo "- Se erro de importação → problema no PYTHONPATH"
echo "- Se erro de API → problema de conectividade"
echo ""
echo "🔧 PRÓXIMOS PASSOS:"
echo "- Execute: docker-compose down && docker-compose build --no-cache && docker-compose up -d"
echo "- Depois execute este script novamente"
