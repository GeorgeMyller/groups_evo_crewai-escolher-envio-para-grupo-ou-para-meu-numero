"""
Sistema de Geração e Envio de Resumos de Grupos / Group Message Summary Generation and Sending System

PT-BR:
Este módulo implementa a geração automática de resumos das mensagens dos grupos.
Processa as mensagens de um período específico e utiliza CrewAI para gerar
um resumo inteligente que é enviado de volta ao grupo.

EN:
This module implements automatic group message summary generation.
It processes messages from a specific time period and uses CrewAI to generate
an intelligent summary that is sent back to the group.
"""

import argparse
import os
import sys
import time
from datetime import datetime, timedelta # Keep as is, or split if strict one-per-line for all froms

# Define Project Root assuming this file is src/whatsapp_manager/core/summary.py
# Navigate three levels up to reach the project root from core.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Add src directory to Python path to enable absolute imports when running as script
import sys
src_path = os.path.join(PROJECT_ROOT, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Third-party library imports
from dotenv import load_dotenv

# Local application/library imports - try relative first, fallback to absolute
try:
    # This works when imported as a module
    from .group_controller import GroupController
    from .summary_crew import SummaryCrew
    from .send_sandeco import SendSandeco
except ImportError:
    # This works when executed as a script
    from whatsapp_manager.core.group_controller import GroupController
    from whatsapp_manager.core.summary_crew import SummaryCrew
    from whatsapp_manager.core.send_sandeco import SendSandeco

# Load environment variables / Carrega variáveis de ambiente
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path, override=True) # Added override=True for consistency

# Get WhatsApp number from environment / Obtém número do WhatsApp do ambiente
personal_number = os.getenv("WHATSAPP_NUMBER")
if personal_number:
    # Garante que o número está no formato correto
    personal_number = personal_number.strip()
    if not personal_number.endswith('@s.whatsapp'):
        personal_number = f"{personal_number}@s.whatsapp"

print(f"\nConfigurações carregadas:")
print(f"Número do WhatsApp: {personal_number}")
print(f"Base URL: {os.getenv('EVO_BASE_URL')}")
print(f"Instance Name: {os.getenv('EVO_INSTANCE_NAME')}")

# Initialize SendSandeco / Inicializa SendSandeco
evo_send = SendSandeco()

# Command line argument initialization / Inicialização dos argumentos de linha de comando
parser = argparse.ArgumentParser(description="Group Summary Generator / Gerador de Resumos de Grupo")
parser.add_argument("--task_name", required=True, 
                   help="Scheduled task identifier (formato: ResumoGrupo_[ID]) / Nome da tarefa agendada")
args = parser.parse_args()

# Extract group ID from task name / Extrai o ID do grupo do nome da tarefa
group_id = args.task_name.split("_")[1]

control = GroupController()
df = control.load_data_by_group(group_id)
group = control.find_group_by_id(group_id)
if group is None:
    print(f"Group with ID {group_id} not found.")
    sys.exit(1)  # Exit with error code
nome = group.name

# Ensure group summary information is present in group_summary.csv
# Garante que as informações do resumo do grupo estejam no arquivo group_summary.csv
if not df:
    control.update_summary(group_id, '22:00', True, False, False, __file__)
    df = control.load_data_by_group(group_id)

print("EXECUTANDO TAREFA AGENDADA")
print(f"Resumo do grupo : {nome}")

if df and df.get('enabled', False):
    """
    Message Processing and Summary Generation / Processamento de Mensagens e Geração do Resumo
    
    PT-BR:
    - Calcula o intervalo de tempo para coleta (últimas 24 horas)
    - Recupera e formata as mensagens do período
    - Gera o resumo usando CrewAI
    - Envia o resultado de volta ao grupo
    
    EN:
    - Calculates time range for collection (last 24 hours)
    - Retrieves and formats messages from the period
    - Generates summary using CrewAI
    - Sends result back to the group
    """
    # Calculate time range for message collection
    # Calcula o intervalo de tempo para coleta de mensagens
    data_atual = datetime.now()
    data_anterior = data_atual - timedelta(days=1)

    formato = "%Y-%m-%d %H:%M:%S"
    data_atual_formatada = data_atual.strftime(formato)
    data_anterior_formatada = data_anterior.strftime(formato)

    print(f"Data atual: {data_atual_formatada}")
    print(f"Data de 1 dia anterior: {data_anterior_formatada}")

    # Retrieve messages for the specified time period
    # Recupera mensagens para o período especificado
    msgs = control.get_messages(group_id, data_anterior_formatada, data_atual_formatada)

    cont = len(msgs)
    print(f"Total de mensagens: {cont}")

    # Carrega o valor de min_messages_summary do group_summary.csv
    min_messages_config = df.get('min_messages_summary', 50) # Default para 50 se não encontrado

    # Verifica se o total de mensagens é superior ao configurado
    if cont <= min_messages_config:
        print(f"O número de mensagens ({cont}) é inferior ou igual ao configurado ({min_messages_config}). O resumo não será gerado.")
        sys.exit(0) # Sai sem erro, pois não é uma falha, mas uma condição não atendida

    # Delay for processing
    # Aguarda processamento
    time.sleep(20)

    # Message data formatting for CrewAI / Formatação dos dados para o CrewAI
    pull_msg = f"""
    Group Message Data / Dados sobre as mensagens do grupo
    Initial Date / Data Inicial: {data_anterior_formatada}
    Final Date / Data Final: {data_atual_formatada}
    
    USER MESSAGES FOR SUMMARY / MENSAGENS DOS USUÁRIOS PARA O RESUMO:
    --------------------------
    """

    for msg in reversed(msgs):
        pull_msg += f"""
        Nome: *{msg.get_name()}*
        Postagem: "{msg.get_text()}"  
        data: {time.strftime("%d/%m %H:%M", time.localtime(msg.message_timestamp))}'     
        """

    print(pull_msg)
    
    # Summary generation and delivery / Geração e entrega do resumo
    inputs = {
        "msgs": pull_msg
    }
    
    summary_crew = SummaryCrew()
    resposta = summary_crew.kickoff(inputs=inputs)

    # Send summary based on configuration / Envia resumo com base na configuração
    if df.get('send_to_group', True):
        evo_send.textMessage(group_id, resposta)
        print(f"Resumo enviado para o grupo: {nome}")

    # Envia para o número pessoal se estiver definido
    if personal_number:
        try:
            mensagem = f"Resumo do grupo {nome}:\n\n{resposta}"
            evo_send.textMessage(personal_number, mensagem)
            print(f"Resumo enviado para número pessoal: {personal_number}")
        except Exception as e:
            print(f"Erro ao enviar para número pessoal: {str(e)}")

    # Success logging / Registro de sucesso
    # Ensure log_summary.txt is written to the data directory at the project root
    log_file_path = os.path.join(PROJECT_ROOT, "data", "log_summary.txt")

    with open(log_file_path, "a", encoding="utf-8") as arquivo:
        destinations = []
        if df.get('send_to_group', True):
            destinations.append("grupo")
        if personal_number:  # Atualizado aqui também
            destinations.append("número pessoal")
        
        destinations_str = " e ".join(destinations)
        log = f"[{data_atual}] [INFO] [GRUPO: {nome}] [GROUP_ID: {group_id}] - Mensagem: Resumo gerado e enviado com sucesso para {destinations_str}!"
        arquivo.write(log)
else:
    print("Grupo não encontrado ou resumo não está habilitado para este grupo. / Group not found or summary is not enabled for this group.")