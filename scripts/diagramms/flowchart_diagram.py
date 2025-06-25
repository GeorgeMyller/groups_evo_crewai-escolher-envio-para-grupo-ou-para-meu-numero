# flowchart_diagram_custom_absolute.py
import base64
import os
from diagrams import Diagram, Edge, Cluster
from diagrams.programming.flowchart import Decision

# A classe Custom é necessária para usar ícones próprios.
from diagrams.custom import Custom

# --- Função Auxiliar para Salvar Ícones ---
def save_icon_from_base64(base64_string, filename):
    """
    Decodifica uma string de dados URI Base64, salva como um arquivo SVG
    e retorna o caminho ABSOLUTO para o arquivo, que é mais confiável para o Graphviz.
    """
    output_dir = "custom_icons"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    filepath = os.path.join(output_dir, filename)

    try:
        # Extrai o conteúdo Base64 da string de dados URI
        header, encoded = base64_string.split(",", 1)
        data = base64.b64decode(encoded)
        with open(filepath, "wb") as f:
            f.write(data)
        # *** MELHORIA PRINCIPAL: Retorna o caminho absoluto do arquivo ***
        return os.path.abspath(filepath)
    except (ValueError, TypeError) as e:
        print(f"Erro ao decodificar a string Base64 para {filename}: {e}")
        return None

