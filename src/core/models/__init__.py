"""
Modelos de Dados Pydantic / Pydantic Data Models

PT-BR:
Este módulo contém todos os modelos de dados usando Pydantic v2.x
para validação robusta de tipos e valores.

EN:
This module contains all data models using Pydantic v2.x
for robust type and value validation.
"""

from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
import re


class GroupStatus(str, Enum):
    """Status do grupo / Group status"""
    ACTIVE = "active"
    INACTIVE = "inactive" 
    ARCHIVED = "archived"
    ERROR = "error"


class MessageType(str, Enum):
    """Tipo de mensagem / Message type"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    STICKER = "sticker"
    LOCATION = "location"
    OTHER = "other"


class Group(BaseModel):
    """
    PT-BR:
    Modelo Pydantic para representar um grupo do WhatsApp.
    Validação robusta de dados com Pydantic v2.x.
    
    EN:
    Pydantic model to represent a WhatsApp group.
    Robust data validation with Pydantic v2.x.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    # Identificação / Identification
    id: str = Field(..., description="Group ID (formato: numero@g.us)")
    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    
    # Status e metadados / Status and metadata
    status: GroupStatus = Field(default=GroupStatus.ACTIVE, description="Group status")
    description: Optional[str] = Field(None, max_length=500, description="Group description")
    
    # Dados de resumo / Summary data
    last_summary: Optional[str] = Field(None, description="Last generated summary")
    last_summary_date: Optional[datetime] = Field(None, description="Last summary generation date")
    
    # Estatísticas / Statistics
    total_messages: int = Field(default=0, ge=0, description="Total message count")
    total_participants: int = Field(default=0, ge=0, description="Total participant count")
    
    # Configurações / Settings
    auto_summary_enabled: bool = Field(default=True, description="Auto summary enabled")
    summary_frequency_hours: int = Field(default=24, ge=1, le=168, description="Summary frequency in hours")
    
    # Metadados de sistema / System metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @field_validator('id')
    @classmethod
    def validate_group_id(cls, v: str) -> str:
        """
        PT-BR: Valida formato do ID do grupo WhatsApp
        EN: Validates WhatsApp group ID format
        """
        if not v.endswith('@g.us'):
            raise ValueError('Group ID must end with @g.us')
        
        # Verifica se tem o formato número@g.us
        if not re.match(r'^\d+@g\.us$', v):
            raise ValueError('Group ID must be in format: number@g.us')
        
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        PT-BR: Valida nome do grupo
        EN: Validates group name
        """
        if not v.strip():
            raise ValueError('Group name cannot be empty')
        return v.strip()
    
    @computed_field
    @property
    def display_name(self) -> str:
        """
        PT-BR: Nome de exibição formatado
        EN: Formatted display name
        """
        return f"{self.name} ({self.total_participants} membros)"
    
    @computed_field
    @property
    def is_recently_updated(self) -> bool:
        """
        PT-BR: Verifica se foi atualizado recentemente (últimas 24h)
        EN: Checks if recently updated (last 24h)
        """
        if not self.last_summary_date:
            return False
        return (datetime.now() - self.last_summary_date).total_seconds() < 86400
    
    def to_legacy_dict(self) -> Dict[str, Any]:
        """
        PT-BR: Converte para formato de dicionário legado para compatibilidade
        EN: Converts to legacy dictionary format for compatibility
        """
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'description': self.description,
            'last_summary': self.last_summary,
            'last_summary_date': self.last_summary_date.isoformat() if self.last_summary_date else None,
            'total_messages': self.total_messages,
            'total_participants': self.total_participants,
            'auto_summary_enabled': self.auto_summary_enabled,
            'summary_frequency_hours': self.summary_frequency_hours,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @classmethod
    def from_legacy_dict(cls, data: Dict[str, Any]) -> 'Group':
        """
        PT-BR: Cria instância a partir de dicionário legado
        EN: Creates instance from legacy dictionary
        """
        # Converte strings de data para datetime
        if isinstance(data.get('last_summary_date'), str):
            data['last_summary_date'] = datetime.fromisoformat(data['last_summary_date'])
        if isinstance(data.get('created_at'), str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if isinstance(data.get('updated_at'), str):
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        return cls(**data)


class MessageData(BaseModel):
    """
    PT-BR:
    Modelo para dados de mensagem do WhatsApp.
    
    EN:
    Model for WhatsApp message data.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    id: str = Field(..., description="Message ID")
    group_id: str = Field(..., description="Group ID")
    sender: str = Field(..., description="Sender phone number")
    content: str = Field(..., description="Message content")
    message_type: MessageType = Field(default=MessageType.TEXT, description="Message type")
    timestamp: datetime = Field(..., description="Message timestamp")
    
    @field_validator('group_id')
    @classmethod
    def validate_group_id(cls, v: str) -> str:
        """Valida formato do ID do grupo"""
        if not v.endswith('@g.us'):
            raise ValueError('Group ID must end with @g.us')
        return v


