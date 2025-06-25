# flowchart_diagram_enhanced.py
from diagrams import Diagram, Edge, Cluster
from diagrams.onprem.client import User
from diagrams.programming.language import Python
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Internet
from diagrams.onprem.logging import FluentBit


# --- Definição do Diagrama Melhorado ---
graph_attr = {
    "nodesep": "1.5",
    "ranksep": "2.0",
    "bgcolor": "#f4f8fb",
    "fontname": "Segoe UI",
    "fontsize": "16",
    "label": "\n\n📈 WhatsApp Manager: Geração e Envio de Resumos",
    "labelloc": "t",
    "labeljust": "c"
}

with Diagram(
    "Sistema WhatsApp Manager - Fluxo de Geração e Envio de Resumos", 
    show=False, 
    filename="flowchart_diagram_enhanced2", 
    outformat="png", 
    graph_attr=graph_attr
):
    

    inicio = User("Início: Tarefa Agendada")

    with Cluster("🔧 Configuração e Inicialização", graph_attr={"bgcolor": "#e3f2fd", "style": "rounded", "margin": "40"}):
        env_vars = Python("Carrega Variáveis\nde Ambiente (.env)")
        args_input = Python("Recebe Argumento\n--task_name")
        extract_id = Python("Extrai group_id\ndo task_name")
        load_group = Server("Carrega Dados\ndo Grupo")

    with Cluster("✅ Validação", graph_attr={"bgcolor": "#fffde7", "style": "rounded,bold", "color": "#fbc02d", "margin": "40"}):
        check_group = Python("🔶 Grupo Existe e\nResumo Habilitado?")
        group_error = User("Fim:\n Grupo Não Encontrado\nou Resumo Desabilitado")

    with Cluster("📊 Processamento de Dados", graph_attr={"bgcolor": "#f3e5f5", "style": "rounded","margin": "40"}):
        calc_interval = Python("Calcula Intervalo\nde 24 horas")
        retrieve_msgs = Server("Recupera Mensagens\ndo Grupo no Período")
        format_msgs = Python("Formata Mensagens\npara o CrewAI")

    with Cluster("🤖 Geração de Resumo (CrewAI)", graph_attr={"bgcolor": "#e8f5e8", "style": "rounded","margin": "40"}):
        generate_summary = Python("Gera Resumo\ncom CrewAI")

    with Cluster("📱 Envio de Mensagens", graph_attr={"bgcolor": "#e1f5fe", "style": "rounded","margin": "40"}):
        send_group_q = Internet("❓ Enviar para\nGrupo?")
        send_to_group = Internet("Envia Resumo\npara o Grupo")
        send_personal_q = Internet("❓ Enviar para\nNúmero Pessoal?")
        send_to_personal = Internet("Envia Resumo para\nNúmero Pessoal")

    with Cluster("📝 Finalização", graph_attr={"bgcolor": "#f5f5f5", "style": "rounded","margin": "40"}):
        log_success = FluentBit("Registra Sucesso\nno Log")
        fim = User("Fim")


    # --- Definição do Fluxo ---
    _ = inicio >> env_vars >> args_input >> extract_id >> load_group >> check_group

    _ = check_group >> Edge(label="❌ Não", color="red", style="dashed") >> group_error
    _ = check_group >> Edge(label="✅ Sim", color="green", style="bold") >> calc_interval

    _ = calc_interval >> retrieve_msgs >> format_msgs >> generate_summary

    _ = generate_summary >> send_group_q
    _ = send_group_q >> Edge(label="✅ Sim", color="green", style="bold") >> send_to_group
    _ = send_group_q >> Edge(label="❌ Não", color="orange", style="dashed") >> send_personal_q

    _ = send_to_group >> send_personal_q

    _ = send_personal_q >> Edge(label="✅ Sim", color="green", style="bold") >> send_to_personal
    _ = send_personal_q >> Edge(label="❌ Não", color="orange", style="dashed") >> log_success

    _ = send_to_personal >> log_success
    _ = log_success >> fim

print("✅ Diagrama de fluxo melhorado gerado com sucesso!")
print("📁 Arquivo: flowchart_diagram_enhanced.png")