# --- Definições dos Ícones SVG Personalizados (Base64 Encoded) ---
ICON_START_TASK = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzI4YTc0NSI+PHBhdGggZD0iTTggNXYxNGwxMS03eiIvPjwvc3ZnPg=="
ICON_END_FLOW = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzYxNjE2MSI+PHBhdGggZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6Ii8+PC9zdmc+"
ICON_ENV_VARS = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzM3NDc0RiI+PHBhdGggZD0iTTIgNmgyMHYxMkgwdi01bDMtM3YtM2wtMy0yeiIvPjxwYXRoIGQ9Ik00IDhoMnYySDQiIGZpbGw9IiNmZmYiLz48cGF0aCBkPSJtOCAxMyAzIDMgMy0zeiIgZmlsbD0iI2ZmZiIvPjwvc3ZnPg=="
ICON_ARGUMENT = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzQyNDI0MiI+PHBhdGggZD0iTTYgOWg0djJINnoiLz48cGF0aCBkPSJNNiA2bDMgMy41TDYgMTNINHYtN2gybS0xIDFoMXY1aC0xdi01eiIvPjxwYXRoIGQ9Ik0yIDR2MTZoMjBWNEgyem0xOCAxNGgtMTZWNkg0djEwaDE2VjZoMnYxMnoiLz48L3N2Zz4="
ICON_EXTRACT_ID = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzE5NzZkMiI+PHBhdGggZD0iTTMgMTdoNHYyaC00ek0xMCA3aDR2MmgtNHpNMyAzaDE4djJoLTQvMTh2M2gtMnYtM2gtNHYzaC0ydi0zaC00djNoLTJ2LTN6TTEwIDEyLjVoNGwxLjUgNC41aC03eiIvPjwvc3ZnPg=="
ICON_LOAD_DATA = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzAwNjA2NCI+PHBhdGggZD0iTTQgMThoMTZ2LTJIMHYyeiIvPjxwYXRoIGQ9Ik00IDE0aDE2di0ySDR2MnoiLz48cGF0aCBkPSJNMjAgMTBWM0g0djdoMnYtNWgxMnY1em0tMiAyaC04djJoOHYtMnoiLz48L3N2Zz4="
ICON_END_ERROR = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI0QzMjkzMCI+PHBhdGggZD0iTTEyIDJDNi40NyAyIDIgNi40NyAyIDEyczQuNDcgMTAgMTAgMTAgMTAtNC40NyAxMC0xMFMxNy41MyAyIDEyIDJ6bTUgMTMuNTlsLTEuNDEgMS40MUwxMiAxMy40MWwtMy41OSAzLjU5TDIuODMgOC40MWwzLjU5IDMuNTkgMS40MS0xLjQxTDEzLjQxIDEybDMuNTkgMy41OXoiLz48L3N2Zz4="
ICON_CALCULATE = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzRiMzQ1osiI+PHBhdGggZD0iTTcgMnYySDN2MThoMThWNEgyMHYtMkg3em0wIDRoMnYyaC0yVjZ6bTQgMGgydjJoLTJWOXptNCAwaDJ2MmgtMlY2ek03IDEwaDJ2MmgtMlYxMHptNCAwaDJ2MmgtMlYxMHptNCAwaDJ2MmgtMlYxMHptLThIDRoMnYyaC0yVjE0em00IDBoMnYyaC0yVjE0eiIvPjwvc3ZnPg=="
ICON_MESSAGES_IN = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzAzYWRhNCI+PHBhdGggZD0iTTIwIDRoLTRsMS4wOSAxLjA5TDIgMjAuNDlMMi41MSAyMSA3LjkyIDE1LjQxTDIwIDRINHoiLz48L3N2Zz4="
ICON_TRANSFORM = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iI2FkNGNkYSI+PHBhdGggZD0iTTYuNiAxbDIuNCAyLjRIMnYzaDE4di0zaC03bC0yLjQtMi40ek0yMiAxMS44aC0zLjJsMy4yIDMuMnYtMy4yem0tMTYgMEg5djQuOEg2eiIvPjwvc3ZnPg=="
ICON_AI_SUMMARY = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzM4OGU3YyI+PHBhdGggZD0iTTcgNmgydjJIN3ptNCAwaDJ2MkgxMXptNCAwaDJ2MkgxNXoiLz48cGF0aCBkPSJNOSAxMGgydjJIMXptNCAwaDJ2MkgxM3oiLz48cGF0aCBkPSJNOSAxNGgydjJIMXptNCAwaDJ2MkgxM3oiLz48cGF0aCBkPSJNMTIgMmMtNC40MiAwLTggMy41OC04IDhzMy41OCA4IDggOCA4LTMuNTggOC04LTcuNTgtOC04LTgtMTAgMTAuNDUgMTAgMTAtMTAgMTAtNC41IDAtMTAgMC0yMCAweiIvPjwvc3ZnPg=="
ICON_SEND_MESSAGE = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzAyODhEMSI+PHBhdGggZD0iTTIgMjFsMjEtOS0yMS05diE3bDE1IDJMMiAxNHoiLz48L3N2Zz4="
ICON_LOG_SUCCESS = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0iIzBEMzA0MiI+PHBhdGggZD0iTTkgMTYuMTdsLTQuMi00LjJMMi43IDIzLjM5IDkgMTguMSAxOSA1LjU5IDE3LjU5IDQuMTl6Ii8+PC9zdmc+"

# --- Salvando os Ícones em Arquivos e Obtendo Caminhos Absolutos ---
icon_start_path = save_icon_from_base64(ICON_START_TASK, "icon_start.svg")
icon_end_path = save_icon_from_base64(ICON_END_FLOW, "icon_end.svg")
icon_env_path = save_icon_from_base64(ICON_ENV_VARS, "icon_env.svg")
icon_arg_path = save_icon_from_base64(ICON_ARGUMENT, "icon_arg.svg")
icon_extract_path = save_icon_from_base64(ICON_EXTRACT_ID, "icon_extract.svg")
icon_load_path = save_icon_from_base64(ICON_LOAD_DATA, "icon_load.svg")
icon_error_path = save_icon_from_base64(ICON_END_ERROR, "icon_error.svg")
icon_calc_path = save_icon_from_base64(ICON_CALCULATE, "icon_calc.svg")
icon_msg_in_path = save_icon_from_base64(ICON_MESSAGES_IN, "icon_msg_in.svg")
icon_transform_path = save_icon_from_base64(ICON_TRANSFORM, "icon_transform.svg")
icon_ai_path = save_icon_from_base64(ICON_AI_SUMMARY, "icon_ai.svg")
icon_send_path = save_icon_from_base64(ICON_SEND_MESSAGE, "icon_send.svg")
icon_log_path = save_icon_from_base64(ICON_LOG_SUCCESS, "icon_log.svg")

