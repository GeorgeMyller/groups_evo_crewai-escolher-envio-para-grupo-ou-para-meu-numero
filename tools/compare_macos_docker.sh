#!/bin/bash

# Script para diagnosticar diferenças entre macOS e Docker
# Script to diagnose differences between macOS and Docker

echo "🔍 Diagnóstico: Comparação macOS vs Docker"
echo "=========================================="

CONTAINER_NAME="groups-evo-crewai"

# Verificar se container está rodando
if ! docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container não está rodando"
    echo "   Execute: docker-compose up -d"
    exit 1
fi

echo "✅ Container encontrado: $CONTAINER_NAME"
echo ""

# Função para testar no macOS local
test_local_macos() {
    echo "🍎 TESTE NO MACOS LOCAL"
    echo "======================"
    
    echo "📂 Diretório atual:"
    pwd
    
    echo ""
    echo "🐍 Versão do Python:"
    python3 --version
    
    echo ""
    echo "📋 Variáveis de ambiente críticas:"
    echo "WHATSAPP_NUMBER: ${WHATSAPP_NUMBER:-[NÃO DEFINIDO]}"
    echo "EVO_BASE_URL: ${EVO_BASE_URL:-[NÃO DEFINIDO]}"
    echo "EVO_INSTANCE_NAME: ${EVO_INSTANCE_NAME:-[NÃO DEFINIDO]}"
    echo "PYTHONPATH: ${PYTHONPATH:-[NÃO DEFINIDO]}"
    
    echo ""
    echo "🧪 Teste de importação (macOS):"
    PYTHONPATH="./src:$PYTHONPATH" python3 -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python path: {sys.path}')
print()

try:
    from whatsapp_manager.core.group_controller import GroupController
    print('✅ GroupController importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar GroupController: {e}')

try:
    from whatsapp_manager.core.summary_crew import SummaryCrew
    print('✅ SummaryCrew importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar SummaryCrew: {e}')

try:
    from whatsapp_manager.core.send_sandeco import SendSandeco
    print('✅ SendSandeco importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar SendSandeco: {e}')

try:
    from whatsapp_manager.utils.logger import get_logger
    print('✅ Logger importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar Logger: {e}')
"
    
    echo ""
    echo "🌐 Teste de conectividade API (macOS):"
    PYTHONPATH="./src:$PYTHONPATH" python3 -c "
import sys
import os
sys.path.insert(0, './src')

try:
    from whatsapp_manager.infrastructure.api.evolution_client import EvolutionClientWrapper
    
    client = EvolutionClientWrapper(
        base_url=os.getenv('EVO_BASE_URL'),
        api_token=os.getenv('EVO_API_TOKEN'),
        instance_id=os.getenv('EVO_INSTANCE_NAME'),
        instance_token=os.getenv('EVO_INSTANCE_TOKEN')
    )
    
    print('✅ Cliente Evolution criado')
    
    if client.ping_api():
        print('✅ API acessível')
        status = client.check_connection_status()
        print(f'   Estado: {status.get(\"state\", \"unknown\")}')
        print(f'   Conectado: {status.get(\"connected\", False)}')
    else:
        print('❌ API não acessível')
        
except Exception as e:
    print(f'❌ Erro: {e}')
"
}

# Função para testar no Docker
test_docker() {
    echo "🐳 TESTE NO DOCKER"
    echo "=================="
    
    echo "📂 Informações do container:"
    docker exec "$CONTAINER_NAME" bash -c "
        echo \"Diretório atual: \$(pwd)\"
        echo \"Usuário: \$(whoami)\"
        echo \"Sistema: \$(uname -a)\"
    "
    
    echo ""
    echo "🐍 Versão do Python no Docker:"
    docker exec "$CONTAINER_NAME" python3 --version
    
    echo ""
    echo "📋 Variáveis de ambiente no Docker:"
    docker exec "$CONTAINER_NAME" bash -c "
        echo \"WHATSAPP_NUMBER: \${WHATSAPP_NUMBER:-[NÃO DEFINIDO]}\"
        echo \"EVO_BASE_URL: \${EVO_BASE_URL:-[NÃO DEFINIDO]}\"
        echo \"EVO_INSTANCE_NAME: \${EVO_INSTANCE_NAME:-[NÃO DEFINIDO]}\"
        echo \"PYTHONPATH: \${PYTHONPATH:-[NÃO DEFINIDO]}\"
    "
    
    echo ""
    echo "🧪 Teste de importação (Docker):"
    docker exec "$CONTAINER_NAME" python3 -c "
import sys
print(f'Python version: {sys.version}')
print(f'Python path: {sys.path}')
print()

sys.path.insert(0, '/app/src')

try:
    from whatsapp_manager.core.group_controller import GroupController
    print('✅ GroupController importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar GroupController: {e}')
    import traceback
    traceback.print_exc()

try:
    from whatsapp_manager.core.summary_crew import SummaryCrew
    print('✅ SummaryCrew importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar SummaryCrew: {e}')
    import traceback
    traceback.print_exc()

try:
    from whatsapp_manager.core.send_sandeco import SendSandeco
    print('✅ SendSandeco importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar SendSandeco: {e}')
    import traceback
    traceback.print_exc()

try:
    from whatsapp_manager.utils.logger import get_logger
    print('✅ Logger importado com sucesso')
except Exception as e:
    print(f'❌ Erro ao importar Logger: {e}')
    import traceback
    traceback.print_exc()
"

    echo ""
    echo "🌐 Teste de conectividade API (Docker):"
    docker exec "$CONTAINER_NAME" bash -c "
        source /app/.env
        python3 -c \"
import sys
import os
sys.path.insert(0, '/app/src')

try:
    from whatsapp_manager.infrastructure.api.evolution_client import EvolutionClientWrapper
    
    client = EvolutionClientWrapper(
        base_url=os.getenv('EVO_BASE_URL'),
        api_token=os.getenv('EVO_API_TOKEN'),
        instance_id=os.getenv('EVO_INSTANCE_NAME'),
        instance_token=os.getenv('EVO_INSTANCE_TOKEN')
    )
    
    print('✅ Cliente Evolution criado')
    
    if client.ping_api():
        print('✅ API acessível')
        status = client.check_connection_status()
        print(f'   Estado: {status.get(\\\"state\\\", \\\"unknown\\\")}')
        print(f'   Conectado: {status.get(\\\"connected\\\", False)}')
    else:
        print('❌ API não acessível')
        
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()
\"
    "
}

