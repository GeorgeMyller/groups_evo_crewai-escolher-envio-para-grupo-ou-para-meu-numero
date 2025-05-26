"""
Sistema de Validação Robusto / Robust Validation System

PT-BR:
Fornece validadores customizados para dados de entrada, configurações
e parâmetros do sistema, garantindo integridade e consistência.

EN:
Provides custom validators for input data, configurations and system
parameters, ensuring integrity and consistency.
"""

import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, time, date
from pathlib import Path
from pydantic import validator, ValidationError


class ValidationError(Exception):
    """Exceção customizada para erros de validação"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(self.message)


class DataValidator:
    """Validadores de dados do sistema"""
    
    @staticmethod
    def validate_whatsapp_id(value: str) -> str:
        """Valida formato de ID do WhatsApp"""
        if not value:
            raise ValidationError("ID do WhatsApp não pode estar vazio", "whatsapp_id", value)
        
        # Padrão para grupos: números@g.us
        group_pattern = r'^\d+@g\.us$'
        # Padrão para contatos: números@s.whatsapp.net
        contact_pattern = r'^\d+@s\.whatsapp\.net$'
        
        if not (re.match(group_pattern, value) or re.match(contact_pattern, value)):
            raise ValidationError(
                "Formato de ID do WhatsApp inválido. Deve ser número@g.us ou número@s.whatsapp.net",
                "whatsapp_id", 
                value
            )
        
        return value
    
    @staticmethod
    def validate_time_format(value: str) -> str:
        """Valida formato de horário HH:MM"""
        if not value:
            raise ValidationError("Horário não pode estar vazio", "time", value)
        
        time_pattern = r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$'
        if not re.match(time_pattern, value):
            raise ValidationError(
                "Formato de horário inválido. Use HH:MM (ex: 14:30)",
                "time",
                value
            )
        
        return value
    
    @staticmethod
    def validate_date_format(value: str) -> str:
        """Valida formato de data YYYY-MM-DD"""
        if not value:
            raise ValidationError("Data não pode estar vazia", "date", value)
        
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, value):
            raise ValidationError(
                "Formato de data inválido. Use YYYY-MM-DD (ex: 2025-12-31)",
                "date",
                value
            )
        
        # Validar se é uma data válida
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            raise ValidationError(
                "Data inválida. Verifique se o dia/mês existem",
                "date",
                value
            )
        
        return value
    
    @staticmethod
    def validate_url(value: str) -> str:
        """Valida formato de URL"""
        if not value:
            raise ValidationError("URL não pode estar vazia", "url", value)
        
        url_pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        if not re.match(url_pattern, value):
            raise ValidationError(
                "Formato de URL inválido. Deve começar com http:// ou https://",
                "url",
                value
            )
        
        return value.rstrip('/')
    
    @staticmethod
    def validate_positive_integer(value: int, min_value: int = 1, max_value: Optional[int] = None) -> int:
        """Valida número inteiro positivo"""
        if not isinstance(value, int):
            raise ValidationError(
                "Valor deve ser um número inteiro",
                "positive_integer",
                value
            )
        
        if value < min_value:
            raise ValidationError(
                f"Valor deve ser maior ou igual a {min_value}",
                "positive_integer",
                value
            )
        
        if max_value and value > max_value:
            raise ValidationError(
                f"Valor deve ser menor ou igual a {max_value}",
                "positive_integer",
                value
            )
        
        return value
    
    @staticmethod
    def validate_file_path(value: str, must_exist: bool = False, create_if_missing: bool = False) -> str:
        """Valida caminho de arquivo"""
        if not value:
            raise ValidationError("Caminho do arquivo não pode estar vazio", "file_path", value)
        
        path = Path(value)
        
        if must_exist and not path.exists():
            raise ValidationError(
                f"Arquivo não encontrado: {value}",
                "file_path",
                value
            )
        
        if create_if_missing and not path.exists():
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            except Exception as e:
                raise ValidationError(
                    f"Não foi possível criar arquivo: {e}",
                    "file_path",
                    value
                )
        
        return str(path.absolute())
    
    @staticmethod
    def validate_environment_variables(required_vars: List[str]) -> Dict[str, str]:
        """Valida variáveis de ambiente obrigatórias"""
        import os
        missing_vars = []
        env_vars = {}
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                env_vars[var] = value
        
        if missing_vars:
            raise ValidationError(
                f"Variáveis de ambiente obrigatórias não encontradas: {', '.join(missing_vars)}",
                "environment_variables",
                missing_vars
            )
        
        return env_vars
    
    @staticmethod
    def validate_group_name(value: str) -> str:
        """Valida nome do grupo"""
        if not value or not value.strip():
            raise ValidationError("Nome do grupo não pode estar vazio", "group_name", value)
        
        # Remove caracteres perigosos
        cleaned_name = re.sub(r'[<>:"/\\|?*]', '', value.strip())
        
        if len(cleaned_name) > 100:
            raise ValidationError(
                "Nome do grupo não pode ter mais de 100 caracteres",
                "group_name",
                value
            )
        
        return cleaned_name
    
    @staticmethod
    def validate_message_content(value: str) -> str:
        """Valida conteúdo de mensagem"""
        if not value:
            return ""
        
        # Remove caracteres de controle
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
        
        # Limita tamanho
        if len(cleaned) > 10000:
            cleaned = cleaned[:10000] + "..."
        
        return cleaned.strip()


class ConfigValidator:
    """Validador específico para configurações"""
    
    @staticmethod
    def validate_summary_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida configuração de resumo"""
        validator = DataValidator()
        
        # Validações obrigatórias
        if 'group_id' in config:
            config['group_id'] = validator.validate_whatsapp_id(config['group_id'])
        
        if 'schedule_time' in config:
            config['schedule_time'] = validator.validate_time_format(config['schedule_time'])
        
        if 'min_messages' in config:
            config['min_messages'] = validator.validate_positive_integer(
                config['min_messages'], 
                min_value=1, 
                max_value=1000
            )
        
        # Validações condicionais
        if config.get('schedule_type') == 'once':
            required_fields = ['start_date', 'start_time', 'end_date', 'end_time']
            for field in required_fields:
                if field not in config or not config[field]:
                    raise ValidationError(
                        f"Campo '{field}' é obrigatório para agendamento único",
                        field,
                        config.get(field)
                    )
                
                if 'date' in field:
                    config[field] = validator.validate_date_format(config[field])
                else:
                    config[field] = validator.validate_time_format(config[field])
        
        return config
    
    @staticmethod
    def validate_api_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida configuração da API"""
        validator = DataValidator()
        
        required_fields = ['base_url', 'api_token', 'instance_name', 'instance_token']
        for field in required_fields:
            if field not in config or not config[field]:
                raise ValidationError(
                    f"Campo '{field}' é obrigatório na configuração da API",
                    field,
                    config.get(field)
                )
        
        config['base_url'] = validator.validate_url(config['base_url'])
        
        return config


def validate_system_requirements() -> List[str]:
    """Valida requisitos do sistema e retorna lista de problemas"""
    problems = []
    
    # Validar variáveis de ambiente
    try:
        DataValidator.validate_environment_variables([
            'EVO_API_TOKEN',
            'EVO_INSTANCE_NAME', 
            'EVO_INSTANCE_TOKEN'
        ])
    except ValidationError as e:
        problems.append(f"Configuração: {e.message}")
    
    # Validar diretórios necessários
    required_dirs = ['data', 'logs', 'config']
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                problems.append(f"Não foi possível criar diretório {dir_name}: {e}")
    
    return problems
