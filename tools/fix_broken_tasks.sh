#!/bin/bash
# fix_broken_tasks.sh
# Script para corrigir tarefas criadas com formato incorreto

echo "🔧 Correção de Tarefas com Formato Incorreto"
echo "==========================================="

echo "📋 Tarefas atuais no cron:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "🔍 Procurando tarefas com formato incorreto (contendo ano)..."

# Listar tarefas que contêm anos (formato incorreto)
broken_tasks=$(docker exec groups-evo-crewai bash -c "crontab -l 2>/dev/null | grep -E '[0-9]{4}' || echo 'none'")

if [ "$broken_tasks" = "none" ]; then
    echo "✅ Nenhuma tarefa com formato incorreto encontrada!"
else
    echo "❌ Tarefas com formato incorreto encontradas:"
    echo "$broken_tasks"
    
    echo ""
    echo "🔧 Corrigindo tarefas..."
    
    # Corrigir tarefa específica encontrada
    if echo "$broken_tasks" | grep -q "23 02 2025 07"; then
        echo "Corrigindo tarefa ResumoGrupo_120363400095683544@g.us..."
        
        # Remover a tarefa incorreta
        docker exec groups-evo-crewai bash -c "crontab -l 2>/dev/null | grep -v '23 02 2025 07' | crontab -"
        
        # Adicionar a tarefa correta (diariamente às 02:23)
        docker exec groups-evo-crewai bash -c "(crontab -l 2>/dev/null ; echo '23 02 * * * /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name ResumoGrupo_120363400095683544@g.us # TASK_ID:ResumoGrupo_120363400095683544@g.us') | crontab -"
        
        echo "✅ Tarefa corrigida para execução diária às 02:23"
    fi
fi

echo ""
echo "📋 Tarefas corrigidas no cron:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "🧪 Testando uma tarefa para execução imediata (próximo minuto)..."

# Criar uma tarefa para testar no próximo minuto
current_minute=$(docker exec groups-evo-crewai date '+%M')
current_hour=$(docker exec groups-evo-crewai date '+%H')

# Calcular próximo minuto
next_minute=$((current_minute + 1))
next_hour=$current_hour

# Se passou de 59 minutos, ajustar hora
if [ $next_minute -eq 60 ]; then
    next_minute=0
    next_hour=$((current_hour + 1))
    if [ $next_hour -eq 24 ]; then
        next_hour=0
    fi
fi

# Garantir formato de 2 dígitos
next_minute=$(printf "%02d" $next_minute)
next_hour=$(printf "%02d" $next_hour)

echo "Agendando teste para ${next_hour}:${next_minute}..."

# Criar tarefa de teste
docker exec groups-evo-crewai bash -c "(crontab -l 2>/dev/null ; echo '${next_minute} ${next_hour} * * * /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name ResumoGrupo_120363400095683544@g.us # TASK_ID:TEST_IMMEDIATE') | crontab -"

echo "⏰ Aguardando 70 segundos para ver se a tarefa executa..."
sleep 70

echo "📋 Verificando logs de execução..."
if docker exec groups-evo-crewai bash -c "tail -5 /app/data/logs/summary_task.log 2>/dev/null | grep -q $(date '+%Y-%m-%d')"; then
    echo "✅ SUCESSO! Tarefa executou corretamente"
    docker exec groups-evo-crewai bash -c "tail -5 /app/data/logs/summary_task.log"
else
    echo "❌ Tarefa não executou. Verificando logs de erro..."
    docker exec groups-evo-crewai bash -c "tail -5 /app/data/cron_execution.log 2>/dev/null || echo 'Log de execução não encontrado'"
fi

# Remover tarefa de teste
echo "🧹 Removendo tarefa de teste..."
docker exec groups-evo-crewai bash -c "crontab -l 2>/dev/null | grep -v '# TASK_ID:TEST_IMMEDIATE' | crontab -"

echo ""
echo "✅ Correção finalizada!"
echo "📋 Estado final do cron:"
docker exec groups-evo-crewai crontab -l
