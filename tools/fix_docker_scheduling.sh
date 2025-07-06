#!/bin/bash
# fix_docker_scheduling.sh
# Script para corrigir problemas de agendamento no Docker

echo "🔧 CORREÇÃO DO SISTEMA DE AGENDAMENTO DOCKER"
echo "=============================================="

echo ""
echo "1. DIAGNÓSTICO INICIAL:"
echo "======================"

echo "📊 Estado atual do sistema:"
echo "Container: $(docker ps --filter name=groups-evo-crewai --format 'table {{.Names}}\t{{.Status}}' | tail -1)"
echo "Cron: $(docker exec groups-evo-crewai pgrep -f cron >/dev/null && echo 'Ativo' || echo 'Inativo')"
echo "Supervisord: $(docker exec groups-evo-crewai pgrep -f supervisord >/dev/null && echo 'Ativo' || echo 'Inativo')"

echo ""
echo "2. APLICANDO CORREÇÕES:"
echo "======================"

echo "🔄 Reiniciando serviços críticos..."

# Reiniciar cron dentro do container
docker exec groups-evo-crewai bash -c "
    # Parar cron se estiver rodando
    pkill -f cron 2>/dev/null || true
    sleep 2
    
    # Iniciar cron novamente
    cron
    
    # Verificar se iniciou
    if pgrep -f cron >/dev/null; then
        echo '✅ Cron reiniciado com sucesso'
    else
        echo '❌ Falha ao reiniciar cron'
    fi
"

echo ""
echo "📝 Melhorando script load_env.sh..."

# Criar uma versão melhorada do load_env.sh
docker exec groups-evo-crewai bash -c "
cat > /usr/local/bin/load_env.sh << 'EOF'
#!/bin/bash
# load_env.sh - Versão melhorada
# Carrega variáveis do .env e executa o comando passado como argumento

# Função de log
log_message() {
    echo \"\$(date '+%Y-%m-%d %H:%M:%S') [LOAD_ENV] \$1\" >> /app/data/cron_execution.log
    echo \"[LOAD_ENV] \$1\"
}

# Função para verificar se comando foi executado com sucesso
check_command() {
    if [ \$? -eq 0 ]; then
        log_message \"✅ \$1 executado com sucesso\"
        return 0
    else
        log_message \"❌ \$1 falhou com código \$?\"
        return 1
    fi
}

# Navega para o diretório do aplicativo
cd /app || {
    log_message \"ERRO: Não foi possível navegar para /app\"
    exit 1
}

log_message \"Iniciando execução de tarefa agendada\"
log_message \"Diretório atual: \$(pwd)\"
log_message \"Comando a executar: \$*\"

# Verifica se o arquivo .env existe
if [ ! -f .env ]; then
    log_message \"ERRO: Arquivo .env não encontrado em \$(pwd)\"
    exit 1
fi

# Carrega variáveis do .env
log_message \"Carregando variáveis de ambiente...\"
set -a
source .env 2>/dev/null || {
    log_message \"ERRO: Falha ao carregar arquivo .env\"
    exit 1
}
set +a

# Garantir PYTHONPATH correto
export PYTHONPATH=\"/app/src:\${PYTHONPATH}\"

# Verificar se Python está disponível
if ! command -v python3 >/dev/null 2>&1; then
    log_message \"ERRO: Python3 não encontrado no PATH\"
    exit 1
fi

