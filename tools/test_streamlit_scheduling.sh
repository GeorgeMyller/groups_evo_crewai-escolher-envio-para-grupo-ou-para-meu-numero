#!/bin/bash
set -euo pipefail
# test_streamlit_scheduling.sh
# Script para testar agendamento via Streamlit e monitorar logs

echo "🧪 Teste de Agendamento via Streamlit"
echo "===================================="

# Função para monitorar logs
monitor_logs() {
    echo "📋 Monitorando logs em tempo real..."
    echo "Pressione Ctrl+C para parar"
    
    # Monitor múltiplos logs simultaneamente
    docker exec groups-evo-crewai bash -c "
        echo '=== CRON LOGS ==='
        tail -f /var/log/cron.log &
        echo '=== SUMMARY LOGS ==='
        tail -f /app/data/logs/summary_task.log &
        echo '=== SCHEDULED TASKS LOGS ==='
        tail -f /app/data/logs/scheduled_tasks.log &
        echo '=== TASK MONITOR LOGS ==='
        tail -f /app/data/logs/task_monitor.log &
        wait
    "
}

# Verificar se container está rodando
if ! docker ps | grep -q groups-evo-crewai; then
    echo "❌ Container não está rodando. Iniciando..."
    docker compose up -d
    sleep 5
fi

echo "📊 Status atual do sistema:"
echo "=========================="

# Verificar crontab antes
echo "⏰ Tarefas agendadas ANTES do teste:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "🌐 Streamlit disponível em: http://localhost:8501"
echo ""
echo "📝 INSTRUÇÕES:"
echo "1. Acesse o Streamlit no navegador"
echo "2. Vá para a seção de agendamento"
echo "3. Agende uma nova tarefa"
echo "4. Volte aqui e pressione ENTER para verificar mudanças"
echo ""
read -p "Pressione ENTER após agendar uma tarefa no Streamlit..."

echo ""
echo "⏰ Tarefas agendadas DEPOIS do teste:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "📋 Últimas linhas dos logs principais:"
echo "===================================="

echo "--- CRON LOG ---"
docker exec groups-evo-crewai bash -c "tail -5 /var/log/cron.log 2>/dev/null || echo 'Log não encontrado'"

echo ""
echo "--- SUMMARY LOG ---"
docker exec groups-evo-crewai bash -c "tail -5 /app/data/logs/summary_task.log 2>/dev/null || echo 'Log não encontrado'"

echo ""
echo "--- SCHEDULED TASKS LOG ---"
docker exec groups-evo-crewai bash -c "tail -5 /app/data/logs/scheduled_tasks.log 2>/dev/null || echo 'Log não encontrado'"

echo ""
echo "🔄 Quer monitorar logs em tempo real? (y/n)"
read -p "Resposta: " monitor
if [[ $monitor =~ ^[Yy]$ ]]; then
    monitor_logs
fi

echo ""
echo "✅ Teste concluído!"
