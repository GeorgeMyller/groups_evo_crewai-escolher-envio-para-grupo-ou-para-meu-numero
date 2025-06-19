"""
Constantes da Aplicação / Application Constants

PT-BR:
Define todas as constantes utilizadas no sistema.

EN:
Defines all constants used in the system.
"""


class AppConstants:
    """
    Constantes principais da aplicação
    Main application constants
    """
    
    # Configurações da API / API Settings
    DEFAULT_API_URL = "http://localhost:8081"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAYS = [60, 120, 300]  # Segundos
    
    # Configurações de Cache / Cache Settings
    CACHE_TIMEOUT = 300  # 5 minutos
    CACHE_DIR = "data/cache"
    
    # Configurações de Mensagens / Message Settings
    MAX_MESSAGE_LENGTH = 4096
    DEFAULT_MIN_MESSAGES = 50
    MAX_MESSAGES_PER_REQUEST = 1000
    
    # Tipos de Mensagem / Message Types
    MESSAGE_TYPE_TEXT = "conversation"
    MESSAGE_TYPE_EXTENDED_TEXT = "extendedTextMessage"
    MESSAGE_TYPE_AUDIO = "audioMessage"
    MESSAGE_TYPE_IMAGE = "imageMessage"
    MESSAGE_TYPE_DOCUMENT = "documentMessage"
    MESSAGE_TYPE_VIDEO = "videoMessage"
    
    # Identificadores WhatsApp / WhatsApp Identifiers
    GROUP_SUFFIX = "@g.us"
    CONTACT_SUFFIX = "@s.whatsapp.net"
    
    # Configurações de Resumo / Summary Settings
    DEFAULT_SUMMARY_TIME = "22:00"
    DEFAULT_SUMMARY_DAYS = 1
    MIN_SUMMARY_LENGTH = 100
    MAX_SUMMARY_LENGTH = 2000
    
    # Estados de Conexão / Connection States
    CONNECTION_STATE_OPEN = "open"
    CONNECTION_STATE_CONNECTING = "connecting"
    CONNECTION_STATE_CLOSE = "close"
    
    # Configurações de Agendamento / Scheduling Settings
    TASK_PREFIX = "ResumoGrupo_"
    SCHEDULER_CHECK_INTERVAL = 60  # Segundos
    
    # Formatos de Data / Date Formats
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M"
    ISO_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
    
    # Configurações de Log / Log Settings
    LOG_FORMAT = "[{timestamp}] [{level}] [{context}] - {message}"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # Configurações de Arquivo / File Settings
    CSV_ENCODING = "utf-8"
    JSON_ENCODING = "utf-8"
    
    # Limites do Sistema / System Limits
    MAX_GROUPS_PER_INSTANCE = 256
    MAX_CONCURRENT_OPERATIONS = 5
    
    # Configurações de UI / UI Settings
    STREAMLIT_PAGE_TITLE = "WhatsApp Group Resumer"
    STREAMLIT_LAYOUT = "wide"
    
    # Emojis para Interface / Interface Emojis
    EMOJI_SUCCESS = "✅"
    EMOJI_ERROR = "❌"
    EMOJI_WARNING = "⚠️"
    EMOJI_INFO = "ℹ️"
    EMOJI_LOADING = "🔄"
    EMOJI_GROUP = "👥"
    EMOJI_MESSAGE = "💬"
    EMOJI_SUMMARY = "📋"
    EMOJI_SCHEDULE = "📅"
    EMOJI_SETTINGS = "⚙️"


class ErrorMessages:
    """
    Mensagens de erro padronizadas
    Standardized error messages
    """
    
    # Erros de Configuração / Configuration Errors
    MISSING_ENV_VARS = "Variáveis de ambiente obrigatórias não encontradas"
    INVALID_API_CONFIG = "Configuração da API inválida"
    
    # Erros de Conexão / Connection Errors
    API_CONNECTION_FAILED = "Falha na conexão com a API"
    WHATSAPP_NOT_CONNECTED = "WhatsApp não está conectado"
    RATE_LIMIT_EXCEEDED = "Limite de requisições excedido"
    
    # Erros de Dados / Data Errors
    GROUP_NOT_FOUND = "Grupo não encontrado"
    INVALID_GROUP_ID = "ID do grupo inválido"
    INSUFFICIENT_MESSAGES = "Mensagens insuficientes para gerar resumo"
    
    # Erros de Arquivo / File Errors
    FILE_NOT_FOUND = "Arquivo não encontrado"
    FILE_PERMISSION_DENIED = "Permissão negada para acessar arquivo"
    INVALID_FILE_FORMAT = "Formato de arquivo inválido"
    
    # Erros de Processamento / Processing Errors
    SUMMARY_GENERATION_FAILED = "Falha na geração do resumo"
    MESSAGE_SEND_FAILED = "Falha no envio da mensagem"
    SCHEDULE_CREATE_FAILED = "Falha na criação do agendamento"


class SuccessMessages:
    """
    Mensagens de sucesso padronizadas
    Standardized success messages
    """
    
    GROUPS_LOADED = "Grupos carregados com sucesso"
    SUMMARY_GENERATED = "Resumo gerado com sucesso"
    MESSAGE_SENT = "Mensagem enviada com sucesso"
    SETTINGS_SAVED = "Configurações salvas com sucesso"
    SCHEDULE_CREATED = "Agendamento criado com sucesso"
    SCHEDULE_DELETED = "Agendamento removido com sucesso"


class InfoMessages:
    """
    Mensagens informativas padronizadas
    Standardized info messages
    """
    
    OFFLINE_MODE = "Modo offline ativo - Trabalhando com dados locais"
    ONLINE_MODE = "Modo online ativo - Conectado à API"
    LOADING_GROUPS = "Carregando grupos..."
    GENERATING_SUMMARY = "Gerando resumo..."
    SENDING_MESSAGE = "Enviando mensagem..."
