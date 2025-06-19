"""
Serviço de Gerenciamento de Mensagens / Message Management Service

PT-BR:
Este serviço implementa a lógica de negócio relacionada ao processamento
de mensagens do WhatsApp, incluindo busca, filtragem e formatação.

EN:
This service implements business logic related to WhatsApp message processing,
including fetching, filtering, and formatting.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..models.message import Message, MessageProcessor
from ...infrastructure.api.evolution_client import EvolutionClientWrapper


class MessageService:
    """
    Serviço para lógica de negócio relacionada a mensagens
    Service for message-related business logic
    """
    
    def __init__(self, evolution_client: EvolutionClientWrapper):
        """
        Inicializa o serviço
        Initializes the service
        """
        self.evolution_client = evolution_client
        self.message_processor = MessageProcessor()
    
    def get_messages(
        self, 
        group_id: str, 
        start_date: str, 
        end_date: str,
        limit: int = 1000
    ) -> List[Message]:
        """
        Obtém mensagens de um grupo em período específico
        Gets messages from a group in specific period
        
        Args:
            group_id: ID do grupo
            start_date: Data inicial (formato: "YYYY-MM-DD HH:MM:SS")
            end_date: Data final (formato: "YYYY-MM-DD HH:MM:SS")
            limit: Limite de mensagens
            
        Returns:
            Lista de mensagens processadas
        """
        try:
            # Converter datas para formato de timestamp
            start_timestamp = self._date_to_timestamp(start_date)
            end_timestamp = self._date_to_timestamp(end_date)
            
            # Buscar mensagens da API
            raw_messages = self.evolution_client.get_group_messages(
                group_id=group_id,
                timestamp_start=start_timestamp,
                timestamp_end=end_timestamp,
                limit=limit
            )
            
            # Processar mensagens
            messages = self.message_processor.get_messages(raw_messages)
            
            # Filtrar por timestamp mínimo
            filtered_messages = self.message_processor.filter_messages_by_timestamp(
                messages, 
                start_timestamp
            )
            
            return filtered_messages
            
        except Exception as e:
            print(f"Erro ao buscar mensagens do grupo {group_id}: {e}")
            return []
    
    def get_messages_for_summary(
        self,
        group_id: str,
        days_back: int = 1,
        include_names: bool = True,
        include_links: bool = False,
        min_messages: int = 50
    ) -> List[Message]:
        """
        Obtém mensagens formatadas para geração de resumo
        Gets formatted messages for summary generation
        
        Args:
            group_id: ID do grupo
            days_back: Quantos dias para trás buscar
            include_names: Incluir nomes dos remetentes
            include_links: Incluir mensagens com links
            min_messages: Número mínimo de mensagens
            
        Returns:
            Lista de mensagens processadas
        """
        # Calcular período
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Formatar datas
        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # Buscar mensagens
        messages = self.get_messages(group_id, start_date_str, end_date_str)
        
        # Filtrar mensagens próprias
        messages = [msg for msg in messages if not msg.from_me]
        
        # Filtrar links se necessário
        if not include_links:
            messages = [
                msg for msg in messages 
                if not self._message_contains_links(msg.get_display_text())
            ]
        
        # Verificar quantidade mínima
        if len(messages) < min_messages:
            print(f"Mensagens insuficientes: {len(messages)} < {min_messages}")
        
        return messages
    
    def format_messages_for_ai(
        self,
        messages: List[Message],
        include_names: bool = True,
        max_length: int = 10000
    ) -> str:
        """
        Formata mensagens para processamento por IA
        Formats messages for AI processing
        
        Args:
            messages: Lista de mensagens
            include_names: Incluir nomes dos remetentes
            max_length: Comprimento máximo do texto
            
        Returns:
            Texto formatado para IA
        """
        formatted_text = self.message_processor.format_messages_for_summary(
            messages, 
            include_names=include_names,
            include_links=False
        )
        
        # Truncar se necessário
        if len(formatted_text) > max_length:
            formatted_text = formatted_text[:max_length] + "\n[TEXTO TRUNCADO]"
        
        return formatted_text
    
    def get_message_statistics(self, messages: List[Message]) -> Dict[str, Any]:
        """
        Gera estatísticas das mensagens
        Generates message statistics
        
        Args:
            messages: Lista de mensagens
            
        Returns:
            Dicionário com estatísticas
        """
        if not messages:
            return {
                "total_messages": 0,
                "unique_senders": 0,
                "message_types": {},
                "time_range": None
            }
        
        # Contadores
        total_messages = len(messages)
        unique_senders = len(set(msg.get_sender_name() for msg in messages))
        
        # Tipos de mensagem
        message_types = {}
        for msg in messages:
            msg_type = msg.message_type
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        # Intervalo de tempo
        timestamps = [msg.message_timestamp for msg in messages if msg.message_timestamp > 0]
        time_range = None
        if timestamps:
            min_time = datetime.fromtimestamp(min(timestamps))
            max_time = datetime.fromtimestamp(max(timestamps))
            time_range = {
                "start": min_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end": max_time.strftime("%Y-%m-%d %H:%M:%S")
            }
        
        return {
            "total_messages": total_messages,
            "unique_senders": unique_senders,
            "message_types": message_types,
            "time_range": time_range
        }
    
    def _date_to_timestamp(self, date_str: str) -> int:
        """
        Converte string de data para timestamp
        Converts date string to timestamp
        """
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            # Tentar formato ISO
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return int(dt.timestamp())
            except ValueError:
                raise ValueError(f"Formato de data inválido: {date_str}")
    
    def _message_contains_links(self, text: str) -> bool:
        """
        Verifica se mensagem contém links
        Checks if message contains links
        """
        if not text:
            return False
        
        return "http://" in text or "https://" in text or "www." in text
