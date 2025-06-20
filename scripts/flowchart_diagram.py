"""
Diagrama do fluxo real de geração/envio de resumo, refletindo a lógica do programa conforme flowchart.md.
"""
from diagrams import Diagram, Edge, Cluster
# Nodes on-prem (genéricos ou para componentes locais)
from diagrams.onprem.compute import Server
from diagrams.onprem.client import User
# Reverting to the generic _Logging as Logging_Icon from previous attempt, hoping it works now.
# If _Logging also fails, we will need to use a different node like Server for logging.
from diagrams.onprem.logging import _Logging as Logging_Icon # Using _Logging as previously identified
from diagrams.onprem.workflow import Airflow # Para fluxo de trabalho ou agendamento
# Nodes de programação/fluxo
# Removed Terminator as it caused an ImportError. Keeping Decision.
# Added Dataflow import for message processing nodes
# Use Process for message processing and summary generation steps
# Use Operation for message processing and summary generation steps
from diagrams.programming.flowchart import Decision
# Using Blank from generic for "Fim"
from diagrams.generic.blank import Blank # For the 'Fim' node

with Diagram("Fluxo de Geração e Envio de Resumo", show=False, filename="flowchart_diagram_v4", outformat="png", direction="LR", graph_attr={"splines": "curved", "rankdir": "LR"}):
    # Nodos de início e fim
    # Using Server for start and Blank for end due to Terminator import error
    inicio = Server("Início: Tarefa Agendada") # Changed from Terminator
    fim = Blank("Fim") # Changed from Terminator

    with Cluster("Configuração e Inicialização"):
        env_vars = Server("Carrega Variáveis de Ambiente (.env)")
        args_input = Airflow("Recebe Argumento --task_name")
        extract_id = Airflow("Extrai group_id do task_name")
        load_group_data = Server("Carrega Dados do Grupo")
        
    with Cluster("Validação do Grupo"):
        check_group_enabled = Decision("Grupo Existe e Resumo Habilitado?")
        # Using a simple Server node for the error end path
        group_not_found = Server("Fim: Grupo Não Encontrado ou Desabilitado") # Removed style/color, not supported

    with Cluster("Processamento de Mensagens"):
        calc_interval = Server("Calcula Intervalo de 24h")
        retrieve_msgs = Server("Recupera Mensagens do Grupo no Período")
        format_msgs = Server("Formata Mensagens para o CrewAI")
        
    with Cluster("Geração do Resumo (CrewAI)"):
        generate_summary = Server("Gera Resumo com CrewAI")

    with Cluster("Envio do Resumo"):
        send_to_group_decision = Decision("Enviar para Grupo?")
        send_to_group = User("Envia Resumo para o Grupo")
        send_to_personal_decision = Decision("Enviar para Número Pessoal?")
        send_to_personal = User("Envia Resumo para Número Pessoal")

    log_success = Logging_Icon("Registra Sucesso no Log") 

    # Definindo o fluxo
    inicio >> env_vars >> args_input >> extract_id >> load_group_data >> check_group_enabled

    # Ramificação da decisão principal
    check_group_enabled - Edge(label="Não", color="red", style="dashed") >> group_not_found
    check_group_enabled - Edge(label="Sim", color="green", style="bold") >> calc_interval

    calc_interval >> retrieve_msgs >> format_msgs >> generate_summary

    generate_summary >> send_to_group_decision

    # Fluxo de envio para o grupo
    send_to_group_decision - Edge(label="Sim", color="green", style="bold") >> send_to_group
    # Conecta "Não" diretamente para a próxima decisão
    send_to_group_decision - Edge(label="Não", color="red", style="dashed") >> send_to_personal_decision 

    # Conecta o envio para o grupo com a próxima decisão
    send_to_group >> send_to_personal_decision 

    # Fluxo de envio para o número pessoal
    send_to_personal_decision - Edge(label="Sim", color="green", style="bold") >> send_to_personal
    # Conecta "Não" diretamente para o log
    send_to_personal_decision - Edge(label="Não", color="red", style="dashed") >> log_success 

    send_to_personal >> log_success

    log_success >> fim