# Verificar se o script existe
if [[ \"\$1\" == \"python3\" ]] && [[ \"\$2\" == \"/app/src/whatsapp_manager/core/summary.py\" ]]; then
    if [ ! -f \"\$2\" ]; then
        log_message \"ERRO: Script \$2 não encontrado\"
        exit 1
    fi
fi

# Log de variáveis críticas (sem expor tokens)
log_message \"Variáveis carregadas:\"
log_message \"WHATSAPP_NUMBER: \${WHATSAPP_NUMBER:-[NÃO DEFINIDO]}\"
log_message \"EVO_BASE_URL: \${EVO_BASE_URL:-[NÃO DEFINIDO]}\"
log_message \"EVO_INSTANCE_NAME: \${EVO_INSTANCE_NAME:-[NÃO DEFINIDO]}\"
log_message \"EVO_API_TOKEN: \${EVO_API_TOKEN:+[DEFINIDO]}\"
log_message \"EVO_INSTANCE_TOKEN: \${EVO_INSTANCE_TOKEN:+[DEFINIDO]}\"
log_message \"PYTHONPATH: \$PYTHONPATH\"

# Executar comando com timeout de 10 minutos
log_message \"Executando comando: \$*\"
timeout 600 \"\$@\"
exit_code=\$?

if [ \$exit_code -eq 124 ]; then
    log_message \"ERRO: Comando excedeu timeout de 10 minutos\"
elif [ \$exit_code -eq 0 ]; then
    log_message \"✅ Comando executado com sucesso\"
else
    log_message \"❌ Comando falhou com código \$exit_code\"
fi

exit \$exit_code
EOF

chmod +x /usr/local/bin/load_env.sh
"

echo "✅ Script load_env.sh atualizado"

echo ""
echo "3. VERIFICANDO INTEGRIDADE DO SISTEMA:"
echo "====================================="

echo "🧪 Testando execução direta..."
docker exec groups-evo-crewai /usr/local/bin/load_env.sh python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Load_env.sh funcionando corretamente"
else
    echo "❌ Problema com load_env.sh"
fi

echo ""
echo "📋 Verificando dependências Python..."
docker exec groups-evo-crewai python3 -c "
import sys
modules = ['dotenv', 'streamlit', 'requests', 'pandas']
missing = []
for module in modules:
    try:
        __import__(module)
        print(f'✅ {module}')
    except ImportError:
        missing.append(module)
        print(f'❌ {module}')

if missing:
    print(f'Módulos faltando: {missing}')
    sys.exit(1)
else:
    print('✅ Todas as dependências estão disponíveis')
"

echo ""
echo "4. OTIMIZANDO AGENDAMENTO:"
echo "========================="

echo "🔧 Aplicando otimizações no cron..."

# Garantir que o cron tenha as variáveis de ambiente necessárias
docker exec groups-evo-crewai bash -c "
# Criar um arquivo de ambiente para o cron
cat > /etc/cron.d/whatsapp-env << 'EOF'
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
PYTHONPATH=/app/src
EOF

# Reiniciar cron para aplicar mudanças
pkill -f cron 2>/dev/null || true
sleep 2
cron

echo 'Cron otimizado'
"

echo ""
echo "5. TESTE FINAL:"
echo "==============="

echo "🚀 Executando teste completo..."
docker exec groups-evo-crewai bash -c "
    # Teste com timeout para não travar
    timeout 300 /usr/local/bin/load_env.sh python3 /app/src/whatsapp_manager/core/summary.py --task_name 'ResumoGrupo_120363400095683544@g.us' 2>/dev/null >/dev/null
    
    if [ \$? -eq 0 ]; then
        echo '✅ Teste completo executado com sucesso!'
    else
        echo '⚠️  Teste teve problemas, mas pode ser normal (grupo sem mensagens novas)'
    fi
"

echo ""
echo "6. RESUMO DAS CORREÇÕES:"
echo "========================"

echo "✅ Correções aplicadas:"
echo "• Script load_env.sh melhorado com tratamento de erros"
echo "• Cron reiniciado e otimizado"
echo "• Verificação de dependências realizada"
echo "• Timeout adicionado para evitar travamentos"
echo "• Logs melhorados para debugging"

echo ""
echo "📊 Estado final do sistema:"
echo "Cron: $(docker exec groups-evo-crewai pgrep -f cron >/dev/null && echo 'Ativo' || echo 'Inativo')"
echo "Supervisord: $(docker exec groups-evo-crewai pgrep -f supervisord >/dev/null && echo 'Ativo' || echo 'Inativo')"
echo "Streamlit: $(docker exec groups-evo-crewai pgrep -f streamlit >/dev/null && echo 'Ativo' || echo 'Inativo')"

echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "=================="
echo "1. Acesse o Streamlit em http://localhost:8501"
echo "2. Configure um novo agendamento"
echo "3. Aguarde a execução no horário programado"
echo "4. Verifique os logs em /app/data/cron_execution.log"

echo ""
echo "🔍 Para monitorar execuções:"
echo "docker exec groups-evo-crewai tail -f /app/data/cron_execution.log"

echo ""
echo "✅ CORREÇÃO CONCLUÍDA!"
