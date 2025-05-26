"""
Sistema de Configuração Centralizada / Centralized Configuration System

PT-BR:
Sistema de configuração usando Pydantic v2.x para validação robusta
de configurações da aplicação com suporte a variáveis de ambiente.

EN:
Configuration system using Pydantic v2.x for robust validation
of application settings with environment variable support.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from typing import Optional, List, Dict, Any
import re
from pathlib import Path


class Settings(BaseSettings):
    """
    PT-BR:
    Configurações centralizadas da aplicação com validação Pydantic.
    Suporta carregamento de variáveis de ambiente e arquivo .env.
    
    EN:
    Centralized application settings with Pydantic validation.
    Supports loading from environment variables and .env file.
    """
    
    # =============================================================================
    # CONFIGURAÇÕES GERAIS / GENERAL SETTINGS
    # =============================================================================
    
    app_name: str = Field(default="WhatsApp Group Manager", description="Application name")
    app_version: str = Field(default="2.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development/production)")
    
    # =============================================================================
    # EVOLUTION API SETTINGS
    # =============================================================================
    
    evolution_api_url: str = Field(default="http://localhost:8080", description="Evolution API base URL")
    evolution_api_key: str = Field(default="test-key", description="Evolution API key")
    evolution_instance_name: str = Field(default="test-instance", description="Evolution API instance name")
    evolution_timeout: int = Field(default=30, ge=5, le=300, description="Evolution API timeout in seconds")
    
    @field_validator('evolution_api_url')
    @classmethod
    def validate_evolution_url(cls, v: str) -> str:
        """
        PT-BR: Valida URL da Evolution API
        EN: Validates Evolution API URL
        """
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Evolution API URL must start with http:// or https://')
        if v.endswith('/'):
            v = v.rstrip('/')
        return v
    
    # =============================================================================
    # WHATSAPP SETTINGS
    # =============================================================================
    
    whatsapp_phone_number: str = Field(default="5511999999999", description="WhatsApp phone number")
    whatsapp_session_name: str = Field(default="main", description="WhatsApp session name")
    whatsapp_auto_reconnect: bool = Field(default=True, description="Auto reconnect WhatsApp")
    whatsapp_message_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between messages in seconds")
    
    @field_validator('whatsapp_phone_number')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        """
        PT-BR: Valida número de telefone WhatsApp
        EN: Validates WhatsApp phone number
        """
        # Remove caracteres não numéricos
        phone = re.sub(r'[^\d]', '', v)
        
        # Verifica se tem pelo menos 10 dígitos
        if len(phone) < 10:
            raise ValueError('Phone number must have at least 10 digits')
        
        # Adiciona código do país se não tiver
        if not phone.startswith('55'):  # Brasil
            phone = '55' + phone
        
        return phone
    
    # =============================================================================
    # CONFIGURAÇÕES DE RESUMO / SUMMARY SETTINGS
    # =============================================================================
    
    summary_default_hours: int = Field(default=24, ge=1, le=168, description="Default hours for summary")
    summary_max_messages: int = Field(default=1000, ge=10, le=10000, description="Maximum messages to process")
    summary_auto_schedule: bool = Field(default=True, description="Auto schedule summaries")
    summary_schedule_time: str = Field(default="09:00", description="Daily summary schedule time (HH:MM)")
    summary_language: str = Field(default="pt", description="Summary language (pt/en)")
    
    @field_validator('summary_schedule_time')
    @classmethod
    def validate_schedule_time(cls, v: str) -> str:
        """
        PT-BR: Valida formato de horário de agendamento
        EN: Validates schedule time format
        """
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Schedule time must be in HH:MM format (24h)')
        return v
    
    @field_validator('summary_language')
    @classmethod
    def validate_language(cls, v: str) -> str:
        """
        PT-BR: Valida código de idioma
        EN: Validates language code
        """
        valid_languages = ['pt', 'en', 'es', 'fr']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of: {valid_languages}')
        return v
    
    # =============================================================================
    # CONFIGURAÇÕES DE IA / AI SETTINGS
    # =============================================================================
    
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_model: str = Field(default="gpt-3.5-turbo", description="OpenAI model to use")
    openai_temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="OpenAI temperature")
    openai_max_tokens: int = Field(default=1000, ge=50, le=4000, description="OpenAI max tokens")
    
    # CrewAI Settings
    crewai_enabled: bool = Field(default=True, description="Enable CrewAI for summaries")
    crewai_max_iterations: int = Field(default=3, ge=1, le=10, description="CrewAI max iterations")
    crewai_verbose: bool = Field(default=False, description="CrewAI verbose mode")
    
    # =============================================================================
    # CONFIGURAÇÕES DE CACHE / CACHE SETTINGS
    # =============================================================================
    
    cache_enabled: bool = Field(default=True, description="Enable caching")
    cache_ttl_seconds: int = Field(default=3600, ge=60, le=86400, description="Cache TTL in seconds")
    cache_max_size: int = Field(default=1000, ge=10, le=10000, description="Maximum cache entries")
    cache_type: str = Field(default="memory", description="Cache type (memory/redis)")
    
    # Redis Cache Settings (se usando Redis)
    redis_url: Optional[str] = Field(None, description="Redis URL for caching")
    redis_password: Optional[str] = Field(None, description="Redis password")
    redis_db: int = Field(default=0, ge=0, le=15, description="Redis database number")
    
    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: Optional[str]) -> Optional[str]:
        """
        PT-BR: Valida URL do Redis
        EN: Validates Redis URL
        """
        if v and not v.startswith('redis://'):
            raise ValueError('Redis URL must start with redis://')
        return v
    
    # =============================================================================
    # CONFIGURAÇÕES DE LOGGING / LOGGING SETTINGS
    # =============================================================================
    
    log_level: str = Field(default="INFO", description="Log level")
    log_file: Optional[str] = Field(None, description="Log file path")
    log_max_size: str = Field(default="10MB", description="Maximum log file size")
    log_backup_count: int = Field(default=5, ge=1, le=20, description="Number of log backup files")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """
        PT-BR: Valida nível de log
        EN: Validates log level
        """
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v = v.upper()
        if v not in valid_levels:
            raise ValueError(f'Log level must be one of: {valid_levels}')
        return v
    
    # =============================================================================
    # CONFIGURAÇÕES DE BANCO DE DADOS / DATABASE SETTINGS
    # =============================================================================
    
    database_url: Optional[str] = Field(None, description="Database URL")
    database_pool_size: int = Field(default=5, ge=1, le=50, description="Database connection pool size")
    database_timeout: int = Field(default=30, ge=5, le=300, description="Database timeout in seconds")
    
    # =============================================================================
    # CONFIGURAÇÕES DE ARQUIVO / FILE SETTINGS
    # =============================================================================
    
    data_directory: str = Field(default="./data", description="Data directory path")
    backup_directory: str = Field(default="./backup", description="Backup directory path")
    export_directory: str = Field(default="./exports", description="Export directory path")
    max_file_size_mb: int = Field(default=50, ge=1, le=500, description="Maximum file size in MB")
    
    # =============================================================================
    # CONFIGURAÇÕES DE SEGURANÇA / SECURITY SETTINGS
    # =============================================================================
    
    secret_key: str = Field(default="your-secret-key-must-be-at-least-32-characters-long-for-security", description="Secret key for encryption")
    jwt_secret: Optional[str] = Field(None, description="JWT secret key")
    jwt_expire_hours: int = Field(default=24, ge=1, le=168, description="JWT expiration in hours")
    api_rate_limit: int = Field(default=100, ge=10, le=1000, description="API rate limit per minute")
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        PT-BR: Valida chave secreta
        EN: Validates secret key
        """
        if len(v) < 32:
            raise ValueError('Secret key must be at least 32 characters long')
        return v
    
    # =============================================================================
    # CONFIGURAÇÕES DE INTERFACE / UI SETTINGS
    # =============================================================================
    
    ui_theme: str = Field(default="light", description="UI theme (light/dark)")
    ui_language: str = Field(default="pt", description="UI language")
    ui_page_size: int = Field(default=20, ge=5, le=100, description="UI pagination size")
    ui_refresh_interval: int = Field(default=30, ge=5, le=300, description="UI auto-refresh interval in seconds")
    
    @field_validator('ui_theme')
    @classmethod
    def validate_ui_theme(cls, v: str) -> str:
        """
        PT-BR: Valida tema da interface
        EN: Validates UI theme
        """
        valid_themes = ['light', 'dark', 'auto']
        if v not in valid_themes:
            raise ValueError(f'UI theme must be one of: {valid_themes}')
        return v
    
    # =============================================================================
    # MÉTODOS AUXILIARES / HELPER METHODS
    # =============================================================================
    
    def get_data_path(self, filename: str) -> Path:
        """
        PT-BR: Retorna caminho completo para arquivo de dados
        EN: Returns full path for data file
        """
        return Path(self.data_directory) / filename
    
    def get_backup_path(self, filename: str) -> Path:
        """
        PT-BR: Retorna caminho completo para arquivo de backup
        EN: Returns full path for backup file
        """
        return Path(self.backup_directory) / filename
    
    def get_export_path(self, filename: str) -> Path:
        """
        PT-BR: Retorna caminho completo para arquivo de exportação
        EN: Returns full path for export file
        """
        return Path(self.export_directory) / filename
    
    def is_production(self) -> bool:
        """
        PT-BR: Verifica se está em ambiente de produção
        EN: Checks if in production environment
        """
        return self.environment.lower() == "production"
    
    def is_development(self) -> bool:
        """
        PT-BR: Verifica se está em ambiente de desenvolvimento
        EN: Checks if in development environment
        """
        return self.environment.lower() == "development"
    
    def get_evolution_headers(self) -> Dict[str, str]:
        """
        PT-BR: Retorna headers para Evolution API
        EN: Returns headers for Evolution API
        """
        return {
            'Content-Type': 'application/json',
            'apikey': self.evolution_api_key
        }
    
    def get_whatsapp_webhook_url(self) -> str:
        """
        PT-BR: Retorna URL do webhook do WhatsApp
        EN: Returns WhatsApp webhook URL
        """
        return f"{self.evolution_api_url}/webhook/{self.evolution_instance_name}"
    
    class Config:
        """Configuração do Pydantic"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignora campos extras do .env


# Instância global das configurações / Global settings instance
settings = None

# Export para importação simplificada / Export for simplified import
__all__ = ['Settings', 'settings']
