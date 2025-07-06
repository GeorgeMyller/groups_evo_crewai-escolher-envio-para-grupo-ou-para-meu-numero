#!/bin/bash

# Script para corrigir agendamentos de data específica para diário
# Script to fix specific date scheduling to daily

echo "🔄 Corretor de Agendamentos / Schedule Fixer"
echo "==========================================="

CONTAINER_NAME="groups-evo-crewai"

if ! docker ps --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
    echo "❌ Container não está rodando"
    exit 1
fi

echo "📋 Verificando agendamentos atuais..."

# Mostrar crontab atual
current_cron=$(docker exec "$CONTAINER_NAME" crontab -l 2>/dev/null)
echo "Agendamentos atuais:"
echo "$current_cron"
echo ""

# Verificar se há tarefas com data específica
specific_date_tasks=$(echo "$current_cron" | grep "ResumoGrupo" | grep -E "^[0-9]+ [0-9]+ [0-9]+ [0-9]+ \*")

if [ -n "$specific_date_tasks" ]; then
    echo "⚠️  Encontradas tarefas com datas específicas:"
    echo "$specific_date_tasks"
    echo ""
    
    echo "🔄 Convertendo para agendamento diário..."
    
    # Para cada tarefa encontrada, extrair informações e recriar
    echo "$specific_date_tasks" | while IFS= read -r line; do
        # Extrair informações da linha
        minute=$(echo "$line" | awk '{print $1}')
        hour=$(echo "$line" | awk '{print $2}')
        task_id=$(echo "$line" | grep -o "TASK_ID:[^[:space:]]*" | cut -d: -f2)
        
        echo "  Tarefa: $task_id"
        echo "  Horário original: $hour:$minute"
        
        # Remover a tarefa antiga
        docker exec "$CONTAINER_NAME" bash -c "
            crontab -l 2>/dev/null | grep -v 'TASK_ID:$task_id' | crontab -
        "
        
        # Adicionar nova tarefa diária
        docker exec "$CONTAINER_NAME" bash -c "
            (crontab -l 2>/dev/null ; echo '$minute $hour * * * /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name $task_id # TASK_ID:$task_id') | crontab -
        "
        
        echo "  ✅ Convertido para execução diária às $hour:$minute"
    done
    
    echo ""
    echo "📋 Agendamentos após correção:"
    docker exec "$CONTAINER_NAME" crontab -l 2>/dev/null
    
else
    echo "✅ Nenhuma tarefa com data específica encontrada"
fi

echo ""
echo "🧪 Testando próxima execução..."

# Calcular quando seria a próxima execução
docker exec "$CONTAINER_NAME" python3 -c "
from datetime import datetime, timedelta
import subprocess

# Obter crontab atual
try:
    result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
    cron_lines = result.stdout.strip().split('\n') if result.stdout else []
    
    print('=== PRÓXIMAS EXECUÇÕES ===')
    now = datetime.now()
    print(f'Hora atual: {now.strftime(\"%Y-%m-%d %H:%M:%S\")}')
    print()
    
    for line in cron_lines:
        if 'ResumoGrupo' in line and 'TASK_ID:' in line:
            parts = line.split()
            if len(parts) >= 5:
                minute, hour = int(parts[0]), int(parts[1])
                task_id = line.split('TASK_ID:')[1].strip()
                
                # Calcular próxima execução
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
                
                time_until = next_run - now
                
                print(f'Tarefa: {task_id}')
                print(f'Próxima execução: {next_run.strftime(\"%Y-%m-%d %H:%M:%S\")}')
                print(f'Tempo restante: {time_until}')
                print()
                
except Exception as e:
    print(f'Erro ao calcular próximas execuções: {e}')
"

echo ""
echo "💡 RECOMENDAÇÕES:"
echo "================"
echo "1. Rebuild do container para aplicar melhorias:"
echo "   docker compose down && docker compose build --no-cache && docker compose up -d"
echo ""
echo "2. Execute o diagnóstico detalhado:"
echo "   ./tools/diagnose_instance_problems.sh"
echo ""
echo "3. Monitore logs em tempo real:"
echo "   ./tools/monitor_docker_logs.sh"
