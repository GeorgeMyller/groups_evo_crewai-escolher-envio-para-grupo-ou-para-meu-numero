"""
Sistema de Cache Redis Simplificado
"""
import json
import asyncio
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import redis
from redis import asyncio as aioredis

logger = logging.getLogger(__name__)

class CacheConfig:
    """Configuração do cache Redis."""
    def __init__(self):
        self.redis_host = "localhost"
        self.redis_port = 6379
        self.redis_password = None
        self.redis_db = 0
        self.enabled = True
        
        # TTL padrão em segundos
        self.default_ttl = 3600  # 1 hora
        self.groups_ttl = 3600   # 1 hora
        self.messages_ttl = 1800 # 30 minutos
        self.summaries_ttl = 7200 # 2 horas

class RedisCache:
    """Cache Redis com suporte assíncrono."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._sync_client = None
        self._async_client = None
        self._connected = False
        self.stats = {
            "hits": 0,
            "misses": 0,
            "operations": 0,
            "last_error": None
        }
    
    async def connect(self) -> bool:
        """Conectar ao Redis."""
        try:
            # Cliente assíncrono
            self._async_client = aioredis.from_url(
                f"redis://{self.config.redis_host}:{self.config.redis_port}",
                password=self.config.redis_password,
                db=self.config.redis_db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Cliente síncrono
            self._sync_client = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password,
                db=self.config.redis_db,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Testar conexão
            await self._async_client.ping()
            self._connected = True
            logger.info("✅ Redis conectado com sucesso")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Falha ao conectar Redis: {e}")
            self._connected = False
            return False
    
    async def disconnect(self):
        """Desconectar do Redis."""
        try:
            if self._async_client:
                await self._async_client.close()
            if self._sync_client:
                self._sync_client.close()
            self._connected = False
            logger.info("Redis desconectado")
        except Exception as e:
            logger.warning(f"Erro ao desconectar Redis: {e}")
    
    def is_connected(self) -> bool:
        """Verificar se está conectado."""
        return self._connected
    
    async def get(self, key: str) -> Optional[Any]:
        """Obter valor do cache."""
        if not self._connected or not self._async_client:
            return None
        
        try:
            self.stats["operations"] += 1
            value = await self._async_client.get(key)
            
            if value is not None:
                self.stats["hits"] += 1
                return self._deserialize(value)
            else:
                self.stats["misses"] += 1
                return None
                
        except Exception as e:
            logger.warning(f"Erro ao obter cache {key}: {e}")
            self.stats["last_error"] = str(e)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Salvar valor no cache."""
        if not self._connected or not self._async_client:
            return False
        
        try:
            self.stats["operations"] += 1
            serialized_value = self._serialize(value)
            ttl = ttl or self.config.default_ttl
            
            await self._async_client.setex(key, ttl, serialized_value)
            return True
            
        except Exception as e:
            logger.warning(f"Erro ao salvar cache {key}: {e}")
            self.stats["last_error"] = str(e)
            return False
    
    async def delete(self, key: str) -> bool:
        """Deletar chave do cache."""
        if not self._connected or not self._async_client:
            return False
        
        try:
            self.stats["operations"] += 1
            result = await self._async_client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.warning(f"Erro ao deletar cache {key}: {e}")
            self.stats["last_error"] = str(e)
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Deletar chaves por padrão."""
        if not self._connected or not self._async_client:
            return 0
        
        try:
            self.stats["operations"] += 1
            keys = await self._async_client.keys(pattern)
            
            if keys:
                deleted = await self._async_client.delete(*keys)
                return deleted
            return 0
            
        except Exception as e:
            logger.warning(f"Erro ao deletar padrão {pattern}: {e}")
            self.stats["last_error"] = str(e)
            return 0
    
    async def clear_all(self) -> bool:
        """Limpar todo o cache."""
        if not self._connected or not self._async_client:
            return False
        
        try:
            self.stats["operations"] += 1
            await self._async_client.flushdb()
            return True
            
        except Exception as e:
            logger.warning(f"Erro ao limpar cache: {e}")
            self.stats["last_error"] = str(e)
            return False
    
    async def exists(self, key: str) -> bool:
        """Verificar se chave existe."""
        if not self._connected or not self._async_client:
            return False
        
        try:
            result = await self._async_client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.warning(f"Erro ao verificar existência {key}: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do cache."""
        stats = self.stats.copy()
        
        # Calcular taxas
        total_operations = stats["hits"] + stats["misses"]
        if total_operations > 0:
            stats["hit_rate"] = (stats["hits"] / total_operations) * 100
            stats["miss_rate"] = (stats["misses"] / total_operations) * 100
        else:
            stats["hit_rate"] = 0
            stats["miss_rate"] = 0
        
        stats["connected"] = self._connected
        stats["total_operations"] = stats["operations"]
        
        # Informações do Redis se conectado
        if self._connected and self._async_client:
            try:
                info = await self._async_client.info()
                stats.update({
                    "redis_version": info.get("redis_version"),
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed")
                })
            except Exception as e:
                logger.warning(f"Erro ao obter info do Redis: {e}")
        
        return stats
    
    def _serialize(self, value: Any) -> str:
        """Serializar valor para JSON."""
        try:
            return json.dumps(value, ensure_ascii=False, default=str)
        except Exception:
            return str(value)
    
    def _deserialize(self, value: str) -> Any:
        """Deserializar valor do JSON."""
        try:
            return json.loads(value)
        except Exception:
            return value
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar saúde do cache."""
        try:
            if not self._connected:
                return {"healthy": False, "error": "Não conectado"}
            
            # Testar operação básica
            test_key = "_health_check"
            test_value = {"timestamp": datetime.now().isoformat()}
            
            await self.set(test_key, test_value, 10)
            result = await self.get(test_key)
            await self.delete(test_key)
            
            if result:
                return {"healthy": True, "latency_ms": 0}
            else:
                return {"healthy": False, "error": "Teste de operação falhou"}
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}

# Instância global do cache manager
cache_manager = None

def get_cache_manager(config: Optional[CacheConfig] = None) -> RedisCache:
    """Obter instância global do cache manager."""
    global cache_manager
    
    if cache_manager is None:
        cache_config = config or CacheConfig()
        cache_manager = RedisCache(cache_config)
    
    return cache_manager

async def init_cache(config: Optional[CacheConfig] = None) -> RedisCache:
    """Inicializar cache."""
    cache = get_cache_manager(config)
    await cache.connect()
    return cache
