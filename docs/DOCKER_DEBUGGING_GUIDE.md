# 🔍 Guia de Debugging - Docker

Este guia ajuda a diagnosticar e resolver problemas com o agendamento de tarefas no ambiente Docker.

## 🚀 Scripts de Diagnóstico

### 1. Diagnóstico Rápido
```bash
./tools/quick_diagnosis.sh
```
**O que faz:**
- Verifica se o container está rodando
- Testa conectividade da API
- Verifica configurações essenciais
- Mostra status geral do sistema

### 2. Monitor de Logs em Tempo Real
```bash
./tools/monitor_docker_logs.sh
```
**O que faz:**
- Monitora logs do container
- Verifica tarefas agendadas (crontab)
- Mostra logs internos do sistema
- Testa conectividade da API

### 3. Teste Manual de Execução
```bash
./tools/test_manual_execution.sh
```
**O que faz:**
- Lista grupos disponíveis
- Executa tarefas manualmente
- Mostra logs detalhados de execução
- Diagnostica problemas de importação

## 📋 Logs Importantes

### Logs do Sistema
- `/app/data/logs/whatsapp_manager.log` - Log principal do sistema
- `/app/data/logs/scheduled_tasks.log` - Log específico de tarefas agendadas
- `/app/data/cron_execution.log` - Log de execução do cron
- `/app/data/log_summary.txt` - Log tradicional de resumos

### Logs do Docker/Supervisor
- `/app/data/supervisord.log` - Log do supervisord
- `/app/data/cron.log` - Log do serviço cron
- `/app/data/streamlit.log` - Log do Streamlit

## 🔧 Comandos Úteis

### Verificar Container
```bash
# Status do container
docker ps | grep groups-evo-crewai

# Logs do container
docker logs -f groups-evo-crewai

# Acessar shell do container
docker exec -it groups-evo-crewai bash
```

### Verificar Agendamentos
```bash
# Ver tarefas agendadas
docker exec groups-evo-crewai crontab -l

# Ver logs do cron
docker exec groups-evo-crewai tail -f /var/log/cron.log
```

### Verificar Ambiente
```bash
# Variáveis de ambiente
docker exec groups-evo-crewai env | grep -E "(WHATSAPP|EVO_)"

# Estrutura de arquivos
docker exec groups-evo-crewai ls -la /app/data/
```

## 🐛 Problemas Comuns

### 1. Tarefas Não Executam
**Sintomas:** Agendamento criado mas tarefa não roda no horário
**Diagnóstico:**
```bash
# Verificar se cron está rodando
docker exec groups-evo-crewai ps aux | grep cron

# Verificar logs de execução
docker exec groups-evo-crewai tail -f /app/data/cron_execution.log
```

**Soluções:**
- Verificar se o arquivo `.env` existe e está correto
- Confirmar que as variáveis de ambiente estão carregadas
- Testar execução manual da tarefa

### 2. Erro de Importação Python
**Sintomas:** Erro "ModuleNotFoundError" nos logs
**Diagnóstico:**
```bash
# Testar importações
docker exec groups-evo-crewai python3 -c "
import sys
sys.path.insert(0, '/app/src')
from whatsapp_manager.core.summary import *
"
```

**Soluções:**
- Verificar PYTHONPATH no load_env.sh
- Confirmar estrutura de diretórios
- Rebuild do container se necessário

### 3. API Não Acessível
**Sintomas:** Erro de conectividade com Evolution API
**Diagnóstico:**
```bash
# Testar conectividade
./tools/quick_diagnosis.sh
```

**Soluções:**
- Verificar configurações de rede no docker-compose.yml
- Confirmar tokens da API
- Testar acesso manual à API

### 4. Permissões de Arquivo
**Sintomas:** Erro "Permission denied" nos logs
**Diagnóstico:**
```bash
# Verificar permissões
docker exec groups-evo-crewai ls -la /app/data/
```

**Soluções:**
```bash
# Corrigir permissões
docker exec groups-evo-crewai chmod 755 /app/data
docker exec groups-evo-crewai chmod 644 /app/data/*.csv
```

## 📊 Monitoramento Contínuo

### Dashboard de Status
```bash
# Status geral
./tools/quick_diagnosis.sh

# Logs em tempo real
./tools/monitor_docker_logs.sh
```

### Verificação Periódica
```bash
# Adicionar ao crontab do host (opcional)
# */5 * * * * /path/to/project/tools/quick_diagnosis.sh >> /var/log/whatsapp_diagnosis.log
```

## 🔄 Rebuild do Container

Se os problemas persistirem, faça um rebuild completo:

```bash
# Parar container
docker-compose down

# Rebuild sem cache
docker-compose build --no-cache

# Reiniciar
docker-compose up -d

# Verificar logs
docker logs -f groups-evo-crewai
```

## 📞 Teste de Conectividade Completo

```bash
# 1. Verificar container
docker ps | grep groups-evo-crewai

# 2. Verificar Streamlit
curl -s http://localhost:8501 > /dev/null && echo "Streamlit OK" || echo "Streamlit FAIL"

# 3. Verificar API Evolution
./tools/quick_diagnosis.sh

# 4. Testar tarefa manual
./tools/test_manual_execution.sh

# 5. Monitorar logs
./tools/monitor_docker_logs.sh
```

## 📝 Relatório de Bug

Se ainda houver problemas, colete estas informações:

```bash
# Informações do sistema
./tools/quick_diagnosis.sh > debug_report.txt

# Logs completos
docker logs groups-evo-crewai >> debug_report.txt

# Configuração atual
docker exec groups-evo-crewai env | grep -E "(WHATSAPP|EVO_)" >> debug_report.txt

# Estrutura de arquivos
docker exec groups-evo-crewai find /app -name "*.log" -ls >> debug_report.txt
```
