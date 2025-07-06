#!/bin/bash
# test_scheduling_debug.sh
# Script para testar e debuggar o agendamento via Streamlit no Docker

echo "🔍 TESTE DE AGENDAMENTO E DEBUGGING"
echo "===================================="

echo ""
echo "📊 1. VERIFICANDO ESTADO ATUAL:"
echo "==============================="

echo "🐳 Container Docker ativo:"
docker ps | grep groups-evo-crewai

echo ""
echo "⏰ Tarefas atualmente agendadas no cron:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "🕐 Horário atual do sistema:"
echo "macOS: $(date)"
echo "Docker: $(docker exec groups-evo-crewai date)"

echo ""
echo "📋 2. TESTANDO EXECUÇÃO MANUAL:"
echo "==============================="

echo "🚀 Executando resumo manualmente..."
docker exec groups-evo-crewai bash -c "
    source /app/.env
    export PYTHONPATH='/app/src'
    python3 /app/src/whatsapp_manager/core/summary.py --task_name 'ResumoGrupo_120363400095683544@g.us'
" > /tmp/manual_test.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Execução manual: SUCESSO"
    echo "📄 Últimas 3 linhas do log:"
    tail -3 /tmp/manual_test.log
else
    echo "❌ Execução manual: FALHA"
    echo "📄 Log completo:"
    cat /tmp/manual_test.log
fi

echo ""
echo "📋 3. SIMULANDO AGENDAMENTO VIA CRON:"
echo "====================================="

# Calcular próximo minuto para teste
current_minute=$(date '+%M')
current_hour=$(date '+%H')
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

echo "⏰ Agendando teste para ${next_hour}:${next_minute}..."

# Criar tarefa temporária de teste
docker exec groups-evo-crewai bash -c "(crontab -l 2>/dev/null ; echo '${next_minute} ${next_hour} * * * /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name ResumoGrupo_120363400095683544@g.us >> /app/data/test_cron_execution.log 2>&1 # TASK_ID:TEST_CRON_EXEC') | crontab -"

echo "📋 Aguardando execução..."
echo "Horário atual: $(date '+%H:%M:%S')"
echo "Execução prevista: ${next_hour}:${next_minute}:00"

# Aguardar até a execução + margem
sleep 70

echo ""
echo "📋 4. VERIFICANDO RESULTADO DO TESTE CRON:"
echo "=========================================="

if docker exec groups-evo-crewai test -f /app/data/test_cron_execution.log; then
    echo "✅ SUCESSO! Teste cron executou:"
    echo "📄 Conteúdo do log:"
    docker exec groups-evo-crewai cat /app/data/test_cron_execution.log
    
    # Verificar se o resumo foi enviado
    echo ""
    echo "📧 Verificando se o resumo foi enviado..."
    if docker exec groups-evo-crewai grep -q "Resumo enviado" /app/data/test_cron_execution.log; then
        echo "✅ Resumo foi enviado com sucesso!"
    else
        echo "⚠️  Resumo não foi enviado ou erro ocorreu"
    fi
    
    # Limpeza
    docker exec groups-evo-crewai rm -f /app/data/test_cron_execution.log
else
    echo "❌ FALHA! Teste cron não executou"
    echo "   Verificando logs do cron..."
    docker exec groups-evo-crewai cat /app/data/cron.log | tail -5
fi

# Limpar tarefa de teste
echo ""
echo "🧹 Limpando tarefa de teste..."
docker exec groups-evo-crewai bash -c "crontab -l 2>/dev/null | grep -v '# TASK_ID:TEST_CRON_EXEC' | crontab -"

echo ""
echo "📋 5. VERIFICANDO DIFERENÇAS ENTRE MANUAL E CRON:"
echo "==============================================="

echo "🔍 Comparando variáveis de ambiente..."

echo "📄 Variáveis no contexto manual:"
docker exec groups-evo-crewai bash -c "source /app/.env && echo 'WHATSAPP_NUMBER=$WHATSAPP_NUMBER' && echo 'EVO_BASE_URL=$EVO_BASE_URL' && echo 'PYTHONPATH=$PYTHONPATH'"

echo ""
echo "📄 Variáveis no contexto do load_env.sh:"
docker exec groups-evo-crewai bash -c "/usr/local/bin/load_env.sh env | grep -E '(WHATSAPP_NUMBER|EVO_BASE_URL|PYTHONPATH)' | head -3"

echo ""
echo "📋 6. ANÁLISE DE LOGS DE EXECUÇÃO:"
echo "================================="

echo "📄 Logs recentes de execução do cron:"
docker exec groups-evo-crewai cat /app/data/cron_execution.log | tail -10

echo ""
echo "📄 Logs de tarefas agendadas:"
if docker exec groups-evo-crewai test -f /app/data/logs/scheduled_tasks.log; then
    docker exec groups-evo-crewai cat /app/data/logs/scheduled_tasks.log | tail -5
else
    echo "❌ Log de tarefas agendadas não encontrado"
fi

echo ""
echo "✅ TESTE DE DEBUGGING CONCLUÍDO!"
echo ""
echo "💡 RESUMO:"
echo "=========="
echo "• Execução manual: $([ -f /tmp/manual_test.log ] && echo 'Testada' || echo 'Falhou')"
echo "• Cron funcionando: $(docker exec groups-evo-crewai pgrep cron >/dev/null && echo 'Sim' || echo 'Não')"
echo "• Supervisor ativo: $(docker exec groups-evo-crewai pgrep supervisord >/dev/null && echo 'Sim' || echo 'Não')"
echo "• Tarefas agendadas: $(docker exec groups-evo-crewai crontab -l 2>/dev/null | wc -l) linha(s)"

# Cleanup
rm -f /tmp/manual_test.log

echo ""
echo "🚀 Para resolver problemas de agendamento via Streamlit:"
echo "1. Verifique se o cron está funcionando (mostrado acima)"
echo "2. Verifique se as variáveis de ambiente estão corretas"
echo "3. Verifique se o load_env.sh está executando corretamente"
echo "4. Verifique se não há diferenças de horário entre sistema e Docker"
