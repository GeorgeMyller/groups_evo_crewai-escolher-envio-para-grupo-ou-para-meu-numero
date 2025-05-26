"""
Sistema de logging estruturado / Structured logging system
"""
import logging
import sys
import os
from typing import Optional, Dict, Any
from datetime import datetime


class StructuredLogger:
    """Logger estruturado para o sistema de grupos"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        
        # Evita duplicação de handlers
        if not self.logger.handlers:
            self._setup_logger(level)
    
    def _setup_logger(self, level: str):
        """Configura o logger com formatação estruturada"""
        
        # Set level
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # File handler
        log_dir = os.path.dirname(__file__)
        log_file = os.path.join(log_dir, "system.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formatters
        console_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str, **kwargs):
        """Log info com contexto estruturado"""
        extra_info = self._format_extra(**kwargs)
        self.logger.info(f"{message} {extra_info}".strip())
    
    def error(self, message: str, **kwargs):
        """Log error com contexto estruturado"""
        extra_info = self._format_extra(**kwargs)
        self.logger.error(f"{message} {extra_info}".strip())
    
    def warning(self, message: str, **kwargs):
        """Log warning com contexto estruturado"""
        extra_info = self._format_extra(**kwargs)
        self.logger.warning(f"{message} {extra_info}".strip())
    
    def debug(self, message: str, **kwargs):
        """Log debug com contexto estruturado"""
        extra_info = self._format_extra(**kwargs)
        self.logger.debug(f"{message} {extra_info}".strip())
    
    def _format_extra(self, **kwargs) -> str:
        """Formata informações extras como string estruturada"""
        if not kwargs:
            return ""
        
        formatted_items = []
        for key, value in kwargs.items():
            formatted_items.append(f"{key}={value}")
        
        return f"| {' | '.join(formatted_items)}"


# Logger padrão para o sistema
system_logger = StructuredLogger("GroupSystem")

# Loggers específicos para cada módulo
group_controller_logger = StructuredLogger("GroupController")
summary_logger = StructuredLogger("Summary")
scheduler_logger = StructuredLogger("Scheduler")
api_logger = StructuredLogger("API")
