"""
Serviço de Geração de Resumos / Summary Generation Service

PT-BR:
Este serviço implementa a lógica de negócio para geração de resumos
inteligentes das             # Gerar resumo usando IA
            summary = self.summary_crew.generate_summary(formatted_messages)as dos grupos usando IA.

EN:
This service implements business logic for generating intelligent
summaries of group conversations using AI.
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime

from ..models.group import Group
from ..models.message import Message
from .message_service import MessageService
from ...infrastructure.messaging.message_sender import MessageSender
from .summary_crew_service import SummaryCrewService
from ...shared.utils.date_utils import DateUtils


class SummaryService:
    """
    Serviço para geração de resumos inteligentes
    Service for intelligent summary generation
    """
    
    def __init__(
        self, 
        message_service: MessageService,
        message_sender: MessageSender,
        summary_crew: SummaryCrewService
    ):
        """
        Inicializa o serviço
        Initializes the service
        """
        self.message_service = message_service
        self.message_sender = message_sender
        self.summary_crew = summary_crew
    
    def generate_and_send_summary(
        self,
        group: Group,
        days_back: int = 1,
        custom_period: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Gera e envia resumo para um grupo
        Generates and sends summary for a group
        
        Args:
            group: Objeto do grupo
            days_back: Quantos dias para trás buscar mensagens
            custom_period: Período customizado {"start": "YYYY-MM-DD HH:MM:SS", "end": "..."}
            
        Returns:
            Dicionário com resultado da operação
        """
        try:
            # Validar se resumo está habilitado
            if not group.enabled:
                return {
                    "success": False,
                    "error": "Resumo não habilitado para este grupo",
                    "group_id": group.group_id
                }
            
            # Obter mensagens
            messages = self._get_messages_for_summary(group, days_back, custom_period)
            
            # Verificar quantidade mínima de mensagens
            if len(messages) < group.min_messages_summary:
                return {
                    "success": False,
                    "error": f"Mensagens insuficientes: {len(messages)} < {group.min_messages_summary}",
                    "group_id": group.group_id,
                    "message_count": len(messages)
                }
            
            # Gerar resumo
            summary_result = self._generate_summary(group, messages)
            
            if not summary_result["success"]:
                return summary_result
            
            # Enviar resumo
            send_result = self._send_summary(group, summary_result["summary"])
            
            # Log da operação
            self._log_summary_operation(group, len(messages), send_result)
            
            return {
                "success": True,
                "group_id": group.group_id,
                "group_name": group.name,
                "message_count": len(messages),
                "summary_length": len(summary_result["summary"]),
                "sent_to_group": send_result.get("sent_to_group", False),
                "sent_to_personal": send_result.get("sent_to_personal", False),
                "summary": summary_result["summary"]
            }
            
        except Exception as e:
            error_msg = f"Erro ao gerar resumo para grupo {group.group_id}: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "group_id": group.group_id
            }
    
    def _get_messages_for_summary(
        self,
        group: Group,
        days_back: int,
        custom_period: Optional[Dict[str, str]] = None
    ) -> List[Message]:
        """
        Obtém mensagens para geração de resumo
        Gets messages for summary generation
        """
        if custom_period:
            # Período customizado
            messages = self.message_service.get_messages(
                group_id=group.group_id,
                start_date=custom_period["start"],
                end_date=custom_period["end"]
            )
        else:
            # Período padrão (últimos X dias)
            messages = self.message_service.get_messages_for_summary(
                group_id=group.group_id,
                days_back=days_back,
                include_names=group.is_names,
                include_links=group.is_links,
                min_messages=group.min_messages_summary
            )
        
        return messages
    
    def _generate_summary(self, group: Group, messages: List[Message]) -> Dict[str, Any]:
        """
        Gera resumo usando IA
        Generates summary using AI
        """
        try:
            # Formatar mensagens para IA
            formatted_messages = self.message_service.format_messages_for_ai(
                messages=messages,
                include_names=group.is_names
            )
            
            # Gerar resumo com CrewAI
            summary = self.summary_crew.generate_summary(formatted_messages)
            
            return {
                "success": True,
                "summary": summary
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Erro na geração do resumo: {str(e)}"
            }
    
    def _send_summary(self, group: Group, summary: str) -> Dict[str, bool]:
        """
        Envia resumo para destinos configurados
        Sends summary to configured destinations
        """
        result = {
            "sent_to_group": False,
            "sent_to_personal": False
        }
        
        # Formatar mensagem
        formatted_summary = f"📋 *Resumo do grupo {group.name}*\n\n{summary}"
        
        # Enviar para o grupo
        if group.send_to_group:
            try:
                self.message_sender.send_text_message(group.group_id, formatted_summary)
                result["sent_to_group"] = True
                print(f"Resumo enviado para o grupo: {group.name}")
            except Exception as e:
                print(f"Erro ao enviar resumo para o grupo {group.group_id}: {e}")
        
        # Enviar para número pessoal
        if group.send_to_personal:
            try:
                personal_number = self._get_personal_number()
                if personal_number:
                    self.message_sender.send_text_message(personal_number, formatted_summary)
                    result["sent_to_personal"] = True
                    print(f"Resumo enviado para número pessoal: {personal_number}")
            except Exception as e:
                print(f"Erro ao enviar resumo para número pessoal: {e}")
        
        return result
    
    def _get_personal_number(self) -> Optional[str]:
        """
        Obtém número pessoal das configurações
        Gets personal number from settings
        """
        personal_number = os.getenv("WHATSAPP_NUMBER")
        if personal_number and not personal_number.endswith('@s.whatsapp.net'):
            personal_number = f"{personal_number}@s.whatsapp.net"
        return personal_number
    
    def _log_summary_operation(
        self,
        group: Group,
        message_count: int,
        send_result: Dict[str, bool]
    ):
        """
        Registra operação de resumo em log
        Logs summary operation
        """
        try:
            # Determinar destinos
            destinations = []
            if send_result.get("sent_to_group", False):
                destinations.append("grupo")
            if send_result.get("sent_to_personal", False):
                destinations.append("número pessoal")
            
            destinations_str = " e ".join(destinations) if destinations else "nenhum destino"
            
            # Criar entrada de log
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = (
                f"[{timestamp}] [INFO] [GRUPO: {group.name}] [GROUP_ID: {group.group_id}] "
                f"- Resumo gerado com {message_count} mensagens e enviado para {destinations_str}!\n"
            )
            
            # Escrever no arquivo de log
            log_file_path = self._get_log_file_path()
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            
            with open(log_file_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry)
                
        except Exception as e:
            print(f"Erro ao escrever log: {e}")
    
    def _get_log_file_path(self) -> str:
        """
        Retorna caminho do arquivo de log
        Returns log file path
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
        return os.path.join(project_root, "data", "log_summary.txt")
