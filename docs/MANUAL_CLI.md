# Manual de Uso via CLI

Este manual descreve os principais comandos de linha de comando (CLI) disponíveis no sistema para gerenciamento de grupos, agendamento de tarefas e geração/envio de resumos de mensagens de WhatsApp.

---

## 1. Gerar Resumo de Grupo Manualmente

Execute o script `summary.py` para gerar e enviar o resumo de um grupo específico:

```sh
python3 summary.py --task_name ResumoGrupo_<ID_DO_GRUPO>
```
- Substitua `<ID_DO_GRUPO>` pelo ID do grupo desejado.
- O script coleta as mensagens das últimas 24h, gera o resumo com IA e envia para o grupo e/ou número pessoal, conforme configuração.

---

## 2. Listar Grupos com Resumos Agendados

Para listar todos os grupos que possuem tarefas de resumo agendadas:

```sh
python3 list_scheduled_tasks.py
```
- Exibe nome, ID, horário e configurações de cada grupo com resumo agendado.
- Mostra também as tarefas agendadas no sistema operacional.

---

## 3. Remover Agendamento de Grupo

Para remover o agendamento de resumo de um grupo:

```sh
python3 delete_scheduled_tasks.py
```
- O sistema exibirá os grupos agendados e solicitará que você escolha qual deseja remover.
- Confirme a remoção quando solicitado.

---

## 4. Exportar Dados dos Grupos para CSV

Para exportar informações detalhadas dos grupos para um arquivo CSV:

```sh
python3 save_groups_to_csv.py
```
- Gera/atualiza o arquivo `group_info.csv` com os dados dos grupos.

---

## 5. Sumarização Leve (sem CrewAI)

Para gerar um resumo simples, sem IA avançada:

```sh
python3 summary_lite.py
```
- O script pode ser adaptado para receber mensagens e gerar um resumo leve.

---

## 6. Agendamento de Tarefas (Avançado)

O sistema permite agendar tarefas de resumo automaticamente via SO (Windows, Linux, macOS). Para criar, remover ou listar tarefas programaticamente, utilize as funções da classe `TaskScheduled` em `task_scheduler.py`.

Exemplo de uso programático:
```python
from task_scheduler import TaskScheduled
TaskScheduled.create_task('ResumoGrupo_<ID>', '/caminho/para/summary.py', schedule_type='DAILY', time='22:00')
TaskScheduled.delete_task('ResumoGrupo_<ID>')
TaskScheduled.list_tasks()
```

---

## 7. Executar via Docker (Interface Web)

Consulte o `README.md` para instruções detalhadas de execução via Docker/Docker Compose para uso da interface web.

---

## Observações
- Certifique-se de configurar o arquivo `.env` com as variáveis obrigatórias antes de executar os scripts.
- Todos os comandos devem ser executados no diretório raiz do projeto.
- Para mais detalhes sobre cada script, consulte os docstrings e comentários nos próprios arquivos Python.

---

**Atualizado em: 04/05/2025**