class GroupStats(BaseModel):
    """
    PT-BR:
    Estatísticas detalhadas de um grupo.
    
    EN:
    Detailed group statistics.
    """
    
    group_id: str = Field(..., description="Group ID")
    total_messages: int = Field(default=0, ge=0, description="Total messages")
    messages_today: int = Field(default=0, ge=0, description="Messages today")
    active_participants: int = Field(default=0, ge=0, description="Active participants")
    most_active_hour: Optional[int] = Field(None, ge=0, le=23, description="Most active hour")
    message_types: Dict[MessageType, int] = Field(default_factory=dict, description="Message type distribution")
    
    @field_validator('group_id')
    @classmethod
    def validate_group_id(cls, v: str) -> str:
        """Valida formato do ID do grupo"""
        if not v.endswith('@g.us'):
            raise ValueError('Group ID must end with @g.us')
        return v


class SummaryRequest(BaseModel):
    """
    PT-BR:
    Modelo para requisição de resumo.
    
    EN:
    Model for summary request.
    """
    
    group_id: str = Field(..., description="Group ID")
    hours_back: int = Field(default=24, ge=1, le=168, description="Hours to look back")
    include_media: bool = Field(default=False, description="Include media in summary")
    language: str = Field(default="pt", pattern=r'^[a-z]{2}$', description="Summary language")
    
    @field_validator('group_id')
    @classmethod
    def validate_group_id(cls, v: str) -> str:
        """Valida formato do ID do grupo"""
        if not v.endswith('@g.us'):
            raise ValueError('Group ID must end with @g.us')
        return v


class SummaryResult(BaseModel):
    """
    PT-BR:
    Resultado do resumo gerado.
    
    EN:
    Generated summary result.
    """
    
    group_id: str = Field(..., description="Group ID")
    summary: str = Field(..., description="Generated summary")
    generated_at: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    message_count: int = Field(default=0, ge=0, description="Number of messages summarized")
    hours_covered: int = Field(default=0, ge=0, description="Hours of messages covered")
    success: bool = Field(default=True, description="Summary generation success")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    @field_validator('group_id')
    @classmethod
    def validate_group_id(cls, v: str) -> str:
        """Valida formato do ID do grupo"""
        if not v.endswith('@g.us'):
            raise ValueError('Group ID must end with @g.us')
        return v


class APIResponse(BaseModel):
    """
    PT-BR:
    Modelo padrão para respostas da API.
    
    EN:
    Standard model for API responses.
    """
    
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error_code: Optional[str] = Field(None, description="Error code if failed")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


# Exports para importação simplificada / Exports for simplified import
__all__ = [
    'Group',
    'GroupStatus', 
    'MessageType',
    'MessageData',
    'GroupStats',
    'SummaryRequest',
    'SummaryResult',
    'APIResponse'
]
