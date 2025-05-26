"""
Configuração principal do sistema com suporte a escalabilidade.
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class RedisConfig:
    """Configuração do Redis."""
    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.password = os.getenv("REDIS_PASSWORD")
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.enabled = os.getenv("REDIS_ENABLED", "true").lower() == "true"
        
        # TTL padrão para diferentes tipos de cache
        self.groups_ttl = int(os.getenv("REDIS_GROUPS_TTL", "3600"))  # 1 hora
        self.messages_ttl = int(os.getenv("REDIS_MESSAGES_TTL", "1800"))  # 30 min
        self.summaries_ttl = int(os.getenv("REDIS_SUMMARIES_TTL", "7200"))  # 2 horas

class MetricsConfig:
    """Configuração de métricas e monitoramento."""
    def __init__(self):
        self.enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        self.port = int(os.getenv("METRICS_PORT", "8000"))
        self.collection_interval = int(os.getenv("METRICS_COLLECTION_INTERVAL", "30"))
    
class BackupConfig:
    """Configuração de backup."""
    def __init__(self):
        self.enabled = os.getenv("BACKUP_ENABLED", "true").lower() == "true"
        self.retention_days = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
        self.compression = os.getenv("BACKUP_COMPRESSION", "true").lower() == "true"
        self.schedule = os.getenv("BACKUP_SCHEDULE", "daily")
        self.backup_dir = os.getenv("BACKUP_DIR", "./backups")

class AppConfig:
    """Configuração principal da aplicação."""
    def __init__(self):
        # Configurações existentes do WhatsApp
        self.evo_api_token = os.getenv("EVO_API_TOKEN", "")
        self.evo_instance_token = os.getenv("EVO_INSTANCE_TOKEN", "")
        self.evo_instance_name = os.getenv("EVO_INSTANCE_NAME", "")
        self.evo_base_url = os.getenv("EVO_BASE_URL", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.whatsapp_number = os.getenv("WHATSAPP_NUMBER", "")
        self.number = os.getenv("NUMBER", "")
        
        # Configurações de escalabilidade
        self.redis = RedisConfig()
        self.metrics = MetricsConfig()
        self.backup = BackupConfig()
        
        # Configurações gerais
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

# Instância global da configuração
config = AppConfig()
