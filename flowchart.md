```mermaid
flowchart TD
    A[Início: Tarefa Agendada] --> B[Carrega variáveis de ambiente (.env)]
    B --> C[Recebe argumento --task_name (ex: ResumoGrupo_12345)]
    C --> D[Extrai group_id do task_name]
    D --> E[Carrega dados do grupo (group_controller.py)]
    E --> F{Grupo existe e resumo está habilitado?}
    F -- Não --> Z[Fim: Grupo não encontrado ou resumo desabilitado]
    F -- Sim --> G[Calcula intervalo de 24h (data_atual e data_anterior)]
    G --> H[Recupera mensagens do grupo no período]
    H --> I[Formata mensagens para o CrewAI]
    I --> J[Gera resumo com CrewAI (summary_crew.kickoff)]
    J --> K{Enviar para grupo?}
    K -- Sim --> L[Envia resumo para o grupo (evo_send.textMessage)]
    K -- Não --> M
    L --> M{Enviar para número pessoal?}
    K -- Não --> M
    M -- Sim --> N[Envia resumo para número pessoal (evo_send.textMessage)]
    M -- Não --> O
    N --> O[Registra sucesso no log (log_summary.txt)]
    O --> P[Fim]
```