# Função para testar execução completa do summary.py
test_summary_execution() {
    echo ""
    echo "🧪 TESTE DE EXECUÇÃO DO SUMMARY.PY"
    echo "================================="
    
    # Buscar um group_id válido
    group_id=""
    if [ -f "./data/group_summary.csv" ]; then
        group_id=$(head -2 "./data/group_summary.csv" | tail -1 | cut -d',' -f1)
        echo "Group ID encontrado no CSV local: $group_id"
    else
        # Tentar do Docker
        group_id=$(docker exec "$CONTAINER_NAME" bash -c "
            if [ -f /app/data/group_summary.csv ]; then
                head -2 /app/data/group_summary.csv | tail -1 | cut -d',' -f1
            fi
        ")
        echo "Group ID encontrado no Docker: $group_id"
    fi
    
    if [ -n "$group_id" ]; then
        echo ""
        echo "🍎 Executando summary.py no macOS:"
        echo "--------------------------------"
        PYTHONPATH="./src:$PYTHONPATH" python3 ./src/whatsapp_manager/core/summary.py --task_name "ResumoGrupo_$group_id" || echo "❌ Falhou no macOS"
        
        echo ""
        echo "🐳 Executando summary.py no Docker:"
        echo "-----------------------------------"
        docker exec "$CONTAINER_NAME" /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name "ResumoGrupo_$group_id" || echo "❌ Falhou no Docker"
    else
        echo "⚠️  Nenhum group_id encontrado para teste"
    fi
}

# Função para comparar estruturas de arquivos
compare_file_structures() {
    echo ""
    echo "📁 COMPARAÇÃO DE ESTRUTURAS DE ARQUIVOS"
    echo "======================================="
    
    echo "🍎 Estrutura local (macOS):"
    find ./src/whatsapp_manager -name "*.py" | head -10
    
    echo ""
    echo "🐳 Estrutura no Docker:"
    docker exec "$CONTAINER_NAME" find /app/src/whatsapp_manager -name "*.py" | head -10
    
    echo ""
    echo "📋 Comparando arquivos específicos:"
    
    # Verificar summary.py
    if [ -f "./src/whatsapp_manager/core/summary.py" ]; then
        echo "✅ summary.py existe localmente"
        local_size=$(wc -c < "./src/whatsapp_manager/core/summary.py")
        echo "   Tamanho: $local_size bytes"
    else
        echo "❌ summary.py NÃO existe localmente"
    fi
    
    docker_summary_exists=$(docker exec "$CONTAINER_NAME" test -f /app/src/whatsapp_manager/core/summary.py && echo "sim" || echo "não")
    if [ "$docker_summary_exists" = "sim" ]; then
        echo "✅ summary.py existe no Docker"
        docker_size=$(docker exec "$CONTAINER_NAME" wc -c < /app/src/whatsapp_manager/core/summary.py)
        echo "   Tamanho: $docker_size bytes"
    else
        echo "❌ summary.py NÃO existe no Docker"
    fi
}

# Executar todos os testes
echo "Executando comparação completa..."
echo ""

test_local_macos
echo ""
test_docker
echo ""
compare_file_structures
echo ""
test_summary_execution

echo ""
echo "🎯 RESUMO DO DIAGNÓSTICO"
echo "======================="
echo "Compare os resultados acima para identificar diferenças entre:"
echo "- Importações de módulos"
echo "- Conectividade da API"
echo "- Estrutura de arquivos"
echo "- Execução do script principal"
echo ""
echo "💡 Próximos passos recomendados:"
echo "1. Se há erros de importação no Docker → verificar PYTHONPATH"
echo "2. Se há erros de API no Docker → verificar conectividade de rede"
echo "3. Se arquivos estão faltando → rebuildar container"
echo "4. Se variáveis de ambiente estão faltando → verificar .env"
