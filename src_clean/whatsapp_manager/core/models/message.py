"""
Modelo de Mensagem do WhatsApp / WhatsApp Message Model

PT-BR:
Esta classe representa uma mensagem do WhatsApp com seus metadados e conteúdo.
Processa diferentes tipos de mensagens (texto, áudio, imagem, documentos).

EN:
This class represents a WhatsApp message with its metadata and content.
Processes different message types (text, audio, image, documents).
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import base64


@dataclass
class Message:
    """
    Modelo de dados para mensagem do WhatsApp
    Data model for WhatsApp message
    """
    # Identificadores únicos / Unique identifiers
    message_id: str
    remote_jid: str
    sender: Optional[str] = None
    participant: Optional[str] = None
    
    # Metadados temporais / Temporal metadata
    message_timestamp: int = 0
    date_time: Optional[str] = None
    
    # Conteúdo da mensagem / Message content
    message_type: str = "conversation"
    text_content: Optional[str] = None
    media_content: Optional[bytes] = None
    media_url: Optional[str] = None
    media_mime_type: Optional[str] = None
    
    # Informações do remetente / Sender information
    push_name: Optional[str] = None
    from_me: bool = False
    
    # Contexto da mensagem / Message context
    is_group: bool = False
    group_id: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Status / Status
    status: Optional[str] = None
    instance_id: Optional[str] = None
    
    @classmethod
    def from_evolution_data(cls, raw_data: Dict[str, Any]) -> 'Message':
        """
        Cria uma instância Message a partir dos dados da Evolution API
        Creates a Message instance from Evolution API data
        """
        if "data" not in raw_data:
            data = raw_data
        else:
            data = raw_data.get("data", {})
        
        key = data.get("key", {})
        message = data.get("message", {})
        
        # Extrair informações básicas
        msg = cls(
            message_id=key.get("id", ""),
            remote_jid=key.get("remoteJid", ""),
            sender=data.get("sender", ""),
            participant=key.get("participant"),
            message_timestamp=int(data.get("messageTimestamp", 0)),
            date_time=raw_data.get("date_time"),
            message_type=data.get("messageType", "conversation"),
            push_name=data.get("pushName"),
            from_me=key.get("fromMe", False),
            status=data.get("status"),
            instance_id=data.get("instanceId")
        )
        
        # Determinar se é grupo ou privado
        msg._determine_scope()
        
        # Extrair conteúdo específico por tipo
        msg._extract_content(message)
        
        return msg
    
    def _determine_scope(self):
        """Determina se a mensagem é de grupo ou privada"""
        if self.remote_jid and "@g.us" in self.remote_jid:
            self.is_group = True
            self.group_id = self.remote_jid
            if self.participant:
                self.phone_number = self.participant.replace("@s.whatsapp.net", "")
        else:
            self.is_group = False
            self.phone_number = self.remote_jid.replace("@s.whatsapp.net", "") if self.remote_jid else None
    
    def _extract_content(self, message: Dict[str, Any]):
        """Extrai conteúdo específico baseado no tipo da mensagem"""
        if self.message_type == "conversation":
            self.text_content = message.get("conversation", "")
        
        elif self.message_type == "extendedTextMessage":
            extended_text = message.get("extendedTextMessage", {})
            self.text_content = extended_text.get("text", "")
        
        elif self.message_type == "audioMessage":
            audio_msg = message.get("audioMessage", {})
            self.media_mime_type = audio_msg.get("mimetype")
            self.media_url = audio_msg.get("url")
            if "data" in audio_msg:
                try:
                    self.media_content = base64.b64decode(audio_msg["data"])
                except Exception:
                    pass
        
        elif self.message_type == "imageMessage":
            image_msg = message.get("imageMessage", {})
            self.media_mime_type = image_msg.get("mimetype")
            self.media_url = image_msg.get("url")
            self.text_content = image_msg.get("caption", "")
            if "data" in image_msg:
                try:
                    self.media_content = base64.b64decode(image_msg["data"])
                except Exception:
                    pass
        
        elif self.message_type == "documentMessage":
            doc_msg = message.get("documentMessage", {})
            self.media_mime_type = doc_msg.get("mimetype")
            self.media_url = doc_msg.get("url")
            self.text_content = doc_msg.get("fileName", "")
            if "data" in doc_msg:
                try:
                    self.media_content = base64.b64decode(doc_msg["data"])
                except Exception:
                    pass
    
    def get_display_text(self) -> str:
        """
        Retorna texto formatado para exibição
        Returns formatted text for display
        """
        if self.text_content:
            return self.text_content
        elif self.message_type == "audioMessage":
            return "[Áudio]"
        elif self.message_type == "imageMessage":
            return f"[Imagem]{': ' + self.text_content if self.text_content else ''}"
        elif self.message_type == "documentMessage":
            return f"[Documento: {self.text_content or 'Arquivo'}]"
        else:
            return f"[{self.message_type}]"
    
    def get_sender_name(self) -> str:
        """
        Retorna nome do remetente
        Returns sender name
        """
        if self.push_name:
            return self.push_name
        elif self.phone_number:
            return self.phone_number
        else:
            return "Desconhecido"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Converte para dicionário
        Converts to dictionary
        """
        return {
            "message_id": self.message_id,
            "remote_jid": self.remote_jid,
            "sender": self.sender,
            "participant": self.participant,
            "message_timestamp": self.message_timestamp,
            "date_time": self.date_time,
            "message_type": self.message_type,
            "text_content": self.text_content,
            "media_mime_type": self.media_mime_type,
            "media_url": self.media_url,
            "push_name": self.push_name,
            "from_me": self.from_me,
            "is_group": self.is_group,
            "group_id": self.group_id,
            "phone_number": self.phone_number,
            "status": self.status,
            "instance_id": self.instance_id,
            "display_text": self.get_display_text(),
            "sender_name": self.get_sender_name()
        }


class MessageProcessor:
    """
    Processador de mensagens do WhatsApp
    WhatsApp message processor
    """
    
    @staticmethod
    def get_messages(evolution_messages: list) -> list[Message]:
        """
        Processa lista de mensagens da Evolution API
        Processes list of messages from Evolution API
        """
        messages = []
        for msg_data in evolution_messages:
            try:
                message = Message.from_evolution_data(msg_data)
                messages.append(message)
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
                continue
        
        return messages
    
    @staticmethod
    def filter_messages_by_timestamp(messages: list[Message], min_timestamp: int) -> list[Message]:
        """
        Filtra mensagens por timestamp mínimo
        Filters messages by minimum timestamp
        """
        return [msg for msg in messages if msg.message_timestamp >= min_timestamp]
    
    @staticmethod
    def format_messages_for_summary(messages: list[Message], include_names: bool = True, include_links: bool = False) -> str:
        """
        Formata mensagens para geração de resumo
        Formats messages for summary generation
        """
        formatted_lines = []
        
        for msg in messages:
            if msg.from_me:
                continue  # Pular mensagens próprias
            
            # Nome do remetente
            sender_name = msg.get_sender_name() if include_names else "Usuário"
            
            # Conteúdo da mensagem
            content = msg.get_display_text()
            
            # Filtrar links se necessário
            if not include_links and ("http://" in content or "https://" in content):
                continue
            
            formatted_lines.append(f"{sender_name}: {content}")
        
        return "\n".join(formatted_lines)