# --- Definição do Diagrama ---
graph_attr = {
    "splines": "curved",
    "rankdir": "LR",
    "nodesep": "0.8",
    "ranksep": "1.5",
    "fontsize": "12",
    "fontname": "Helvetica",
}
node_attr = {
    "fontsize": "10",
    "fontname": "Helvetica"
}

with Diagram("Fluxo de Geração e Envio de Resumo (v3 - Custom)", show=False, filename="flowchart_diagram_v_custom", outformat="png", graph_attr=graph_attr, node_attr=node_attr):
    
    # Verificação para garantir que os ícones foram criados antes de usá-los
    if not all([icon_start_path, icon_end_path, icon_env_path, icon_arg_path, icon_extract_path, icon_load_path, icon_error_path, icon_calc_path, icon_msg_in_path, icon_transform_path, icon_ai_path, icon_send_path, icon_log_path]):
        raise Exception("Falha ao criar um ou mais arquivos de ícone. O diagrama não pode ser gerado.")

    inicio = Custom("Início: Tarefa Agendada", icon_start_path)
    fim = Custom("Fim", icon_end_path, width="0.5", height="0.5")

    with Cluster("Configuração e Inicialização"):
        env_vars_node = Custom("Carrega Variáveis\nde Ambiente (.env)", icon_env_path)
        args_input_node = Custom("Recebe Argumento\n--task_name", icon_arg_path)
        extract_id_node = Custom("Extrai group_id\ndo task_name", icon_extract_path)
        load_group_data_node = Custom("Carrega Dados do Grupo", icon_load_path)
        
    with Cluster("Validação do Grupo"):
        check_group_enabled = Decision("Grupo Existe e\nResumo Habilitado?")
        group_not_found = Custom("Fim: Grupo Não Encontrado\nou Desabilitado", icon_error_path)

    with Cluster("Processamento de Mensagens"):
        calc_interval = Custom("Calcula Intervalo\nde 24h", icon_calc_path)
        retrieve_msgs = Custom("Recupera Mensagens do\nGrupo no Período", icon_msg_in_path)
        format_msgs = Custom("Formata Mensagens\npara o CrewAI", icon_transform_path)
        
    with Cluster("Geração do Resumo (CrewAI)"):
        generate_summary = Custom("Gera Resumo\ncom CrewAI", icon_ai_path)
        
    with Cluster("Envio do Resumo"):
        send_to_group_decision = Decision("Enviar para Grupo?")
        send_to_group = Custom("Envia Resumo\npara o Grupo", icon_send_path)
        send_to_personal_decision = Decision("Enviar para\nNúmero Pessoal?")
        send_to_personal = Custom("Envia Resumo para\nNúmero Pessoal", icon_send_path)

    log_success = Custom("Registra Sucesso no Log", icon_log_path)

    # --- Definição do Fluxo (Edges) ---
    inicio >> env_vars_node >> args_input_node >> extract_id_node >> load_group_data_node >> check_group_enabled

    check_group_enabled >> Edge(label="Não", color="red", style="dashed") >> group_not_found
    check_group_enabled >> Edge(label="Sim", color="green", style="bold") >> calc_interval

    calc_interval >> retrieve_msgs >> format_msgs >> generate_summary

    generate_summary >> send_to_group_decision
    send_to_group_decision >> Edge(label="Sim", color="green", style="bold") >> send_to_group
    send_to_group_decision >> Edge(label="Não", color="red", style="dashed") >> send_to_personal_decision 

    send_to_group >> send_to_personal_decision 

    send_to_personal_decision >> Edge(label="Sim", color="green", style="bold") >> send_to_personal
    send_to_personal_decision >> Edge(label="Não", color="red", style="dashed") >> log_success 

    send_to_personal >> log_success

    log_success >> Edge(minlen="2", style="dashed", color="grey") >> fim
