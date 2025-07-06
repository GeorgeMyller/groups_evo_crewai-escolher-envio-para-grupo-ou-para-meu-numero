#!/bin/bash
# monitor_cron_executions.sh
# Script para monitorar execuções do cron em tempo real

echo "🔍 MONITOR DE EXECUÇÕES DO CRON"
echo "==============================="

echo ""
echo "📊 Status atual:"
echo "Container: $(docker ps --filter name=groups-evo-crewai --format '{{.Status}}' | head -1)"
echo "Horário Docker: $(docker exec groups-evo-crewai date '+%Y-%m-%d %H:%M:%S')"
echo "Horário macOS:  $(date '+%Y-%m-%d %H:%M:%S')"

echo ""
echo "⏰ Tarefas agendadas:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "📋 Próximas execuções previstas:"
current_hour=$(docker exec groups-evo-crewai date '+%H')
current_minute=$(docker exec groups-evo-crewai date '+%M')

# Mostrar próximas execuções
docker exec groups-evo-crewai crontab -l | grep -v '#' | while read line; do
    if [ ! -z "$line" ]; then
        minute=$(echo $line | awk '{print $1}')
        hour=$(echo $line | awk '{print $2}')
        echo "• ${hour}:${minute} - $(echo $line | grep -o 'ResumoGrupo_[^#]*')"
    fi
done

echo ""
echo "🔄 Aguardando próximas execuções..."
echo "Pressione Ctrl+C para parar o monitoramento"
echo ""

# Monitorar logs em tempo real
echo "📋 Logs de execução (tempo real):"
echo "================================"

# Criar arquivo de marca para identificar execuções novas
marker="MONITOR_START_$(date +%s)"
docker exec groups-evo-crewai bash -c "echo '$marker' >> /app/data/cron_execution.log"

# Monitorar novas linhas no log
docker exec groups-evo-crewai tail -f /app/data/cron_execution.log | while read line; do
    if [[ "$line" == *"$marker"* ]]; then
        echo "🟢 Monitoramento iniciado"
        continue
    fi
    
    timestamp=$(echo "$line" | grep -o '^[0-9-]* [0-9:]*')
    if [ ! -z "$timestamp" ]; then
        echo "⏰ $timestamp: $line"
    else
        echo "$line"
    fi
done
