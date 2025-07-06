#!/bin/bash

# Script para diagnosticar e corrigir problemas de instância
# Script to diagnose and fix instance problems

echo "🔧 Diagnóstico de Problemas da Instância / Instance Problems Diagnosis"
echo "====================================================================="

CONTAINER_NAME="groups-evo-crewai"

if ! docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container não está rodando"
    exit 1
fi

echo "🔍 Testando conectividade detalhada da API..."

# Teste detalhado da API
docker exec "$CONTAINER_NAME" python3 -c "
import sys
sys.path.insert(0, '/app/src')
import os

print('=== TESTE DETALHADO DA API ===')
print(f'Base URL: {os.getenv(\"EVO_BASE_URL\")}')
print(f'Instance Name: {os.getenv(\"EVO_INSTANCE_NAME\")}')

try:
    from whatsapp_manager.infrastructure.api.evolution_client import EvolutionClientWrapper
    
    client = EvolutionClientWrapper(
        base_url=os.getenv('EVO_BASE_URL'),
        api_token=os.getenv('EVO_API_TOKEN'),
        instance_id=os.getenv('EVO_INSTANCE_NAME'),
        instance_token=os.getenv('EVO_INSTANCE_TOKEN')
    )
    
    print('✅ Cliente criado com sucesso')
    
    # Teste de ping básico
    if client.ping_api():
        print('✅ Ping da API: OK')
    else:
        print('❌ Ping da API: FALHOU')
        
    # Verificar status detalhado
    print('\\n=== STATUS DA CONEXÃO ===')
    status = client.check_connection_status()
    print(f'Conectado: {status.get(\"connected\", False)}')
    print(f'Estado: {status.get(\"state\", \"unknown\")}')
    print(f'Instance ID: {status.get(\"instance_id\", \"N/A\")}')
    
    if \"error\" in status:
        print(f'Erro: {status[\"error\"]}')
        
    # Listar todas as instâncias disponíveis
    print('\\n=== INSTÂNCIAS DISPONÍVEIS ===')
    try:
        instances = client.client.instances.fetch_instances()
        print(f'Total de instâncias encontradas: {len(instances)}')
        
        for i, instance_data in enumerate(instances):
            instance = instance_data.get(\"instance\", {})
            name = instance.get(\"instanceName\", \"N/A\")
            status_inst = instance.get(\"status\", \"N/A\")
            print(f'{i+1}. Nome: {name} | Status: {status_inst}')
            
            # Verificar se é nossa instância
            if name == os.getenv(\"EVO_INSTANCE_NAME\"):
                print(f'   ⭐ Esta é nossa instância configurada!')
                print(f'   Detalhes: {instance}')
                
    except Exception as e:
        print(f'❌ Erro ao listar instâncias: {str(e)}')
        
    # Teste de busca de grupos
    print('\\n=== TESTE DE GRUPOS ===')
    try:
        groups = client.fetch_all_groups(get_participants=False)
        print(f'✅ Grupos encontrados: {len(groups)}')
    except Exception as e:
        print(f'❌ Erro ao buscar grupos: {str(e)}')
        
except Exception as e:
    print(f'❌ Erro geral: {str(e)}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "🔧 Verificando configuração do crontab..."

# Verificar o crontab atual
echo "Agendamento atual:"
docker exec "$CONTAINER_NAME" crontab -l

echo ""
echo "🧪 Executando teste manual da tarefa..."

# Executar teste manual
docker exec "$CONTAINER_NAME" bash -c "
    echo '=== TESTE MANUAL ==='
    echo 'Data/Hora atual:' \$(date)
    echo 'Diretório:' \$(pwd)
    echo 'Usuário:' \$(whoami)
    echo 'PYTHONPATH:' \$PYTHONPATH
    echo ''
    
    # Executar o script diretamente
    echo 'Executando summary.py diretamente...'
    /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name ResumoGrupo_120363400095683544@g.us
"

echo ""
echo "📋 Verificando logs de execução..."

# Verificar se foram gerados logs
docker exec "$CONTAINER_NAME" bash -c "
    echo 'Arquivos de log criados:'
    find /app/data -name '*.log' -type f -exec ls -la {} \;
    echo ''
    
    if [ -f /app/data/cron_execution.log ]; then
        echo 'Últimas linhas do log de execução:'
        tail -10 /app/data/cron_execution.log
    fi
"
