"""
Controlador de grupos do WhatsApp com cache Redis integrado.
"""
import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests
from config import config

logger = logging.getLogger(__name__)

class GroupController:
    """Controlador para gerenciamento de grupos do WhatsApp com cache."""
    
    def __init__(self, cache_service=None):
        self.api_token = config.evo_api_token
        self.instance_token = config.evo_instance_token
        self.instance_name = config.evo_instance_name
        self.base_url = config.evo_base_url.rstrip('/')
        self.cache = cache_service
        
        # Headers para as requisições
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_token}'
        }
    
    def fetch_groups(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Buscar grupos do WhatsApp com suporte a cache.
        
        Args:
            use_cache: Se deve usar cache (padrão: True)
            
        Returns:
            Lista de grupos
        """
        cache_key = f"groups:{self.instance_name}"
        
        # Tentar obter do cache primeiro
        if use_cache and self.cache:
            try:
                cached_groups = self._get_from_cache_sync(cache_key)
                if cached_groups:
                    logger.info(f"📋 Grupos obtidos do cache: {len(cached_groups)} grupos")
                    return cached_groups
            except Exception as e:
                logger.warning(f"Erro ao acessar cache: {e}")
        
        # Buscar da API
        try:
            groups = self._fetch_groups_from_api()
            
            # Salvar no cache se disponível
            if self.cache and groups:
                try:
                    self._save_to_cache_sync(cache_key, groups, ttl=config.redis.groups_ttl)
                    logger.info(f"💾 Grupos salvos no cache: {len(groups)} grupos")
                except Exception as e:
                    logger.warning(f"Erro ao salvar no cache: {e}")
            
            return groups
            
        except Exception as e:
            logger.error(f"Erro ao buscar grupos: {e}")
            return []
    
    def _fetch_groups_from_api(self) -> List[Dict[str, Any]]:
        """Buscar grupos diretamente da API Evolution."""
        url = f"{self.base_url}/group/fetchAllGroups/{self.instance_name}"
        logger.info(f"Attempting to fetch groups from URL: {url}")
        
        response_text = ""  # Initialize in case of early exception
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response_text = response.text # Store for potential error logging
            logger.info(f"API Response Status Code: {response.status_code}")
            logger.debug(f"API Response Headers: {response.headers}")
            # Log only a snippet of raw content to avoid overly verbose logs
            logger.debug(f"API Response Content (raw snippet): {response_text[:500]}...")
            
            response.raise_for_status()  # Raises HTTPError for bad responses (4XX or 5XX)
            
            data = response.json()
            logger.debug(f"API Response JSON (parsed): {data}")
            
            groups = data.get('data', [])
            
            # Processar e limpar dados dos grupos
            processed_groups = []
            for group in groups:
                processed_group = {
                    'id': group.get('id', ''),
                    'subject': group.get('subject', 'Sem nome'),
                    'description': group.get('description', ''),
                    'participants': group.get('participants', []),
                    'owner': group.get('owner', ''),
                    'creation': group.get('creation', 0),
                    'last_update': datetime.now().isoformat()
                }
                processed_groups.append(processed_group)
            
            logger.info(f"🔄 Grupos obtidos da API: {len(processed_groups)} grupos")
            if not processed_groups and 'data' not in data: # More specific check
                logger.warning("API response did not contain a 'data' field or it was empty.")
            elif not processed_groups:
                 logger.warning("API returned an empty list of groups in the 'data' field.")
            return processed_groups
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred while fetching groups: {http_err} - Response: {response_text}")
            # Potentially re-raise or return empty list depending on desired error handling
            raise  # Or return [] if you want to handle it gracefully upstream
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para buscar grupos: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar resposta JSON: {e}")
            raise
    
    def get_group_messages(self, group_id: str, limit: int = 100, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Buscar mensagens de um grupo específico.
        
        Args:
            group_id: ID do grupo
            limit: Limite de mensagens (padrão: 100)
            use_cache: Se deve usar cache (padrão: True)
            
        Returns:
            Lista de mensagens
        """
        cache_key = f"messages:{group_id}:{limit}"
        
        # Tentar obter do cache primeiro
        if use_cache and self.cache:
            try:
                cached_messages = self._get_from_cache_sync(cache_key)
                if cached_messages:
                    logger.info(f"📨 Mensagens obtidas do cache: {len(cached_messages)} mensagens")
                    return cached_messages
            except Exception as e:
                logger.warning(f"Erro ao acessar cache de mensagens: {e}")
        
        # Buscar da API
        try:
            messages = self._fetch_messages_from_api(group_id, limit)
            
            # Salvar no cache se disponível
            if self.cache and messages:
                try:
                    self._save_to_cache_sync(cache_key, messages, ttl=config.redis.messages_ttl)
                    logger.info(f"💾 Mensagens salvas no cache: {len(messages)} mensagens")
                except Exception as e:
                    logger.warning(f"Erro ao salvar mensagens no cache: {e}")
            
            return messages
            
        except Exception as e:
            logger.error(f"Erro ao buscar mensagens do grupo {group_id}: {e}")
            return []
    
    def _fetch_messages_from_api(self, group_id: str, limit: int) -> List[Dict[str, Any]]:
        """Buscar mensagens diretamente da API Evolution."""
        url = f"{self.base_url}/chat/findMessages/{self.instance_name}"
        
        payload = {
            "where": {
                "remoteJid": group_id
            },
            "limit": limit
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get('data', [])
            
            logger.info(f"🔄 Mensagens obtidas da API: {len(messages)} mensagens")
            return messages
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para buscar mensagens: {e}")
            raise
    
    def invalidate_cache(self, group_id: Optional[str] = None):
        """
        Invalidar cache de grupos ou de um grupo específico.
        
        Args:
            group_id: ID do grupo específico (opcional)
        """
        if not self.cache:
            return
        
        try:
            if group_id:
                # Invalidar cache específico do grupo
                patterns = [
                    f"messages:{group_id}:*",
                    f"summary:{group_id}:*"
                ]
                for pattern in patterns:
                    self._delete_from_cache_sync(pattern)
                logger.info(f"🗑️ Cache invalidado para grupo: {group_id}")
            else:
                # Invalidar todo o cache de grupos
                cache_key = f"groups:{self.instance_name}"
                self._delete_from_cache_sync(cache_key)
                logger.info("🗑️ Cache de grupos invalidado")
                
        except Exception as e:
            logger.warning(f"Erro ao invalidar cache: {e}")
    
    def _get_from_cache_sync(self, key: str) -> Optional[Any]:
        """Obter dados do cache de forma síncrona."""
        if not self.cache:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.cache.get(key))
        except RuntimeError:
            # Não há loop de eventos ativo
            return asyncio.run(self.cache.get(key))
    
    def _save_to_cache_sync(self, key: str, data: Any, ttl: int = 3600):
        """Salvar dados no cache de forma síncrona."""
        if not self.cache:
            return
        
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.cache.set(key, data, ttl))
        except RuntimeError:
            # Não há loop de eventos ativo
            asyncio.run(self.cache.set(key, data, ttl))
    
    def _delete_from_cache_sync(self, pattern: str):
        """Deletar dados do cache de forma síncrona."""
        if not self.cache:
            return
        
        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.cache.delete_pattern(pattern))
        except RuntimeError:
            # Não há loop de eventos ativo
            asyncio.run(self.cache.delete_pattern(pattern))
    
    def get_stats(self) -> Dict[str, Any]:
        """Obter estatísticas do controlador."""
        stats = {
            "instance_name": self.instance_name,
            "cache_enabled": self.cache is not None,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.cache:
            try:
                cache_stats = self._get_cache_stats_sync()
                stats["cache_stats"] = cache_stats
            except Exception as e:
                logger.warning(f"Erro ao obter estatísticas do cache: {e}")
        
        return stats
    
    def _get_cache_stats_sync(self) -> Dict[str, Any]:
        """Obter estatísticas do cache de forma síncrona."""
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self.cache.get_stats())
        except RuntimeError:
            return asyncio.run(self.cache.get_stats())
