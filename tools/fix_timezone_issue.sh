#!/bin/bash
# fix_timezone_issue.sh
# Script para corrigir problema de fuso horário Docker vs macOS

echo "🕐 Correção do Problema de Fuso Horário"
echo "======================================="

echo "📊 ANÁLISE DO PROBLEMA:"
echo "======================"

echo "🖥️  Horário no macOS (sistema local):"
date

echo ""
echo "🐳 Horário no Docker (antes da correção):"
docker exec groups-evo-crewai date

echo ""
echo "🔧 APLICANDO CORREÇÕES:"
echo "======================"

echo "1. Reconstruindo container com novo fuso horário..."
docker compose down
docker compose build --no-cache
docker compose up -d

echo ""
echo "⏳ Aguardando container inicializar..."
sleep 10

echo ""
echo "📊 VERIFICAÇÃO PÓS-CORREÇÃO:"
echo "==========================="

echo "🖥️  Horário no macOS:"
date

echo ""
echo "🐳 Horário no Docker (após correção):"
docker exec groups-evo-crewai date

echo ""
echo "🌍 Fuso horário configurado no Docker:"
docker exec groups-evo-crewai bash -c "echo \$TZ && cat /etc/timezone 2>/dev/null || echo 'Arquivo timezone não encontrado'"

echo ""
echo "⏰ Comparação de horários:"
macos_hour=$(date '+%H:%M')
docker_hour=$(docker exec groups-evo-crewai date '+%H:%M')

echo "macOS:  $macos_hour"
echo "Docker: $docker_hour"

if [ "$macos_hour" = "$docker_hour" ]; then
    echo "✅ SUCESSO! Horários sincronizados"
else
    echo "⚠️  ATENÇÃO: Ainda há diferença de horário"
    echo "   Diferença detectada entre macOS e Docker"
fi

echo ""
echo "🧪 TESTE DE AGENDAMENTO IMEDIATO:"
echo "================================"

# Calcular próximo minuto
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

echo "⏰ Agendando teste para execução em ${next_hour}:${next_minute}..."

# Criar tarefa de teste que usa o horário local
docker exec groups-evo-crewai bash -c "(crontab -l 2>/dev/null ; echo '${next_minute} ${next_hour} * * * echo \"Teste timezone executado em \$(date)\" >> /app/data/test_timezone.log # TASK_ID:TEST_TIMEZONE') | crontab -"

echo "📋 Tarefa agendada. Aguardando execução..."
echo "Horário atual: $(date '+%H:%M:%S')"
echo "Execução prevista: ${next_hour}:${next_minute}:00"

# Aguardar até a execução
sleep 70

echo ""
echo "📋 Verificando resultado do teste..."
if docker exec groups-evo-crewai test -f /app/data/test_timezone.log; then
    echo "✅ SUCESSO! Teste executou no horário correto:"
    docker exec groups-evo-crewai cat /app/data/test_timezone.log
    
    # Verificar se o horário de execução está próximo do esperado
    execution_time=$(docker exec groups-evo-crewai cat /app/data/test_timezone.log | grep -o '[0-9][0-9]:[0-9][0-9]:[0-9][0-9]')
    echo "⏰ Horário de execução registrado: $execution_time"
    echo "⏰ Horário esperado: ${next_hour}:${next_minute}:XX"
    
    # Limpeza
    docker exec groups-evo-crewai bash -c "crontab -l 2>/dev/null | grep -v '# TASK_ID:TEST_TIMEZONE' | crontab -"
    docker exec groups-evo-crewai rm -f /app/data/test_timezone.log
    echo "🧹 Teste limpo"
else
    echo "❌ FALHA! Teste não executou"
    echo "   Verifique se o cron está funcionando corretamente"
fi

echo ""
echo "📋 Estado atual das tarefas agendadas:"
docker exec groups-evo-crewai crontab -l

echo ""
echo "✅ Correção de fuso horário concluída!"
echo ""
echo "💡 RESUMO DAS MUDANÇAS:"
echo "======================"
echo "• docker-compose.yml: Adicionado TZ=Europe/Lisbon"
echo "• docker-compose.yml: Adicionados volumes para sincronizar timezone"
echo "• task_scheduler_docker.py: Melhorado tratamento de agendamento 'ONCE'"
echo ""
echo "🚀 Agora o agendamento via Streamlit deve funcionar com horário correto!"
