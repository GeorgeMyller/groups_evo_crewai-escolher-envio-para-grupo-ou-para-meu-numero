```mermaid
flowchart TD
    A[Interface Streamlit (2_Portuguese.py/3_English.py)] -->|Salva configurações e agenda| B[Agendamento de Tarefas (task_scheduler.py)]
    B -->|Executa no horário| C[Script de Resumo (summary.py)]
    C --> D[Coleta dados do grupo (group_controller.py)]
    D --> E[Gera resumo com IA (summary_crew.py)]
    E --> F[Envia resumo (send_sandeco.py)]
    F --> G[Registra no log (log_summary.txt)]
    click A call linkCallback("/Volumes/SSD-EXTERNO/2025/Abril/livro_mcp/groups_evo_crewai-escolher-envio-para-grupo-ou-para-meu-numero/pages/2_Portuguese.py")
    click B call linkCallback("/Volumes/SSD-EXTERNO/2025/Abril/livro_mcp/groups_evo_crewai-escolher-envio-para-grupo-ou-para-meu-numero/task_scheduler.py")
    click C call linkCallback("/Volumes/SSD-EXTERNO/2025/Abril/livro_mcp/groups_evo_crewai-escolher-envio-para-grupo-ou-para-meu-numero/summary.py")
    click D call linkCallback("/Volumes/SSD-EXTERNO/2025/Abril/livro_mcp/groups_evo_crewai-escolher-envio-para-grupo-ou-para-meu-numero/group_controller.py")
    click E call linkCallback("/Volumes/SSD-EXTERNO/2025/Abril/livro_mcp/groups_evo_crewai-escolher-envio-para-grupo-ou-para-meu-numero/summary_crew.py")
    click F call linkCallback("/Volumes/SSD-EXTERNO/2025/Abril/livro_mcp/groups_evo_crewai-escolher-envio-para-grupo-ou-para-meu-numero/send_sandeco.py")
```