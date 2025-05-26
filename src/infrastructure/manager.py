"""
Infrastructure components initialization and management

PT-BR:
Inicialização e gerenciamento centralizado dos componentes de infraestrutura:
- Cache Redis
- Métricas e Monitoramento
- Sistema de Backup

EN:
Centralized initialization and management of infrastructure components:
- Redis Cache
- Metrics and Monitoring
- Backup System
"""

import atexit
from typing import Dict, Any, Optional, List
from datetime import datetime
import structlog

from .cache.redis_cache import RedisCache, CacheConfig, get_cache_manager
from .monitoring.metrics import metrics_collector, MonitoringConfig
from .backup.backup_manager import backup_manager, BackupConfig

logger = structlog.get_logger(__name__)


class InfrastructureManager:
    """
    PT-BR:
    Gerenciador centralizado dos componentes de infraestrutura.
    Responsável por inicializar, configurar e coordenar todos os componentes.
    
    EN:
    Centralized manager for infrastructure components.
    Responsible for initializing, configuring and coordinating all components.
    """
    
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.metrics_collector = metrics_collector
        self.backup_manager = backup_manager
        self._initialized = False
        
        # Registrar cleanup no shutdown
        atexit.register(self.shutdown)
    
    async def initialize(self, 
                  cache_config: Optional[CacheConfig] = None,
                  monitoring_config: Optional[MonitoringConfig] = None,
                  backup_config: Optional[BackupConfig] = None) -> Dict[str, Any]:
        """
        PT-BR:
        Inicializa todos os componentes de infraestrutura.
        
        Parâmetros:
            cache_config: Configuração do cache
            monitoring_config: Configuração do monitoramento
            backup_config: Configuração do backup
            
        Retorna:
            Dict: Status da inicialização
            
        EN:
        Initialize all infrastructure components.
        
        Parameters:
            cache_config: Cache configuration
            monitoring_config: Monitoring configuration
            backup_config: Backup configuration
            
        Returns:
            Dict: Initialization status
        """
        if self._initialized:
            return {"status": "already_initialized", "timestamp": datetime.now().isoformat()}
        
        try:
            results = {
                "timestamp": datetime.now().isoformat(),
                "components": {},
                "overall_status": "success"
            }
            
            # Inicializar Cache Redis
            try:
                if cache_config:
                    self.cache_manager.config = cache_config
                
                # Conectar ao Redis
                connection_success = await self.cache_manager.connect()
                
                # Fazer health check após conexão
                cache_health = await self.cache_manager.health_check()
                results["components"]["cache"] = {
                    "status": "healthy" if cache_health["healthy"] else "unhealthy",
                    "enabled": self.cache_manager.config.enabled,
                    "connected": connection_success,
                    "details": cache_health
                }
                
                if cache_health["healthy"]:
                    logger.info("Redis cache initialized successfully")
                else:
                    logger.warning("Redis cache unhealthy but continuing", details=cache_health)
                    
            except Exception as e:
                results["components"]["cache"] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error("Failed to initialize Redis cache", error=str(e))
            
            # Inicializar Métricas
            try:
                if monitoring_config:
                    self.metrics_collector.config = monitoring_config
                
                if self.metrics_collector.config.metrics_enabled:
                    self.metrics_collector.start_metrics_server()
                    
                    metrics_summary = self.metrics_collector.get_metrics_summary()
                    results["components"]["monitoring"] = {
                        "status": "initialized",
                        "enabled": True,
                        "server_running": self.metrics_collector._server_started,
                        "port": self.metrics_collector.config.metrics_port,
                        "details": metrics_summary
                    }
                    
                    logger.info("Metrics system initialized successfully")
                else:
                    results["components"]["monitoring"] = {
                        "status": "disabled",
                        "enabled": False
                    }
                    logger.info("Metrics system disabled")
                    
            except Exception as e:
                results["components"]["monitoring"] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error("Failed to initialize metrics system", error=str(e))
            
            # Inicializar Sistema de Backup
            try:
                if backup_config:
                    self.backup_manager.config = backup_config
                
                # Verificar diretório de backup
                backup_list = self.backup_manager.list_backups()
                results["components"]["backup"] = {
                    "status": "initialized",
                    "enabled": self.backup_manager.config.backup_enabled,
                    "backup_directory": self.backup_manager.backup_path,
                    "existing_backups": backup_list.get("total_backups", 0),
                    "details": backup_list
                }
                
                logger.info("Backup system initialized successfully")
                
            except Exception as e:
                results["components"]["backup"] = {
                    "status": "error",
                    "error": str(e)
                }
                logger.error("Failed to initialize backup system", error=str(e))
            
            # Verificar se todos os componentes foram inicializados com sucesso
            component_statuses = [comp.get("status") for comp in results["components"].values()]
            if any(status == "error" for status in component_statuses):
                results["overall_status"] = "partial_success"
                logger.warning("Some infrastructure components failed to initialize")
            
            self._initialized = True
            logger.info("Infrastructure initialization completed", **results)
            
            return results
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error("Infrastructure initialization failed", **error_result)
            return error_result
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        PT-BR:
        Retorna status de saúde de todos os componentes.
        
        Retorna:
            Dict: Status de saúde dos componentes
            
        EN:
        Returns health status of all components.
        
        Returns:
            Dict: Components health status
        """
        try:
            health_status = {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy",
                "components": {}
            }
            
            # Status do Cache
            cache_health = await self.cache_manager.health_check()
            health_status["components"]["cache"] = cache_health
            
            # Status das Métricas
            metrics_summary = self.metrics_collector.get_metrics_summary()
            health_status["components"]["monitoring"] = {
                "status": "healthy" if metrics_summary.get("metrics_enabled") else "disabled",
                "server_running": metrics_summary.get("server_running", False),
                "details": metrics_summary
            }
            
            # Status do Backup
            backup_list = self.backup_manager.list_backups()
            health_status["components"]["backup"] = {
                "status": "healthy" if backup_list.get("status") == "success" else "error",
                "enabled": self.backup_manager.config.backup_enabled,
                "details": backup_list
            }
            
            # Determinar status geral
            component_health = []
            for component_name, component_status in health_status["components"].items():
                status = component_status.get("status", "unknown")
                if status in ["healthy", "disabled"]:
                    component_health.append(True)
                else:
                    component_health.append(False)
            
            if not all(component_health):
                health_status["overall_status"] = "degraded"
            
            return health_status
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    async def get_infrastructure_stats(self) -> Dict[str, Any]:
        """
        PT-BR:
        Retorna estatísticas completas da infraestrutura.
        
        Retorna:
            Dict: Estatísticas dos componentes
            
        EN:
        Returns complete infrastructure statistics.
        
        Returns:
            Dict: Components statistics
        """
        try:
            stats = {
                "timestamp": datetime.now().isoformat(),
                "cache": await self.cache_manager.get_stats(),
                "monitoring": self.metrics_collector.get_metrics_summary(),
                "backup": self.backup_manager.list_backups()
            }
            
            return stats
            
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
    
    async def perform_maintenance(self) -> Dict[str, Any]:
        """
        PT-BR:
        Executa tarefas de manutenção em todos os componentes.
        
        Retorna:
            Dict: Resultado das tarefas de manutenção
            
        EN:
        Perform maintenance tasks on all components.
        
        Returns:
            Dict: Maintenance tasks result
        """
        try:
            maintenance_results = {
                "timestamp": datetime.now().isoformat(),
                "tasks": {}
            }
            
            # Limpeza de backups antigos
            cleanup_result = self.backup_manager.cleanup_old_backups()
            maintenance_results["tasks"]["backup_cleanup"] = cleanup_result
            
            # Estatísticas do cache
            cache_stats = await self.cache_manager.get_stats()
            maintenance_results["tasks"]["cache_stats"] = cache_stats
            
            # Status das métricas
            metrics_summary = self.metrics_collector.get_metrics_summary()
            maintenance_results["tasks"]["metrics_summary"] = metrics_summary
            
            logger.info("Maintenance tasks completed", **maintenance_results)
            return maintenance_results
            
        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
            logger.error("Maintenance tasks failed", **error_result)
            return error_result
    
    def create_emergency_backup(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PT-BR:
        Cria backup de emergência dos dados críticos.
        
        Parâmetros:
            data: Dados para backup
            
        Retorna:
            Dict: Resultado do backup
            
        EN:
        Create emergency backup of critical data.
        
        Parameters:
            data: Data to backup
            
        Returns:
            Dict: Backup result
        """
        try:
            groups_data = data.get("groups", [])
            summaries_data = data.get("summaries", [])
            config_data = data.get("configuration", {})
            
            backup_result = self.backup_manager.create_full_backup(
                groups_data=groups_data,
                summaries_data=summaries_data,
                config_data=config_data
            )
            
            logger.info("Emergency backup created", **backup_result)
            return backup_result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error("Emergency backup failed", **error_result)
            return error_result
    
    async def warm_cache_with_groups(self, groups_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        PT-BR:
        Aquece o cache com dados dos grupos para melhor performance.
        
        Parâmetros:
            groups_data: Dados dos grupos para pré-carregar no cache
            
        Retorna:
            Dict: Resultado do aquecimento do cache
            
        EN:
        Warm up cache with groups data for better performance.
        
        Parameters:
            groups_data: Groups data to preload in cache
            
        Returns:
            Dict: Cache warming results
        """
        if not self._initialized or not self.cache_manager:
            return {"status": "error", "message": "Infrastructure not initialized"}
        
        try:
            logger.info("Starting cache warming process")
            
            # Warm cache with groups data
            warming_result = await self.cache_manager.warm_cache(groups_data)
            
            # Log results
            if warming_result["status"] == "success":
                logger.info("Cache warming completed successfully", 
                          warmed_keys=warming_result["warmed_keys"])
            else:
                logger.warning("Cache warming failed", 
                             error=warming_result.get("message"))
            
            return warming_result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
            logger.error(f"Cache warming error: {str(e)}")
            return error_result

    async def get_cache_info(self) -> Dict[str, Any]:
        """
        PT-BR:
        Obtém informações detalhadas do cache.
        
        Retorna:
            Dict: Informações do cache
            
        EN:
        Get detailed cache information.
        
        Returns:
            Dict: Cache information
        """
        if not self._initialized or not self.cache_manager:
            return {"status": "not_initialized"}
        
        try:
            cache_info = await self.cache_manager.get_cache_info()
            return cache_info
        except Exception as e:
            logger.error(f"Error getting cache info: {str(e)}")
            return {"status": "error", "error": str(e)}

    async def batch_cache_operation(self, operation: str, data: Dict[str, Any], ttl: Optional[int] = None) -> Dict[str, Any]:
        """
        PT-BR:
        Executa operações em lote no cache para melhor performance.
        
        Parâmetros:
            operation: Tipo de operação ('set' ou 'get')
            data: Dados para a operação
            ttl: Time to live para operações set
            
        Retorna:
            Dict: Resultado das operações
            
        EN:
        Execute batch cache operations for better performance.
        
        Parameters:
            operation: Operation type ('set' or 'get')
            data: Data for the operation
            ttl: Time to live for set operations
            
        Returns:
            Dict: Operation results
        """
        if not self._initialized or not self.cache_manager:
            return {"status": "error", "message": "Infrastructure not initialized"}
        
        try:
            if operation == "set":
                results = await self.cache_manager.batch_set(data, ttl)
                return {"status": "success", "results": results}
            elif operation == "get":
                if isinstance(data, dict):
                    keys = list(data.keys())
                else:
                    keys = data
                results = await self.cache_manager.batch_get(keys)
                return {"status": "success", "results": results}
            else:
                return {"status": "error", "message": f"Unsupported operation: {operation}"}
                
        except Exception as e:
            logger.error(f"Batch cache operation error: {str(e)}")
            return {"status": "error", "message": str(e)}

    def ensure_async_context(self):
        """
        PT-BR:
        Garante que temos um contexto assíncrono adequado.
        
        EN:
        Ensure we have a proper async context.
        """
        try:
            import threading
            
            # Verificar se estamos na thread principal
            if threading.current_thread() is not threading.main_thread():
                # Em thread secundária, criar novo loop
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return loop
                except Exception as e:
                    logger.warning(f"Cannot create new event loop: {e}")
                    return None
            
            # Na thread principal, verificar loop existente
            try:
                loop = asyncio.get_running_loop()
                return loop
            except RuntimeError:
                # Não há loop rodando, usar o padrão
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                    return loop
                except Exception as e:
                    logger.warning(f"Cannot get event loop: {e}")
                    # Criar novo loop como fallback
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    return loop
                    
        except Exception as e:
            logger.error(f"Error ensuring async context: {e}")
            return None

    def shutdown(self):
        """
        PT-BR: Encerra todos os componentes de infraestrutura
        EN: Shutdown all infrastructure components
        """
        try:
            logger.info("Shutting down infrastructure components")
            
            # Parar métricas
            if hasattr(self.metrics_collector, 'stop'):
                self.metrics_collector.stop()
            
            # Fechar cache com tratamento melhorado do event loop
            try:
                import asyncio
                import threading
                
                # Verificar se estamos na thread principal e se há um loop ativo
                if threading.current_thread() is threading.main_thread():
                    try:
                        # Tentar obter o loop atual
                        loop = asyncio.get_running_loop()
                        # Se há um loop rodando, criar task
                        asyncio.create_task(self.cache_manager.disconnect())
                    except RuntimeError:
                        # Não há loop ativo, criar um novo
                        try:
                            asyncio.run(self.cache_manager.disconnect())
                        except RuntimeError as re:
                            # Se ainda há problema, fazer disconnect síncronamente
                            logger.warning("Cannot run async disconnect, performing graceful close", error=str(re))
                            # Simular disconnect sem async
                            try:
                                if hasattr(self.cache_manager, '_sync_client') and self.cache_manager._sync_client:
                                    self.cache_manager._sync_client.close()
                                self.cache_manager._connected = False
                                logger.info("Cache disconnected synchronously")
                            except:
                                pass
                else:
                    # Estamos em uma thread secundária, usar asyncio.run
                    asyncio.run(self.cache_manager.disconnect())
                    
            except Exception as e:
                logger.warning("Error disconnecting cache", error=str(e))
            
            logger.info("Infrastructure shutdown completed")
            
        except Exception as e:
            logger.error("Error during infrastructure shutdown", error=str(e))


# Instância global
infrastructure = InfrastructureManager()
