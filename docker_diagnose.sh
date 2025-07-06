#!/bin/bash
# docker_diagnose.sh
# Script para diagnosticar problemas no ambiente Docker

echo "=== DIAGNÓSTICO DO AMBIENTE DOCKER ==="
date

echo -e "\n=== INFORMAÇÕES DO SISTEMA ==="
uname -a
cat /etc/os-release

echo -e "\n=== VARIÁVEIS DE AMBIENTE ==="
env | sort

echo -e "\n=== VERIFICANDO ARQUIVOS IMPORTANTES ==="
echo "group_summary.csv:"
ls -la /app/data/group_summary.csv 2>/dev/null || echo "Arquivo não encontrado"
cat /app/data/group_summary.csv 2>/dev/null || echo "(Arquivo vazio ou inacessível)"

echo -e "\n=== VERIFICANDO PERMISSÕES ==="
ls -la /app/data/
ls -la /app/src/

echo -e "\n=== VERIFICANDO SERVIÇOS ==="
echo "Status do Cron:"
service cron status || echo "Cron não está ativo"
echo "Tarefas do Cron:"
crontab -l || echo "Sem tarefas agendadas"

echo -e "\n=== VERIFICANDO PROCESSOS ==="
ps aux | grep -E 'streamlit|cron|python'

echo -e "\n=== VERIFICANDO LOGS ==="
echo "Últimas 10 linhas de cron.log:"
tail -n 10 /app/data/cron.log 2>/dev/null || echo "Log não encontrado"
echo "Últimas 10 linhas de streamlit.log:"
tail -n 10 /app/data/streamlit.log 2>/dev/null || echo "Log não encontrado"
echo "Últimas 10 linhas de cron_execution.log:"
tail -n 10 /app/data/cron_execution.log 2>/dev/null || echo "Log não encontrado"

echo -e "\n=== TESTE DE DETECÇÃO DOCKER ==="
python3 -c "
import os
import sys
sys.path.insert(0, '/app/src')
from whatsapp_manager.utils.task_scheduler import is_running_in_docker
print(f'Detecção de Docker: {is_running_in_docker()}')
"

echo -e "\n=== TESTE DE ACESSO AO ARQUIVO CSV ==="
python3 -c "
import os
import pandas as pd
csv_path = '/app/data/group_summary.csv'
print(f'Arquivo existe: {os.path.exists(csv_path)}')
try:
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f'Leitura bem-sucedida, linhas: {len(df)}')
        if not df.empty:
            print(f'Colunas: {list(df.columns)}')
    else:
        print('Arquivo não existe, tentando criar')
        df = pd.DataFrame({'group_id': [], 'enabled': [], 'horario': [], 'is_links': [], 'is_names': []})
        df.to_csv(csv_path, index=False)
        print(f'Arquivo criado em {csv_path}')
except Exception as e:
    print(f'Erro ao acessar arquivo: {str(e)}')
"

echo -e "\n=== DIAGNÓSTICO CONCLUÍDO ==="
