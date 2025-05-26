"""
Metrics and Monitoring System

PT-BR:
Sistema de métricas e monitoramento para acompanhar performance,
uso de recursos e comportamento do sistema em produção.

EN:
Metrics and monitoring system to track performance,
resource usage and system behavior in production.
"""

import time
import psutil
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from functools import wraps
from contextlib import contextmanager
import threading
from prometheus_client import (
    Counter, Histogram, Gauge, start_http_server, 
    CollectorRegistry, REGISTRY
)
import structlog
import os

logger = structlog.get_logger(__name__)


class MonitoringConfig:
    """
    PT-BR: Configurações do sistema de monitoramento
    EN: Monitoring system configuration
    """
    def __init__(self):
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
        self.metrics_port = int(os.getenv("METRICS_PORT", "8000"))
        self.metrics_host = os.getenv("METRICS_HOST", "0.0.0.0")
        self.collect_system_metrics = os.getenv("COLLECT_SYSTEM_METRICS", "true").lower() == "true"
        self.metrics_interval = int(os.getenv("METRICS_INTERVAL", "30"))  # segundos
        self.prometheus_enabled = os.getenv("PROMETHEUS_ENABLED", "false").lower() == "true"


class MetricsCollector:
    """
    PT-BR:
    Coletor de métricas usando Prometheus.
    Monitora operações do sistema, performance e uso de recursos.
    
    EN:
    Metrics collector using Prometheus.
    Monitors system operations, performance and resource usage.
    """
    
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self._registry = CollectorRegistry()
        self._server_started = False
        self._metrics_thread: Optional[threading.Thread] = None
        self._stop_metrics = threading.Event()
        
        if self.config.metrics_enabled:
            self._setup_metrics()
    
    def _setup_metrics(self):
        """
        PT-BR: Configura métricas Prometheus
        EN: Setup Prometheus metrics
        """
        # Contadores de operações
        self.operations_total = Counter(
            'whatsapp_operations_total',
            'Total number of operations performed',
            ['operation_type', 'status'],
            registry=self._registry
        )
        
        # Histogramas de tempo de resposta
        self.operation_duration = Histogram(
            'whatsapp_operation_duration_seconds',
            'Time spent on operations',
            ['operation_type'],
            registry=self._registry
        )
        
        # Gauges para métricas de sistema
        self.cpu_usage = Gauge(
            'system_cpu_usage_percent',
            'CPU usage percentage',
            registry=self._registry
        )
        
        self.memory_usage = Gauge(
            'system_memory_usage_bytes',
            'Memory usage in bytes',
            registry=self._registry
        )
        
        self.disk_usage = Gauge(
            'system_disk_usage_percent',
            'Disk usage percentage',
            registry=self._registry
        )
        
        # Métricas específicas da aplicação
        self.active_groups = Gauge(
            'whatsapp_active_groups_total',
            'Number of active WhatsApp groups',
            registry=self._registry
        )
        
        self.messages_processed = Counter(
            'whatsapp_messages_processed_total',
            'Total messages processed',
            ['group_id'],
            registry=self._registry
        )
        
        self.summaries_generated = Counter(
            'whatsapp_summaries_generated_total',
            'Total summaries generated',
            ['status'],
            registry=self._registry
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'whatsapp_cache_hits_total',
            'Total cache hits',
            ['cache_type'],
            registry=self._registry
        )
        
        self.cache_misses = Counter(
            'whatsapp_cache_misses_total',
            'Total cache misses',
            ['cache_type'],
            registry=self._registry
        )
        
        # API response times
        self.api_request_duration = Histogram(
            'whatsapp_api_request_duration_seconds',
            'Time spent on API requests',
            ['api_endpoint', 'status_code'],
            registry=self._registry
        )
        
        logger.info("Prometheus metrics initialized")
    
    def start_metrics_server(self):
        """
        PT-BR: Inicia servidor de métricas Prometheus
        EN: Start Prometheus metrics server
        """
        if not self.config.metrics_enabled or self._server_started:
            return
        
        try:
            import socket
            
            # Verificar se a porta está disponível
            original_port = self.config.metrics_port
            port_to_use = self._find_available_port(original_port)
            
            if port_to_use != original_port:
                logger.warning(
                    "Original metrics port in use, using alternative",
                    original_port=original_port,
                    alternative_port=port_to_use
                )
                self.config.metrics_port = port_to_use
            
            start_http_server(
                self.config.metrics_port,
                addr=self.config.metrics_host,
                registry=self._registry
            )
            self._server_started = True
            
            logger.info(
                "Metrics server started",
                host=self.config.metrics_host,
                port=self.config.metrics_port
            )
            
            # Iniciar coleta de métricas de sistema
            if self.config.collect_system_metrics:
                self._start_system_metrics_collection()
                
        except Exception as e:
            logger.error("Failed to start metrics server", error=str(e))
    
    def _find_available_port(self, start_port: int, max_attempts: int = 10) -> int:
        """
        PT-BR: Encontra uma porta disponível começando pela porta especificada
        EN: Find an available port starting from the specified port
        """
        import socket
        
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.config.metrics_host, port))
                    return port
            except OSError:
                continue
        
        # Se não encontrou nenhuma porta disponível, retorna a original
        # O erro será capturado pelo método chamador
        return start_port
    
    def _start_system_metrics_collection(self):
        """
        PT-BR: Inicia coleta periódica de métricas de sistema
        EN: Start periodic system metrics collection
        """
        def collect_system_metrics():
            while not self._stop_metrics.is_set():
                try:
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.cpu_usage.set(cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.memory_usage.set(memory.used)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    disk_percent = (disk.used / disk.total) * 100
                    self.disk_usage.set(disk_percent)
                    
                    logger.debug(
                        "System metrics collected",
                        cpu_percent=cpu_percent,
                        memory_used_gb=round(memory.used / (1024**3), 2),
                        disk_percent=round(disk_percent, 1)
                    )
                    
                except Exception as e:
                    logger.error("Error collecting system metrics", error=str(e))
                
                self._stop_metrics.wait(self.config.metrics_interval)
        
        self._metrics_thread = threading.Thread(
            target=collect_system_metrics,
            daemon=True,
            name="SystemMetricsCollector"
        )
        self._metrics_thread.start()
        
        logger.info("System metrics collection started")
    
    @contextmanager
    def time_operation(self, operation_type: str):
        """
        PT-BR:
        Context manager para medir tempo de operações.
        
        Parâmetros:
            operation_type: Tipo da operação
            
        Uso:
            with metrics.time_operation("summary_generation"):
                # código da operação
                
        EN:
        Context manager to measure operation time.
        
        Parameters:
            operation_type: Operation type
            
        Usage:
            with metrics.time_operation("summary_generation"):
                # operation code
        """
        start_time = time.time()
        status = "success"
        
        try:
            yield
        except Exception as e:
            status = "error"
            logger.error("Operation failed", operation_type=operation_type, error=str(e))
            raise
        finally:
            duration = time.time() - start_time
            
            if self.config.metrics_enabled:
                self.operation_duration.labels(operation_type=operation_type).observe(duration)
                self.operations_total.labels(operation_type=operation_type, status=status).inc()
            
            logger.info(
                "Operation completed",
                operation_type=operation_type,
                duration_seconds=round(duration, 3),
                status=status
            )
    
    def record_message_processed(self, group_id: str):
        """
        PT-BR: Registra processamento de mensagem
        EN: Record message processing
        """
        if self.config.metrics_enabled:
            self.messages_processed.labels(group_id=group_id).inc()
    
    def record_summary_generated(self, status: str = "success"):
        """
        PT-BR: Registra geração de resumo
        EN: Record summary generation
        """
        if self.config.metrics_enabled:
            self.summaries_generated.labels(status=status).inc()
    
    def record_cache_hit(self, cache_type: str):
        """
        PT-BR: Registra cache hit
        EN: Record cache hit
        """
        if self.config.metrics_enabled:
            self.cache_hits.labels(cache_type=cache_type).inc()
    
    def record_cache_miss(self, cache_type: str):
        """
        PT-BR: Registra cache miss
        EN: Record cache miss
        """
        if self.config.metrics_enabled:
            self.cache_misses.labels(cache_type=cache_type).inc()
    
    def record_api_request(self, endpoint: str, status_code: int, duration: float):
        """
        PT-BR: Registra requisição de API
        EN: Record API request
        """
        if self.config.metrics_enabled:
            self.api_request_duration.labels(
                api_endpoint=endpoint,
                status_code=str(status_code)
            ).observe(duration)
    
    def update_active_groups(self, count: int):
        """
        PT-BR: Atualiza número de grupos ativos
        EN: Update active groups count
        """
        if self.config.metrics_enabled:
            self.active_groups.set(count)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        PT-BR:
        Retorna resumo das métricas coletadas.
        
        Retorna:
            Dict: Resumo das métricas
            
        EN:
        Returns summary of collected metrics.
        
        Returns:
            Dict: Metrics summary
        """
        try:
            # Métricas de sistema
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Informações do processo
            process = psutil.Process()
            process_info = {
                "pid": process.pid,
                "cpu_percent": process.cpu_percent(),
                "memory_mb": round(process.memory_info().rss / (1024 * 1024), 2),
                "threads": process.num_threads(),
                "open_files": len(process.open_files()),
                "create_time": datetime.fromtimestamp(process.create_time()).isoformat()
            }
            
            return {
                "timestamp": datetime.now().isoformat(),
                "metrics_enabled": self.config.metrics_enabled,
                "server_running": self._server_started,
                "metrics_port": self.config.metrics_port,
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory": {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "used_gb": round(memory.used / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "percent": memory.percent
                    },
                    "disk": {
                        "total_gb": round(disk.total / (1024**3), 2),
                        "used_gb": round(disk.used / (1024**3), 2),
                        "free_gb": round(disk.free / (1024**3), 2),
                        "percent": round((disk.used / disk.total) * 100, 1)
                    }
                },
                "process": process_info
            }
            
        except Exception as e:
            logger.error("Failed to get metrics summary", error=str(e))
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "metrics_enabled": self.config.metrics_enabled
            }
    
    def stop(self):
        """
        PT-BR: Para coleta de métricas
        EN: Stop metrics collection
        """
        self._stop_metrics.set()
        
        if self._metrics_thread and self._metrics_thread.is_alive():
            self._metrics_thread.join(timeout=5)
        
        logger.info("Metrics collection stopped")


def time_function(operation_type: str):
    """
    PT-BR:
    Decorator para medir tempo de execução de funções.
    
    Parâmetros:
        operation_type: Tipo da operação
        
    Uso:
        @time_function("group_processing")
        def process_group(group_id):
            # código da função
            
    EN:
    Decorator to measure function execution time.
    
    Parameters:
        operation_type: Operation type
        
    Usage:
        @time_function("group_processing")
        def process_group(group_id):
            # function code
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with metrics_collector.time_operation(operation_type):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Instância global
metrics_collector = MetricsCollector()
