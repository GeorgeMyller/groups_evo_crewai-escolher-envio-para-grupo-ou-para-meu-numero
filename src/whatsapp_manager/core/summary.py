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

# Initialize logging system / Inicializa sistema de logging
try:
    from whatsapp_manager.utils.logger import get_logger, TaskExecutionMonitor
    logger = get_logger("summary_task", "DEBUG")
    task_monitor = TaskExecutionMonitor()
    task_monitor.log_environment_info()
except ImportError:
    # Fallback para print se o logger não estiver disponível
    logger = None
    task_monitor = None
    print("WARNING: Sistema de logging não disponível, usando print")

# Get WhatsApp number from environment / Obtém número do WhatsApp do ambiente
personal_number = os.getenv("WHATSAPP_NUMBER")
if personal_number:
    # Garante que o número está no formato correto
    personal_number = personal_number.strip()
    if not personal_number.endswith('@s.whatsapp'):
        personal_number = f"{personal_number}@s.whatsapp"

config_info = f"\nConfigurações carregadas:\nNúmero do WhatsApp: {personal_number}\nBase URL: {os.getenv('EVO_BASE_URL')}\nInstance Name: {os.getenv('EVO_INSTANCE_NAME')}"
if logger:
    logger.info(config_info)
else:
    print(config_info)

# Initialize SendSandeco / Inicializa SendSandeco
evo_send = SendSandeco()

# Command line argument initialization / Inicialização dos argumentos de linha de comando
parser = argparse.ArgumentParser(description="Group Summary Generator / Gerador de Resumos de Grupo")
parser.add_argument("--task_name", required=True, 
                   help="Scheduled task identifier (formato: ResumoGrupo_[ID]) / Nome da tarefa agendada")
args = parser.parse_args()

# Extract group ID from task name / Extrai o ID do grupo do nome da tarefa
group_id = args.task_name.split("_")[1]

# Log task start / Log início da tarefa
start_message = f"EXECUTANDO TAREFA AGENDADA - Task: {args.task_name}, Group ID: {group_id}"
if logger:
    logger.info(start_message)
    if task_monitor:
        task_monitor.log_task_start(args.task_name, group_id)
else:
    print(start_message)

control = GroupController()
df = control.load_data_by_group(group_id)
group = control.find_group_by_id(group_id)
if group is None:
    error_message = f"Group with ID {group_id} not found."
    if logger:
        logger.error(error_message)
        if task_monitor:
            task_monitor.log_task_error(args.task_name, group_id, error_message)
    else:
        print(error_message)
    sys.exit(1)  # Exit with error code
nome = group.name

group_info = f"Resumo do grupo : {nome}"
if logger:
    logger.info(group_info)
else:
    print(group_info)

# Ensure group summary information is present in group_summary.csv
# Garante que as informações do resumo do grupo estejam no arquivo group_summary.csv
if not df:
    if logger:
        logger.warning("Dados do grupo não encontrados, criando configuração padrão")
    control.update_summary(group_id, '22:00', True, False, False, __file__)
    df = control.load_data_by_group(group_id)

