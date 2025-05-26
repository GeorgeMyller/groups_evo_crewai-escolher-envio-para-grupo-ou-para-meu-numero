"""
Redis Cache Management System

PT-BR:
Sistema de cache Redis para melhorar performance e escalabilidade.
Suporta cache de grupos, mensagens e resumos com TTL configurável.

EN:
Redis cache management system to improve performance and scalability.
Supports caching of groups, messages and summaries with configurable TTL.
"""

import json
import asyncio
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import redis
from redis import asyncio as aioredis
import structlog

logger = structlog.get_logger(__name__)


class CacheConfig(BaseSettings):
    """
    PT-BR: Configurações do cache Redis
    EN: Redis cache configuration
    """
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    redis_url: Optional[str] = None
    cache_ttl_groups: int = 3600  # 1 hora
    cache_ttl_messages: int = 1800  # 30 minutos
    cache_ttl_summaries: int = 7200  # 2 horas
    cache_enabled: bool = True
    
    class Config:
        env_prefix = "CACHE_"
        env_file = ".env"


class RedisCache:
    """
    PT-BR:
    Gerenciador de cache Redis com suporte síncrono e assíncrono.
    
    EN:
    Redis cache manager with synchronous and asynchronous support.
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self._sync_client: Optional[redis.Redis] = None
        self._async_client: Optional[aioredis.Redis] = None
        
    def _get_connection_params(self) -> Dict[str, Any]:
        """
        PT-BR: Gera parâmetros de conexão Redis
        EN: Generate Redis connection parameters
        """
        if self.config.redis_url:
            return {"url": self.config.redis_url}
        
        params = {
            "host": self.config.redis_host,
            "port": self.config.redis_port,
            "db": self.config.redis_db,
            "decode_responses": True,
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }
        
        if self.config.redis_password:
            params["password"] = self.config.redis_password
            
        return params
    
    @property
    def sync_client(self) -> redis.Redis:
        """
        PT-BR: Cliente Redis síncrono (lazy loading)
        EN: Synchronous Redis client (lazy loading)
        """
        if self._sync_client is None:
            params = self._get_connection_params()
            self._sync_client = redis.Redis(**params)
        return self._sync_client
    
    async def async_client(self) -> aioredis.Redis:
        """
        PT-BR: Cliente Redis assíncrono (lazy loading)
        EN: Asynchronous Redis client (lazy loading)
        """
        if self._async_client is None:
            params = self._get_connection_params()
            self._async_client = aioredis.from_url(
                params.get("url") or f"redis://{params['host']}:{params['port']}/{params['db']}"
            )
        return self._async_client
    
    def _serialize_value(self, value: Any) -> str:
        """
        PT-BR: Serializa valor para armazenamento no Redis
        EN: Serialize value for Redis storage
        """
        if isinstance(value, (dict, list)):
            return json.dumps(value, default=str, ensure_ascii=False)
        return str(value)
    
    def _deserialize_value(self, value: str) -> Any:
        """
        PT-BR: Deserializa valor do Redis
        EN: Deserialize value from Redis
        """
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def _generate_key(self, category: str, identifier: str) -> str:
        """
        PT-BR: Gera chave padronizada para o cache
        EN: Generate standardized cache key
        """
        return f"whatsapp_groups:{category}:{identifier}"
    
    def set_group_cache(self, group_id: str, data: Dict[str, Any]) -> bool:
        """
        PT-BR:
        Armazena dados de grupo no cache.
        
        Parâmetros:
            group_id: ID do grupo
            data: Dados do grupo
            
        Retorna:
            bool: True se sucesso
            
        EN:
        Store group data in cache.
        
        Parameters:
            group_id: Group ID
            data: Group data
            
        Returns:
            bool: True if successful
        """
        if not self.config.cache_enabled:
            return False
            
        try:
            key = self._generate_key("groups", group_id)
            serialized = self._serialize_value(data)
            result = self.sync_client.setex(
                key, 
                self.config.cache_ttl_groups, 
                serialized
            )
            
            logger.info("Group cached successfully", group_id=group_id, key=key)
            return bool(result)
            
        except Exception as e:
            logger.error("Failed to cache group", group_id=group_id, error=str(e))
            return False
    
    def get_group_cache(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        PT-BR:
        Recupera dados de grupo do cache.
        
        Parâmetros:
            group_id: ID do grupo
            
        Retorna:
            Optional[Dict]: Dados do grupo ou None
            
        EN:
        Retrieve group data from cache.
        
        Parameters:
            group_id: Group ID
            
        Returns:
            Optional[Dict]: Group data or None
        """
        if not self.config.cache_enabled:
            return None
            
        try:
            key = self._generate_key("groups", group_id)
            cached_data = self.sync_client.get(key)
            
            if cached_data:
                logger.info("Group cache hit", group_id=group_id, key=key)
                return self._deserialize_value(cached_data)
            
            logger.info("Group cache miss", group_id=group_id, key=key)
            return None
            
        except Exception as e:
            logger.error("Failed to retrieve group from cache", group_id=group_id, error=str(e))
            return None
    
    def set_summary_cache(self, group_id: str, date: str, summary: str) -> bool:
        """
        PT-BR:
        Armazena resumo no cache.
        
        Parâmetros:
            group_id: ID do grupo
            date: Data do resumo (YYYY-MM-DD)
            summary: Conteúdo do resumo
            
        Retorna:
            bool: True se sucesso
            
        EN:
        Store summary in cache.
        
        Parameters:
            group_id: Group ID
            date: Summary date (YYYY-MM-DD)
            summary: Summary content
            
        Returns:
            bool: True if successful
        """
        if not self.config.cache_enabled:
            return False
            
        try:
            key = self._generate_key("summaries", f"{group_id}:{date}")
            result = self.sync_client.setex(
                key,
                self.config.cache_ttl_summaries,
                summary
            )
            
            logger.info("Summary cached successfully", group_id=group_id, date=date, key=key)
            return bool(result)
            
        except Exception as e:
            logger.error("Failed to cache summary", group_id=group_id, date=date, error=str(e))
            return False
    
    def get_summary_cache(self, group_id: str, date: str) -> Optional[str]:
        """
        PT-BR:
        Recupera resumo do cache.
        
        Parâmetros:
            group_id: ID do grupo
            date: Data do resumo (YYYY-MM-DD)
            
        Retorna:
            Optional[str]: Resumo ou None
            
        EN:
        Retrieve summary from cache.
        
        Parameters:
            group_id: Group ID
            date: Summary date (YYYY-MM-DD)
            
        Returns:
            Optional[str]: Summary or None
        """
        if not self.config.cache_enabled:
            return None
            
        try:
            key = self._generate_key("summaries", f"{group_id}:{date}")
            cached_summary = self.sync_client.get(key)
            
            if cached_summary:
                logger.info("Summary cache hit", group_id=group_id, date=date, key=key)
                return cached_summary
            
            logger.info("Summary cache miss", group_id=group_id, date=date, key=key)
            return None
            
        except Exception as e:
            logger.error("Failed to retrieve summary from cache", group_id=group_id, date=date, error=str(e))
            return None
    
    async def async_set_messages_cache(self, group_id: str, messages: List[Dict[str, Any]]) -> bool:
        """
        PT-BR:
        Armazena mensagens no cache (assíncrono).
        
        Parâmetros:
            group_id: ID do grupo
            messages: Lista de mensagens
            
        Retorna:
            bool: True se sucesso
            
        EN:
        Store messages in cache (asynchronous).
        
        Parameters:
            group_id: Group ID
            messages: List of messages
            
        Returns:
            bool: True if successful
        """
        if not self.config.cache_enabled:
            return False
            
        try:
            client = await self.async_client()
            key = self._generate_key("messages", group_id)
            serialized = self._serialize_value(messages)
            
            result = await client.setex(
                key,
                self.config.cache_ttl_messages,
                serialized
            )
            
            logger.info("Messages cached successfully", group_id=group_id, count=len(messages), key=key)
            return bool(result)
            
        except Exception as e:
            logger.error("Failed to cache messages", group_id=group_id, error=str(e))
            return False
    
    async def async_get_messages_cache(self, group_id: str) -> Optional[List[Dict[str, Any]]]:
        """
        PT-BR:
        Recupera mensagens do cache (assíncrono).
        
        Parâmetros:
            group_id: ID do grupo
            
        Retorna:
            Optional[List]: Lista de mensagens ou None
            
        EN:
        Retrieve messages from cache (asynchronous).
        
        Parameters:
            group_id: Group ID
            
        Returns:
            Optional[List]: List of messages or None
        """
        if not self.config.cache_enabled:
            return None
            
        try:
            client = await self.async_client()
            key = self._generate_key("messages", group_id)
            cached_messages = await client.get(key)
            
            if cached_messages:
                logger.info("Messages cache hit", group_id=group_id, key=key)
                return self._deserialize_value(cached_messages)
            
            logger.info("Messages cache miss", group_id=group_id, key=key)
            return None
            
        except Exception as e:
            logger.error("Failed to retrieve messages from cache", group_id=group_id, error=str(e))
            return None
    
    def invalidate_group(self, group_id: str) -> bool:
        """
        PT-BR:
        Invalida cache de um grupo específico.
        
        Parâmetros:
            group_id: ID do grupo
            
        Retorna:
            bool: True se sucesso
            
        EN:
        Invalidate cache for a specific group.
        
        Parameters:
            group_id: Group ID
            
        Returns:
            bool: True if successful
        """
        try:
            patterns = [
                self._generate_key("groups", group_id),
                self._generate_key("messages", group_id),
                self._generate_key("summaries", f"{group_id}:*")
            ]
            
            deleted_count = 0
            for pattern in patterns:
                if "*" in pattern:
                    # Para patterns com wildcard, usar SCAN
                    keys = list(self.sync_client.scan_iter(match=pattern))
                    if keys:
                        deleted_count += self.sync_client.delete(*keys)
                else:
                    deleted_count += self.sync_client.delete(pattern)
            
            logger.info("Group cache invalidated", group_id=group_id, deleted_keys=deleted_count)
            return True
            
        except Exception as e:
            logger.error("Failed to invalidate group cache", group_id=group_id, error=str(e))
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        PT-BR:
        Retorna estatísticas do cache.
        
        Retorna:
            Dict: Estatísticas do Redis
            
        EN:
        Returns cache statistics.
        
        Returns:
            Dict: Redis statistics
        """
        try:
            info = self.sync_client.info()
            
            # Contar chaves por categoria
            groups_count = len(list(self.sync_client.scan_iter(match="whatsapp_groups:groups:*")))
            messages_count = len(list(self.sync_client.scan_iter(match="whatsapp_groups:messages:*")))
            summaries_count = len(list(self.sync_client.scan_iter(match="whatsapp_groups:summaries:*")))
            
            return {
                "redis_version": info.get("redis_version"),
                "used_memory_human": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "cache_enabled": self.config.cache_enabled,
                "keys_count": {
                    "groups": groups_count,
                    "messages": messages_count,
                    "summaries": summaries_count,
                    "total": groups_count + messages_count + summaries_count
                },
                "ttl_config": {
                    "groups": self.config.cache_ttl_groups,
                    "messages": self.config.cache_ttl_messages,
                    "summaries": self.config.cache_ttl_summaries
                }
            }
            
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {"error": str(e), "cache_enabled": self.config.cache_enabled}
    
    def health_check(self) -> Dict[str, Any]:
        """
        PT-BR:
        Verifica saúde da conexão Redis.
        
        Retorna:
            Dict: Status da conexão
            
        EN:
        Check Redis connection health.
        
        Returns:
            Dict: Connection status
        """
        try:
            start_time = datetime.now()
            self.sync_client.ping()
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "cache_enabled": self.config.cache_enabled,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "cache_enabled": self.config.cache_enabled,
                "timestamp": datetime.now().isoformat()
            }
    
    def close(self):
        """
        PT-BR: Fecha conexões Redis
        EN: Close Redis connections
        """
        try:
            if self._sync_client:
                self._sync_client.close()
            
            if self._async_client:
                asyncio.create_task(self._async_client.close())
                
            logger.info("Redis connections closed")
            
        except Exception as e:
            logger.error("Error closing Redis connections", error=str(e))


# Instância global para uso em todo o projeto
cache_manager = RedisCache()
