"""
Enviador de Mensagens / Message Sender

PT-BR:
Este serviço gerencia o envio de mensagens para WhatsApp através da Evolution API.
Fornece interface simplificada para diferentes tipos de mensagens.

EN:
This service manages sending messages to WhatsApp through Evolution API.
Provides simplified interface for different message types.
"""

from typing import Dict, Any, Optional
from ..api.evolution_client import EvolutionClientWrapper


class MessageSender:
    """
    Serviço para envio de mensagens WhatsApp
    Service for sending WhatsApp messages
    """
    
    def __init__(self, evolution_client: EvolutionClientWrapper):
        """
        Inicializa o enviador de mensagens
        Initializes the message sender
        """
        self.evolution_client = evolution_client
    
    def send_text_message(self, remote_jid: str, text: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto
        Sends text message
        
        Args:
            remote_jid: ID do destinatário (grupo ou contato)
            text: Conteúdo da mensagem
            
        Returns:
            Resultado do envio
        """
        try:
            # Validar parâmetros
            if not remote_jid or not text:
                raise ValueError("remote_jid e text são obrigatórios")
            
            # Enviar mensagem
            response = self.evolution_client.send_text_message(remote_jid, text)
            
            return {
                "success": True,
                "remote_jid": remote_jid,
                "message_length": len(text),
                "response": response
            }
            
        except Exception as e:
            error_msg = f"Erro ao enviar mensagem para {remote_jid}: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "remote_jid": remote_jid,
                "error": error_msg
            }
    
    def send_formatted_summary(
        self, 
        remote_jid: str, 
        group_name: str, 
        summary: str,
        include_header: bool = True
    ) -> Dict[str, Any]:
        """
        Envia resumo formatado
        Sends formatted summary
        
        Args:
            remote_jid: ID do destinatário
            group_name: Nome do grupo
            summary: Conteúdo do resumo
            include_header: Incluir cabeçalho formatado
            
        Returns:
            Resultado do envio
        """
        if include_header:
            formatted_message = f"📋 *Resumo do grupo {group_name}*\n\n{summary}"
        else:
            formatted_message = summary
        
        return self.send_text_message(remote_jid, formatted_message)
    
    def send_notification(
        self, 
        remote_jid: str, 
        title: str, 
        message: str,
        emoji: str = "🔔"
    ) -> Dict[str, Any]:
        """
        Envia notificação formatada
        Sends formatted notification
        
        Args:
            remote_jid: ID do destinatário
            title: Título da notificação
            message: Conteúdo da mensagem
            emoji: Emoji para o título
            
        Returns:
            Resultado do envio
        """
        formatted_message = f"{emoji} *{title}*\n\n{message}"
        return self.send_text_message(remote_jid, formatted_message)
    
    def send_error_notification(
        self, 
        remote_jid: str, 
        error_message: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia notificação de erro
        Sends error notification
        
        Args:
            remote_jid: ID do destinatário
            error_message: Mensagem de erro
            context: Contexto adicional
            
        Returns:
            Resultado do envio
        """
        title = "❌ Erro no Sistema"
        
        if context:
            full_message = f"*Contexto:* {context}\n\n*Erro:* {error_message}"
        else:
            full_message = f"*Erro:* {error_message}"
        
        return self.send_notification(remote_jid, title, full_message, "❌")
    
    def validate_remote_jid(self, remote_jid: str) -> bool:
        """
        Valida formato do remote_jid
        Validates remote_jid format
        
        Args:
            remote_jid: ID para validar
            
        Returns:
            True se válido
        """
        if not remote_jid:
            return False
        
        # Verificar se é grupo ou contato individual
        is_group = remote_jid.endswith("@g.us")
        is_contact = remote_jid.endswith("@s.whatsapp.net")
        
        return is_group or is_contact
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Formata número de telefone para remote_jid
        Formats phone number to remote_jid
        
        Args:
            phone_number: Número de telefone
            
        Returns:
            remote_jid formatado
        """
        # Remover caracteres especiais
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Adicionar sufixo do WhatsApp
        return f"{clean_number}@s.whatsapp.net"
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Obtém status da conexão
        Gets connection status
        
        Returns:
            Status da conexão
        """
        return self.evolution_client.check_connection_status()
