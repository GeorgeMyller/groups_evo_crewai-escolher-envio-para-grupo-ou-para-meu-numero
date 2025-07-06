#!/bin/bash
# final_diagnosis.sh
# Diagnóstico final do problema de agendamento

echo "🔍 DIAGNÓSTICO FINAL DO SISTEMA DE AGENDAMENTO"
echo "==============================================="

echo ""
echo "1. VERIFICANDO EXECUÇÕES AUTOMÁTICAS RECENTES:"
echo "=============================================="

echo "📄 Últimas execuções registradas no log tradicional:"
docker exec groups-evo-crewai cat /app/data/log_summary.txt | tail -3

echo ""
echo "📄 Últimas execuções registradas no log de monitoramento:"
docker exec groups-evo-crewai cat /app/data/logs/scheduled_tasks.log | tail -3

echo ""
echo "2. VERIFICANDO ESTADO DO AGENDAMENTO:"
echo "==================================="

echo "⏰ Tarefas agendadas atualmente:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "🕐 Horário atual (Docker vs macOS):"
echo "Docker: $(docker exec groups-evo-crewai date)"
echo "macOS:  $(date)"

echo ""
echo "3. TESTANDO FUNÇÃO DE AGENDAMENTO VIA STREAMLIT:"
echo "==============================================="

echo "📋 Simulando agendamento de nova tarefa..."

# Vamos simular o que acontece quando o Streamlit agenda uma tarefa
# Testando com um horário para alguns minutos à frente
current_minute=$(date '+%M')
current_hour=$(date '+%H')
test_minute=$((current_minute + 2))
test_hour=$current_hour

# Ajustar se necessário
if [ $test_minute -ge 60 ]; then
    test_minute=$((test_minute - 60))
    test_hour=$((current_hour + 1))
    if [ $test_hour -ge 24 ]; then
        test_hour=0
    fi
fi

test_minute=$(printf "%02d" $test_minute)
test_hour=$(printf "%02d" $test_hour)

echo "🕐 Agendando tarefa teste para ${test_hour}:${test_minute}..."

# Criar uma nova tarefa de teste
test_task_name="ResumoGrupo_TEST_$(date +%s)"
docker exec groups-evo-crewai bash -c "(crontab -l 2>/dev/null ; echo '${test_minute} ${test_hour} * * * /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name ${test_task_name} >> /app/data/test_streamlit_scheduling.log 2>&1 # TASK_ID:${test_task_name}') | crontab -"

echo "✅ Tarefa agendada. Aguardando execução..."
echo "Tempo atual: $(date '+%H:%M:%S')"
echo "Execução prevista: ${test_hour}:${test_minute}:00"

# Aguardar execução
sleep 130

echo ""
echo "📋 Verificando resultado..."
if docker exec groups-evo-crewai test -f /app/data/test_streamlit_scheduling.log; then
    echo "✅ Teste executou! Resultado:"
    docker exec groups-evo-crewai cat /app/data/test_streamlit_scheduling.log
    
    # Verificar se foi bem-sucedido
    if docker exec groups-evo-crewai grep -q "Resumo gerado e enviado com sucesso" /app/data/test_streamlit_scheduling.log; then
        echo "✅ SUCESSO: Agendamento via Streamlit funcionou!"
    else
        echo "⚠️  PROBLEMA: Agendamento executou mas teve erro"
    fi
    
    # Cleanup
    docker exec groups-evo-crewai rm -f /app/data/test_streamlit_scheduling.log
else
    echo "❌ FALHA: Teste não executou"
fi

# Remover tarefa de teste
docker exec groups-evo-crewai bash -c "crontab -l 2>/dev/null | grep -v '# TASK_ID:${test_task_name}' | crontab -"

echo ""
echo "4. RESUMO DO DIAGNÓSTICO:"
echo "========================="

echo "📊 Status dos componentes:"
echo "• Container Docker: $(docker ps -q --filter name=groups-evo-crewai | wc -l | tr -d ' ') (deve ser 1)"
echo "• Cron ativo: $(docker exec groups-evo-crewai pgrep -f cron | wc -l | tr -d ' ') processos"
echo "• Supervisord ativo: $(docker exec groups-evo-crewai pgrep -f supervisord | wc -l | tr -d ' ') processos"
echo "• Streamlit ativo: $(docker exec groups-evo-crewai pgrep -f streamlit | wc -l | tr -d ' ') processos"

echo ""
echo "📅 Análise de execuções:"
executions_today=$(docker exec groups-evo-crewai grep "$(date '+%Y-%m-%d')" /app/data/log_summary.txt 2>/dev/null | wc -l | tr -d ' ')
echo "• Execuções hoje: $executions_today"

echo ""
echo "🔧 Recomendações:"
if [ "$executions_today" -gt 0 ]; then
    echo "✅ O sistema está funcionando! Execuções automáticas estão acontecendo."
    echo "💡 Se você não está recebendo resumos, verifique:"
    echo "   1. Se o horário agendado está correto"
    echo "   2. Se o grupo tem mensagens suficientes"
    echo "   3. Se as configurações do grupo estão habilitadas"
else
    echo "⚠️  Poucas execuções detectadas. Possíveis problemas:"
    echo "   1. Horário de agendamento pode estar incorreto"
    echo "   2. Cron pode não estar funcionando corretamente"
    echo "   3. Variáveis de ambiente podem estar incorretas"
fi

echo ""
echo "🏁 DIAGNÓSTICO CONCLUÍDO"
