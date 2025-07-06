#!/bin/bash
# debug_streamlit_scheduling.sh
# Script para debuggar o agendamento via Streamlit

echo "🔍 DEBUG: Agendamento via Streamlit no Docker"
echo "============================================="

# Verificar se container está rodando
if ! docker ps | grep -q groups-evo-crewai; then
    echo "❌ Container não está rodando. Iniciando..."
    docker compose up -d
    sleep 5
fi

echo "📊 STATUS INICIAL DO SISTEMA:"
echo "============================="

echo "⏰ Tarefas agendadas ANTES do teste:"
docker exec groups-evo-crewai crontab -l 2>/dev/null || echo "Nenhuma tarefa agendada"

echo ""
echo "📂 Arquivos de configuração existentes:"
docker exec groups-evo-crewai bash -c "ls -la /app/data/ | grep -E '(csv|json)'"

echo ""
echo "🌐 Streamlit está em: http://localhost:8501"
echo ""
echo "📝 INSTRUÇÕES PARA TESTE:"
echo "========================="
echo "1. Acesse http://localhost:8501"
echo "2. Vá para Portuguese"
echo "3. Selecione um grupo"
echo "4. Configure agendamento (escolha 'Diariamente' e um horário)"
echo "5. Marque 'Habilitar Geração do Resumo'"
echo "6. Clique em 'Salvar Configurações'"
echo "7. Volte aqui e pressione ENTER"
echo ""

read -p "⏳ Pressione ENTER após agendar no Streamlit..."

echo ""
echo "📊 STATUS APÓS AGENDAMENTO:"
echo "=========================="

echo "⏰ Tarefas agendadas DEPOIS do teste:"
docker exec groups-evo-crewai crontab -l 2>/dev/null || echo "Nenhuma tarefa agendada"

echo ""
echo "📂 Arquivo group_summary.csv:"
if docker exec groups-evo-crewai test -f /app/data/group_summary.csv; then
    echo "✅ Arquivo existe"
    docker exec groups-evo-crewai bash -c "tail -5 /app/data/group_summary.csv"
else
    echo "❌ Arquivo NÃO existe"
fi

echo ""
echo "📋 Logs recentes do Streamlit:"
docker exec groups-evo-crewai bash -c "tail -10 /app/data/streamlit.log 2>/dev/null" || echo "Log do Streamlit não encontrado"

echo ""
echo "📋 Logs recentes do summary:"
docker exec groups-evo-crewai bash -c "tail -10 /app/data/logs/summary_task.log 2>/dev/null" || echo "Log do summary não encontrado"

echo ""
echo "🔧 Processos em execução no container:"
docker exec groups-evo-crewai ps aux

echo ""
echo "🔍 Verificando se o cron está funcionando:"
docker exec groups-evo-crewai bash -c "ps aux | grep cron"

echo ""
echo "📄 Logs do cron (se existirem):"
docker exec groups-evo-crewai bash -c "tail -10 /var/log/cron.log 2>/dev/null" || echo "Log do cron não encontrado"

echo ""
echo "🧪 TESTE MANUAL - Vamos simular um agendamento:"
echo "=============================================="

# Criar uma tarefa de teste para o próximo minuto
next_minute=$(date -d "+1 minute" '+%M %H')
test_task_command="echo 'Teste de agendamento executado em $(date)' >> /app/data/test_scheduling.log"

echo "Criando tarefa de teste para o próximo minuto: $next_minute"
docker exec groups-evo-crewai bash -c "(crontab -l 2>/dev/null; echo '$next_minute * * * $test_task_command # TASK_ID:TEST_SCHEDULING') | crontab -"

echo "⏰ Aguardando 70 segundos para ver se a tarefa é executada..."
sleep 70

echo "📋 Verificando se a tarefa de teste executou:"
if docker exec groups-evo-crewai test -f /app/data/test_scheduling.log; then
    echo "✅ SUCESSO! Cron está funcionando:"
    docker exec groups-evo-crewai cat /app/data/test_scheduling.log
    
    # Limpar a tarefa de teste
    docker exec groups-evo-crewai bash -c "crontab -l 2>/dev/null | grep -v '# TASK_ID:TEST_SCHEDULING' | crontab -"
    docker exec groups-evo-crewai rm -f /app/data/test_scheduling.log
    echo "🧹 Tarefa de teste removida"
else
    echo "❌ FALHA! Cron não está executando tarefas"
    echo "   Isso explicaria por que o agendamento via Streamlit não funciona"
fi

echo ""
echo "🔍 DIAGNÓSTICO FINAL:"
echo "===================="

# Verificar se TaskScheduled está funcionando
echo "🐍 Testando TaskScheduled diretamente no Python:"
docker exec groups-evo-crewai python3 -c "
import sys
sys.path.insert(0, '/app/src')
from whatsapp_manager.utils.task_scheduler import TaskScheduled
try:
    print('✅ TaskScheduled importado com sucesso')
    tasks = TaskScheduled.list_project_tasks()
    print(f'📋 Tarefas do projeto encontradas: {len(tasks)}')
    for task in tasks:
        print(f'   - {task}')
except Exception as e:
    print(f'❌ Erro ao usar TaskScheduled: {e}')
"

echo ""
echo "✅ Diagnóstico completo finalizado!"
echo "💡 Se o cron não estiver funcionando, o problema está na infraestrutura do Docker"
echo "💡 Se o cron funcionar mas o Streamlit não criar tarefas, o problema está no código Python"
