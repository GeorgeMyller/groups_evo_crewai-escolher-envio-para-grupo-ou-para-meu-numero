#!/bin/bash
# load_env.sh
# Carrega variáveis do .env e executa o comando passado como argumento
# Enhanced version with logging and error handling

# Log function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') [LOAD_ENV] $1" >> /app/data/cron_execution.log
    echo "[LOAD_ENV] $1"
}

# Navega para o diretório do aplicativo onde .env está localizado
cd /app || {
    log_message "ERRO: Não foi possível navegar para /app"
    exit 1
}

log_message "Iniciando execução de tarefa agendada"
log_message "Diretório atual: $(pwd)"
log_message "Comando a executar: $*"

# Verifica se o arquivo .env existe
if [ ! -f .env ]; then
    log_message "ERRO: Arquivo .env não encontrado em $(pwd)"
    exit 1
fi

# Carrega e exibe variáveis críticas (sem expor tokens)
log_message "Carregando variáveis de ambiente..."

# Exporta as variáveis do .env para o ambiente atual
set -a  # automatically export all variables
source .env 2>/dev/null
set +a

# Garantir PYTHONPATH correto
export PYTHONPATH="/app/src:${PYTHONPATH}"

# Log de variáveis críticas (mascarando tokens)
log_message "WHATSAPP_NUMBER: ${WHATSAPP_NUMBER:-[NÃO DEFINIDO]}"
log_message "EVO_BASE_URL: ${EVO_BASE_URL:-[NÃO DEFINIDO]}"
log_message "EVO_INSTANCE_NAME: ${EVO_INSTANCE_NAME:-[NÃO DEFINIDO]}"
log_message "EVO_API_TOKEN: ${EVO_API_TOKEN:+[DEFINIDO]}"
log_message "EVO_INSTANCE_TOKEN: ${EVO_INSTANCE_TOKEN:+[DEFINIDO]}"
log_message "PYTHONPATH: $PYTHONPATH"

# Executa o comando original passado para este script
log_message "Executando comando: $*"

# Executa o comando e captura o código de saída
exec "$@"
exit_code=$?

log_message "Comando finalizado com código de saída: $exit_code"

exit $exit_code
