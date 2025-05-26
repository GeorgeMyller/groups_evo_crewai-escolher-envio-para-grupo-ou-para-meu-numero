"""
Exceções customizadas para o sistema / Custom exceptions for the system
"""
from typing import Optional


class GroupSystemException(Exception):
    """Exceção base para o sistema de grupos"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class GroupNotFoundError(GroupSystemException):
    """Exceção quando grupo não é encontrado"""
    
    def __init__(self, group_id: str):
        message = f"Grupo com ID '{group_id}' não foi encontrado"
        super().__init__(message, "GROUP_NOT_FOUND")
        self.group_id = group_id


class APIConnectionError(GroupSystemException):
    """Exceção para erros de conexão com API"""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, "API_CONNECTION_ERROR")
        self.status_code = status_code


class ConfigurationError(GroupSystemException):
    """Exceção para erros de configuração"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, "CONFIGURATION_ERROR")
        self.config_key = config_key


class MessageProcessingError(GroupSystemException):
    """Exceção para erros no processamento de mensagens"""
    
    def __init__(self, message: str, group_id: Optional[str] = None):
        super().__init__(message, "MESSAGE_PROCESSING_ERROR")
        self.group_id = group_id


class SummaryGenerationError(GroupSystemException):
    """Exceção para erros na geração de resumos"""
    
    def __init__(self, message: str, group_id: Optional[str] = None):
        super().__init__(message, "SUMMARY_GENERATION_ERROR")
        self.group_id = group_id


class SchedulingError(GroupSystemException):
    """Exceção para erros de agendamento"""
    
    def __init__(self, message: str, task_name: Optional[str] = None):
        super().__init__(message, "SCHEDULING_ERROR")
        self.task_name = task_name