if df and df.get('enabled', False):
    """
    Message Processing and Summary Generation / Processamento de Mensagens e Geração do Resumo
    
    PT-BR:
    - Calcula o intervalo de tempo para coleta (usando datas configuradas ou últimas 24 horas)
    - Recupera e formata as mensagens do período
    - Gera o resumo usando CrewAI
    - Envia o resultado de volta ao grupo
    
    EN:
    - Calculates time range for collection (using configured dates or last 24 hours)
    - Retrieves and formats messages from the period
    - Generates summary using CrewAI
    - Sends result back to the group
    """
    # Tenta obter datas configuradas no CSV
    formato = "%Y-%m-%d %H:%M:%S"
    start_date = df.get('start_date')
    start_time = df.get('start_time')
    end_date = df.get('end_date')
    end_time = df.get('end_time')

    # Se todos os campos de data/hora estiverem presentes e válidos, usa-os
    if start_date and start_time and end_date and end_time and str(start_date) != 'nan' and str(start_time) != 'nan' and str(end_date) != 'nan' and str(end_time) != 'nan':
        data_anterior_formatada = f"{start_date} {start_time}"
        data_atual_formatada = f"{end_date} {end_time}"
        time_info = f"Data inicial configurada: {data_anterior_formatada}\nData final configurada: {data_atual_formatada}"
    else:
        # fallback: últimas 24h
        data_atual = datetime.now()
        data_anterior = data_atual - timedelta(days=1)
        data_atual_formatada = data_atual.strftime(formato)
        data_anterior_formatada = data_anterior.strftime(formato)
        time_info = f"Data atual: {data_atual_formatada}\nData de 1 dia anterior: {data_anterior_formatada}"

    if logger:
        logger.info(time_info)
    else:
        print(time_info)

    # Recupera mensagens para o período especificado
    try:
        msgs = control.get_messages(group_id, data_anterior_formatada, data_atual_formatada)
        if logger:
            logger.info(f"Mensagens recuperadas com sucesso: {len(msgs)} mensagens")
    except Exception as e:
        error_msg = f"Erro ao recuperar mensagens: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
            if task_monitor:
                task_monitor.log_task_error(args.task_name, group_id, error_msg)
        else:
            print(error_msg)
        sys.exit(1)

    cont = len(msgs)
    msg_count_info = f"Total de mensagens: {cont}"
    if logger:
        logger.info(msg_count_info)
    else:
        print(msg_count_info)

    # Carrega o valor de min_messages_summary do group_summary.csv
    min_messages_config = df.get('min_messages_summary', 50) # Default para 50 se não encontrado

    # Verifica se o total de mensagens é superior ao configurado
    if cont <= min_messages_config:
        skip_reason = f"O número de mensagens ({cont}) é inferior ou igual ao configurado ({min_messages_config}). O resumo não será gerado."
        if logger:
            logger.info(skip_reason)
            if task_monitor:
                task_monitor.log_task_skipped(args.task_name, group_id, skip_reason)
        else:
            print(skip_reason)
        sys.exit(0) # Sai sem erro, pois não é uma falha, mas uma condição não atendida

    # Delay for processing
    # Aguarda processamento
    if logger:
        logger.info("Aguardando 20 segundos para processamento...")
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

    if logger:
        logger.debug(f"Mensagens formatadas para CrewAI: {pull_msg[:500]}...")  # Log apenas primeiros 500 chars
    else:
        print(pull_msg)
    
    # Summary generation and delivery / Geração e entrega do resumo
    inputs = {
        "msgs": pull_msg
    }
    
    try:
        if logger:
            logger.info("Iniciando geração de resumo com CrewAI...")
        summary_crew = SummaryCrew()
        resposta = summary_crew.kickoff(inputs=inputs)
        if logger:
            logger.info("Resumo gerado com sucesso")
            logger.debug(f"Resumo gerado: {resposta[:200]}...")  # Log apenas primeiros 200 chars
    except Exception as e:
        error_msg = f"Erro ao gerar resumo com CrewAI: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
            if task_monitor:
                task_monitor.log_task_error(args.task_name, group_id, error_msg)
        else:
            print(error_msg)
        sys.exit(1)

    # Send summary based on configuration / Envia resumo com base na configuração
    send_success = False
    destinations = []
    
    if df.get('send_to_group', True):
        try:
            evo_send.textMessage(group_id, resposta)
            destinations.append("grupo")
            send_success = True
            if logger:
                logger.info(f"Resumo enviado para o grupo: {nome}")
            else:
                print(f"Resumo enviado para o grupo: {nome}")
        except Exception as e:
            error_msg = f"Erro ao enviar resumo para o grupo: {str(e)}"
            if logger:
                logger.error(error_msg, exc_info=True)
            else:
                print(error_msg)

    # Envia para o número pessoal se estiver definido
    if personal_number:
        try:
            mensagem = f"Resumo do grupo {nome}:\n\n{resposta}"
            evo_send.textMessage(personal_number, mensagem)
            destinations.append("número pessoal")
            send_success = True
            if logger:
                logger.info(f"Resumo enviado para número pessoal: {personal_number}")
            else:
                print(f"Resumo enviado para número pessoal: {personal_number}")
        except Exception as e:
            error_msg = f"Erro ao enviar para número pessoal: {str(e)}"
            if logger:
                logger.error(error_msg, exc_info=True)
            else:
                print(error_msg)

    # Success logging / Registro de sucesso
    # Ensure log_summary.txt is written to the data directory at the project root
    log_file_path = os.path.join(PROJECT_ROOT, "data", "log_summary.txt")

    if send_success and destinations:
        destinations_str = " e ".join(destinations)
        success_msg = f"Resumo gerado e enviado com sucesso para {destinations_str}!"
        
        if logger:
            logger.info(success_msg)
            if task_monitor:
                task_monitor.log_task_success(args.task_name, group_id, cont)
        
        # Log tradicional para compatibilidade
        # Usa data_atual_formatada (data final do período de busca) para o log
        with open(log_file_path, "a", encoding="utf-8") as arquivo:
            log = f"[{data_atual_formatada}] [INFO] [GRUPO: {nome}] [GROUP_ID: {group_id}] - Mensagem: {success_msg}\n"
            arquivo.write(log)
    else:
        error_msg = "Falha ao enviar resumo para qualquer destino"
        if logger:
            logger.error(error_msg)
            if task_monitor:
                task_monitor.log_task_error(args.task_name, group_id, error_msg)
        sys.exit(1)
        
else:
    skip_msg = "Grupo não encontrado ou resumo não está habilitado para este grupo. / Group not found or summary is not enabled for this group."
    if logger:
        logger.warning(skip_msg)
        if task_monitor:
            task_monitor.log_task_skipped(args.task_name, group_id, skip_msg)
    else:
        print(skip_msg)