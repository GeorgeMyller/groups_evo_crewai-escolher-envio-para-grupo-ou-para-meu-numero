"""
Sistema de Logging Centralizado / Centralized Logging System

PT-BR:
Sistema de logging robusto para monitorar o funcionamento do sistema,
especialmente útil para debugging em ambiente Docker.

EN:
Robust logging system to monitor system operation,
especially useful for debugging in Docker environment.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

class WhatsAppLogger:
    """
    Logger centralizado para o sistema WhatsApp Manager
    Centralized logger for WhatsApp Manager system
    """
    
    _instances = {}
    
    def __init__(self, name: str = "whatsapp_manager", log_level: str = "INFO"):
        """
        Inicializa o logger
        Initializes the logger
        
        Args:
            name: Nome do logger
            log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Evita duplicação de handlers
        if not self.logger.handlers:
            self._setup_logger(log_level)
    
    def _setup_logger(self, log_level: str):
        """
        Configura o logger com handlers para arquivo e console
        Sets up logger with file and console handlers
        """
        # Define o nível de log
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Formato das mensagens
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo
        log_dir = self._get_log_directory()
        log_file = log_dir / f"{self.name}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler separado para tarefas agendadas
        scheduled_tasks_file = log_dir / "scheduled_tasks.log"
        self.tasks_handler = logging.FileHandler(scheduled_tasks_file, encoding='utf-8')
        self.tasks_handler.setLevel(logging.INFO)
        self.tasks_handler.setFormatter(formatter)
    
    def _get_log_directory(self) -> Path:
        """
        Determina o diretório de logs
        Determines the logs directory
        """
        # Tenta determinar o diretório raiz do projeto
        current_file = Path(__file__).resolve()
        
        # Procura pelo diretório raiz (onde está o pyproject.toml)
        project_root = current_file
        while project_root.parent != project_root:
            if (project_root / "pyproject.toml").exists():
                break
            project_root = project_root.parent
        
        # Cria diretório de logs
        log_dir = project_root / "data" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        return log_dir
    
    def log_task_execution(self, task_name: str, group_id: str, status: str, message: str):
        """
        Log específico para execução de tarefas agendadas
        Specific log for scheduled task execution
        """
        task_logger = logging.getLogger(f"{self.name}.tasks")
        task_logger.addHandler(self.tasks_handler)
        
        log_message = f"[TASK:{task_name}] [GROUP:{group_id}] [STATUS:{status}] {message}"
        task_logger.info(log_message)
    
    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log de informação"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Log de erro"""
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, exc_info: bool = False):
        """Log crítico"""
        self.logger.critical(message, exc_info=exc_info)
    
    @classmethod
    def get_logger(cls, name: str = "whatsapp_manager", log_level: str = "INFO") -> "WhatsAppLogger":
        """
        Singleton pattern para obter instância do logger
        Singleton pattern to get logger instance
        """
        if name not in cls._instances:
            cls._instances[name] = cls(name, log_level)
        return cls._instances[name]


class TaskExecutionMonitor:
    """
    Monitor específico para execução de tarefas agendadas
    Specific monitor for scheduled task execution
    """
    
    def __init__(self):
        self.logger = WhatsAppLogger.get_logger("task_monitor")
    
    def log_task_start(self, task_name: str, group_id: str):
        """Log do início da execução da tarefa"""
        self.logger.log_task_execution(
            task_name, group_id, "START", 
            f"Iniciando execução da tarefa agendada"
        )
    
    def log_task_success(self, task_name: str, group_id: str, message_count: int):
        """Log de sucesso da tarefa"""
        self.logger.log_task_execution(
            task_name, group_id, "SUCCESS",
            f"Tarefa executada com sucesso. {message_count} mensagens processadas"
        )
    
    def log_task_error(self, task_name: str, group_id: str, error: str):
        """Log de erro da tarefa"""
        self.logger.log_task_execution(
            task_name, group_id, "ERROR",
            f"Erro na execução: {error}"
        )
    
    def log_task_skipped(self, task_name: str, group_id: str, reason: str):
        """Log quando tarefa é pulada"""
        self.logger.log_task_execution(
            task_name, group_id, "SKIPPED",
            f"Tarefa pulada: {reason}"
        )
    
    def log_environment_info(self):
        """Log das informações do ambiente"""
        env_info = {
            "WHATSAPP_NUMBER": os.getenv("WHATSAPP_NUMBER", "Não definido"),
            "EVO_BASE_URL": os.getenv("EVO_BASE_URL", "Não definido"),
            "EVO_INSTANCE_NAME": os.getenv("EVO_INSTANCE_NAME", "Não definido"),
            "PYTHONPATH": os.getenv("PYTHONPATH", "Não definido"),
            "WORKING_DIR": os.getcwd(),
            "PYTHON_VERSION": sys.version,
            "IS_DOCKER": os.path.exists("/.dockerenv")
        }
        
        self.logger.info("=== INFORMAÇÕES DO AMBIENTE ===")
        for key, value in env_info.items():
            self.logger.info(f"{key}: {value}")
        self.logger.info("================================")


def get_logger(name: str = "whatsapp_manager", log_level: str = "INFO") -> WhatsAppLogger:
    """
    Função de conveniência para obter o logger
    Convenience function to get logger
    """
    return WhatsAppLogger.get_logger(name, log_level)
