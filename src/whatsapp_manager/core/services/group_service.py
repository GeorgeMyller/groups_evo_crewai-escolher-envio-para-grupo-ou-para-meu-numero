"""
Serviço de Gerenciamento de Grupos / Group Management Service

PT-BR:
Este serviço implementa a lógica de negócio relacionada ao gerenciamento
de grupos do WhatsApp, incluindo busca, cache e configurações.

EN:
This service implements business logic related to WhatsApp group management,
including fetching, caching, and settings.
"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import pandas as pd

from ..models.group import Group
from ...infrastructure.api.evolution_client import EvolutionClientWrapper
from ...infrastructure.persistence.group_repository import GroupRepository


class GroupService:
    """
    Serviço para lógica de negócio relacionada a grupos
    Service for group-related business logic
    """
    
    def __init__(self, evolution_client: EvolutionClientWrapper, group_repository: GroupRepository):
        """
        Inicializa o serviço com suas dependências
        Initializes the service with its dependencies
        """
        self.evolution_client = evolution_client
        self.group_repository = group_repository
        self.cache_timeout = 300  # 5 minutos em segundos
    
    def fetch_groups(self, force_refresh: bool = False) -> List[Group]:
        """
        Busca grupos da API ou cache
        Fetches groups from API or cache
        
        Args:
            force_refresh: Força busca da API ignorando cache
            
        Returns:
            Lista de grupos
        """
        # Verificar cache se não forçar refresh
        if not force_refresh:
            cached_groups = self._load_from_cache()
            if cached_groups:
                return cached_groups
        
        try:
            # Buscar da API
            api_groups = self.evolution_client.fetch_all_groups()
            
            # Converter para objetos Group
            groups = self._convert_api_groups_to_models(api_groups)
            
            # Enriquecer com dados de configuração
            groups = self._enrich_groups_with_settings(groups)
            
            # Salvar no cache
            self._save_to_cache(groups)
            
            return groups
            
        except Exception as e:
            print(f"Erro ao buscar grupos da API: {e}")
            # Fallback para cache ou dados locais
            return self.load_groups_from_cache()
    
    def load_groups_from_cache(self) -> List[Group]:
        """
        Carrega grupos apenas do cache/dados locais
        Loads groups only from cache/local data
        """
        # Primeiro tentar cache da API
        cached_groups = self._load_from_cache()
        if cached_groups:
            return cached_groups
        
        # Fallback: criar grupos a partir do CSV de configurações
        return self._create_groups_from_csv()
    
    def update_summary_settings(
        self,
        group_id: str,
        horario: str,
        enabled: bool,
        is_links: bool = False,
        is_names: bool = False,
        send_to_group: bool = True,
        send_to_personal: bool = False,
        min_messages_summary: int = 50,
        **additional_params
    ) -> bool:
        """
        Atualiza configurações de resumo de um grupo
        Updates group summary settings
        """
        return self.group_repository.update_summary_settings(
            group_id=group_id,
            horario=horario,
            enabled=enabled,
            is_links=is_links,
            is_names=is_names,
            send_to_group=send_to_group,
            send_to_personal=send_to_personal,
            min_messages_summary=min_messages_summary,
            **additional_params
        )
    
    def _convert_api_groups_to_models(self, api_groups: List[Dict[str, Any]]) -> List[Group]:
        """
        Converte grupos da API para objetos Group
        Converts API groups to Group objects
        """
        groups = []
        
        for group_data in api_groups:
            try:
                group = Group(
                    group_id=group_data["id"],
                    name=group_data["subject"],
                    subject_owner=group_data.get("subjectOwner", ""),
                    subject_time=group_data.get("subjectTime", 0),
                    picture_url=group_data.get("pictureUrl"),
                    size=group_data.get("size", 0),
                    creation=group_data.get("creation", 0),
                    owner=group_data.get("owner"),
                    restrict=group_data.get("restrict", False),
                    announce=group_data.get("announce", False),
                    is_community=group_data.get("isCommunity", False),
                    is_community_announce=group_data.get("isCommunityAnnounce", False)
                )
                groups.append(group)
            except Exception as e:
                print(f"Erro ao converter grupo {group_data.get('id', 'unknown')}: {e}")
                continue
        
        return groups
    
    def _enrich_groups_with_settings(self, groups: List[Group]) -> List[Group]:
        """
        Enriquece grupos com configurações de resumo
        Enriches groups with summary settings
        """
        # Carregar dados de configuração
        summary_data = self.group_repository.load_all_summary_data()
        
        for group in groups:
            # Buscar configurações específicas do grupo
            group_config = summary_data.get(group.group_id, {})
            
            # Aplicar configurações
            group.horario = group_config.get("horario", "22:00")
            group.enabled = group_config.get("enabled", False)
            group.is_links = group_config.get("is_links", False)
            group.is_names = group_config.get("is_names", False)
            group.send_to_group = group_config.get("send_to_group", True)
            group.send_to_personal = group_config.get("send_to_personal", False)
            group.min_messages_summary = group_config.get("min_messages_summary", 50)
        
        return groups
    
    def _create_groups_from_csv(self) -> List[Group]:
        """
        Cria grupos básicos a partir do CSV de configurações
        Creates basic groups from configuration CSV
        """
        try:
            summary_data = self.group_repository.load_all_summary_data()
            groups = []
            
            for group_id, config in summary_data.items():
                group = Group(
                    group_id=group_id,
                    name=config.get("group_name", f"Grupo {group_id}"),
                    subject_owner="",
                    subject_time=0,
                    picture_url=None,
                    size=0,
                    creation=0,
                    owner=None,
                    restrict=False,
                    announce=False,
                    is_community=False,
                    is_community_announce=False,
                    horario=config.get("horario", "22:00"),
                    enabled=config.get("enabled", False),
                    is_links=config.get("is_links", False),
                    is_names=config.get("is_names", False),
                    send_to_group=config.get("send_to_group", True),
                    send_to_personal=config.get("send_to_personal", False),
                    min_messages_summary=config.get("min_messages_summary", 50)
                )
                groups.append(group)
            
            return groups
            
        except Exception as e:
            print(f"Erro ao criar grupos do CSV: {e}")
            return []
    
    def _load_from_cache(self) -> Optional[List[Group]]:
        """
        Carrega grupos do cache local
        Loads groups from local cache
        """
        cache_file = self._get_cache_file_path()
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Verificar se o cache não expirou
            cache_time = cache_data.get("timestamp", 0)
            current_time = datetime.now().timestamp()
            
            if current_time - cache_time > self.cache_timeout:
                return None
            
            # Converter dados do cache para objetos Group
            groups = []
            for group_data in cache_data.get("groups", []):
                group = Group(**group_data)
                groups.append(group)
            
            return groups
            
        except Exception as e:
            print(f"Erro ao carregar cache: {e}")
            return None
    
    def _save_to_cache(self, groups: List[Group]):
        """
        Salva grupos no cache local
        Saves groups to local cache
        """
        try:
            cache_data = {
                "timestamp": datetime.now().timestamp(),
                "groups": [group.__dict__ for group in groups]
            }
            
            cache_file = self._get_cache_file_path()
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def _get_cache_file_path(self) -> str:
        """
        Retorna caminho do arquivo de cache
        Returns cache file path
        """
        current_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
        cache_dir = os.path.join(project_root, "data", "cache")
        return os.path.join(cache_dir, "groups_cache.json")
