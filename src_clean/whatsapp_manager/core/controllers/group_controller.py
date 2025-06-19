"""
Controlador de Grupos do WhatsApp / WhatsApp Groups Controller

PT-BR:
Esta classe coordena operações relacionadas a grupos do WhatsApp,
delegando responsabilidades específicas para serviços especializados.

EN:
This class coordinates WhatsApp group operations,
delegating specific responsibilities to specialized services.
"""

import os
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from ..models.group import Group
from ..services.group_service import GroupService
from ..services.message_service import MessageService
from ...infrastructure.api.evolution_client import EvolutionClientWrapper
from ...infrastructure.persistence.group_repository import GroupRepository
from ...shared.constants.app_constants import AppConstants


class GroupController:
    """
    Controller principal para gerenciamento de grupos
    Main controller for group management
    """
    
    def __init__(self):
        """
        Inicializa o controller e seus serviços dependencies
        Initializes the controller and its service dependencies
        """
        # Configurar ambiente
        self._setup_environment()
        
        # Inicializar dependências
        self.evolution_client = EvolutionClientWrapper(
            base_url=self.base_url,
            api_token=self.api_token,
            instance_id=self.instance_id,
            instance_token=self.instance_token
        )
        
        self.group_repository = GroupRepository()
        self.group_service = GroupService(self.evolution_client, self.group_repository)
        self.message_service = MessageService(self.evolution_client)
        
        # Cache interno
        self._groups_cache: List[Group] = []
    
    def _setup_environment(self):
        """Configura variáveis de ambiente"""
        # Buscar .env na raiz do projeto
        current_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
        env_path = os.path.join(project_root, '.env')
        
        load_dotenv(env_path, override=True)
        
        # Configurações da API
        self.base_url = os.getenv("EVO_BASE_URL", AppConstants.DEFAULT_API_URL)
        self.api_token = os.getenv("EVO_API_TOKEN")
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        
        # Validar configurações obrigatórias
        if not all([self.api_token, self.instance_id, self.instance_token]):
            raise ValueError(
                "Configurações obrigatórias não encontradas: "
                "EVO_API_TOKEN, EVO_INSTANCE_NAME, EVO_INSTANCE_TOKEN"
            )
    
    def fetch_groups(self, force_refresh: bool = False) -> List[Group]:
        """
        Busca grupos do WhatsApp
        Fetches WhatsApp groups
        
        Args:
            force_refresh: Força atualização ignorando cache
            
        Returns:
            Lista de grupos
        """
        try:
            self._groups_cache = self.group_service.fetch_groups(force_refresh)
            return self._groups_cache
        except Exception as e:
            print(f"Erro ao buscar grupos: {e}")
            # Fallback para dados locais
            return self.group_service.load_groups_from_cache()
    
    def get_groups(self) -> List[Group]:
        """
        Retorna grupos em cache ou busca se necessário
        Returns cached groups or fetches if needed
        """
        if not self._groups_cache:
            return self.fetch_groups()
        return self._groups_cache
    
    def find_group_by_id(self, group_id: str) -> Optional[Group]:
        """
        Encontra grupo por ID
        Finds group by ID
        """
        groups = self.get_groups()
        return next((group for group in groups if group.group_id == group_id), None)
    
    def filter_groups_by_owner(self, owner: str) -> List[Group]:
        """
        Filtra grupos por proprietário
        Filters groups by owner
        """
        groups = self.get_groups()
        return [group for group in groups if group.owner == owner]
    
    def update_group_summary_settings(
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
        Atualiza configurações de resumo do grupo
        Updates group summary settings
        """
        return self.group_service.update_summary_settings(
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
    
    def get_group_messages(
        self, 
        group_id: str, 
        start_date: str, 
        end_date: str,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Obtém mensagens do grupo em período específico
        Gets group messages in specific period
        """
        return self.message_service.get_messages(
            group_id=group_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    def load_group_summary_data(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        Carrega dados de configuração de resumo do grupo
        Loads group summary configuration data
        """
        return self.group_repository.load_group_summary_data(group_id)
    
    def check_whatsapp_connection(self) -> Dict[str, Any]:
        """
        Verifica status da conexão WhatsApp
        Checks WhatsApp connection status
        """
        return self.evolution_client.check_connection_status()
    
    def get_connection_mode(self) -> str:
        """
        Retorna modo de conexão atual (online/offline)
        Returns current connection mode (online/offline)
        """
        try:
            status = self.check_whatsapp_connection()
            return "online" if status.get("connected", False) else "offline"
        except Exception:
            return "offline"
