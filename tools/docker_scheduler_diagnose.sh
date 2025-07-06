#!/bin/bash
# docker_scheduler_diagnose.sh
# Script para diagnosticar e corrigir problemas de agendamento no Docker

# Cores para saída
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== DIAGNÓSTICO DE AGENDAMENTO NO DOCKER ===${NC}"
echo "Data: $(date)"

# Determinar o container ID
CONTAINER_ID=$(docker ps -f name=groups-evo-crewai --format "{{.ID}}")
if [ -z "$CONTAINER_ID" ]; then
    echo -e "${RED}Erro: Container 'groups-evo-crewai' não encontrado. O Docker está rodando?${NC}"
    exit 1
else
    echo -e "${GREEN}Container encontrado: $CONTAINER_ID${NC}"
fi

echo -e "\n${BLUE}=== VERIFICANDO SERVIÇO CRON ===${NC}"
docker exec $CONTAINER_ID service cron status
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Cron não está rodando. Tentando reiniciar...${NC}"
    docker exec $CONTAINER_ID service cron start
    docker exec $CONTAINER_ID service cron status
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERRO: Não foi possível iniciar o cron no container.${NC}"
    else
        echo -e "${GREEN}Cron reiniciado com sucesso.${NC}"
    fi
else
    echo -e "${GREEN}Cron está rodando corretamente.${NC}"
fi

echo -e "\n${BLUE}=== VERIFICANDO DIRETÓRIOS E PERMISSÕES ===${NC}"
docker exec $CONTAINER_ID ls -la /app/data
docker exec $CONTAINER_ID ls -la /etc/cron.d/
docker exec $CONTAINER_ID ls -la /var/spool/cron/crontabs/

echo -e "\n${BLUE}=== VERIFICANDO TAREFAS AGENDADAS ===${NC}"
echo "Tarefas no crontab:"
docker exec $CONTAINER_ID crontab -l

echo -e "\nTarefas em /etc/cron.d/:"
docker exec $CONTAINER_ID find /etc/cron.d/ -type f -name 'task_*' -exec cat {} \;

echo -e "\n${BLUE}=== VERIFICANDO LOGS ===${NC}"
echo "Log do cron:"
docker exec $CONTAINER_ID cat /app/data/cron.log | tail -n 20

echo -e "\nLog de erros do cron:"
docker exec $CONTAINER_ID cat /app/data/cron_error.log | tail -n 20

echo -e "\nLog de execução:"
docker exec $CONTAINER_ID cat /app/data/cron_execution.log | tail -n 20

echo -e "\n${BLUE}=== VERIFICANDO TAREFAS DO SUPERVISOR ===${NC}"
docker exec $CONTAINER_ID supervisorctl status

echo -e "\n${BLUE}=== CORRIGINDO PROBLEMAS COMUNS ===${NC}"
echo "1. Verificando o load_env.sh..."
docker exec $CONTAINER_ID test -x /usr/local/bin/load_env.sh
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Corrigindo permissões do load_env.sh...${NC}"
    docker exec $CONTAINER_ID chmod +x /usr/local/bin/load_env.sh
    echo -e "${GREEN}Permissões corrigidas.${NC}"
else
    echo -e "${GREEN}load_env.sh tem permissões corretas.${NC}"
fi

echo "2. Corrigindo permissões em /app/data..."
docker exec $CONTAINER_ID chmod -R 777 /app/data
echo -e "${GREEN}Permissões de /app/data corrigidas.${NC}"

echo "3. Verificando se Docker é detectado corretamente..."
docker exec $CONTAINER_ID python3 -c "import os; print('DOCKER_ENV:', os.environ.get('DOCKER_ENV')); print('/.dockerenv exists:', os.path.exists('/.dockerenv'))"

echo -e "\n${BLUE}=== REINICIANDO SERVIÇOS ===${NC}"
echo "Reiniciando cron..."
docker exec $CONTAINER_ID service cron restart

echo "Reiniciando supervisord..."
docker exec $CONTAINER_ID supervisorctl reload

echo -e "\n${BLUE}=== VERIFICAÇÃO FINAL ===${NC}"
docker exec $CONTAINER_ID service cron status
docker exec $CONTAINER_ID supervisorctl status

echo -e "\n${GREEN}Diagnóstico concluído! Verifique se há erros acima.${NC}"
echo -e "${YELLOW}Se problemas persistirem, execute: docker-compose down && docker-compose up -d${NC}"
