"""
Repositório de Grupos / Group Repository

PT-BR:
Este repositório gerencia a persistência de dados relacionados a grupos,
incluindo configurações de resumo e cache local.

EN:
This repository manages persistence of group-related data,
including summary settings and local cache.
"""

import os
import pandas as pd
from typing import Dict, Any, Optional


class GroupRepository:
    """
    Repositório para dados de grupos
    Repository for group data
    """
    
    def __init__(self):
        """
        Inicializa o repositório
        Initializes the repository
        """
        self.project_root = self._get_project_root()
        self.csv_file_primary = os.path.join(self.project_root, "data", "group_summary.csv")
        self.csv_file_fallback = os.path.join(self.project_root, "group_summary.csv")
        
        # Criar diretório data se não existir
        os.makedirs(os.path.dirname(self.csv_file_primary), exist_ok=True)
    
    def load_all_summary_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Carrega todos os dados de configuração de resumo
        Loads all summary configuration data
        
        Returns:
            Dicionário com configurações por group_id
        """
        try:
            df = self._load_csv()
            
            if df.empty:
                return {}
            
            # Converter para dicionário indexado por group_id
            summary_data = {}
            for _, row in df.iterrows():
                group_id = row['group_id']
                summary_data[group_id] = row.to_dict()
            
            return summary_data
            
        except Exception as e:
            print(f"Erro ao carregar dados de resumo: {e}")
            return {}
    
    def load_group_summary_data(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        Carrega dados de configuração de um grupo específico
        Loads configuration data for a specific group
        
        Args:
            group_id: ID do grupo
            
        Returns:
            Configurações do grupo ou None
        """
        try:
            df = self._load_csv()
            
            if df.empty:
                return None
            
            group_data = df[df['group_id'] == group_id]
            
            if group_data.empty:
                return None
            
            return group_data.iloc[0].to_dict()
            
        except Exception as e:
            print(f"Erro ao carregar dados do grupo {group_id}: {e}")
            return None
    
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
        
        Args:
            group_id: ID do grupo
            horario: Horário do resumo
            enabled: Se o resumo está habilitado
            is_links: Incluir links
            is_names: Incluir nomes
            send_to_group: Enviar para o grupo
            send_to_personal: Enviar para número pessoal
            min_messages_summary: Mínimo de mensagens
            **additional_params: Parâmetros adicionais
            
        Returns:
            True se salvou com sucesso
        """
        try:
            df = self._load_csv()
            
            # Remover entrada existente do grupo
            df = df[df['group_id'] != group_id]
            
            # Criar nova configuração
            new_config = {
                "group_id": group_id,
                "horario": horario,
                "enabled": enabled,
                "is_links": is_links,
                "is_names": is_names,
                "send_to_group": send_to_group,
                "send_to_personal": send_to_personal,
                "min_messages_summary": min_messages_summary,
                **additional_params
            }
            
            # Adicionar nova configuração
            df = pd.concat([df, pd.DataFrame([new_config])], ignore_index=True)
            
            # Salvar CSV
            self._save_csv(df)
            
            return True
            
        except Exception as e:
            print(f"Erro ao atualizar configurações do grupo {group_id}: {e}")
            return False
    
    def delete_group_settings(self, group_id: str) -> bool:
        """
        Remove configurações de um grupo
        Removes group settings
        
        Args:
            group_id: ID do grupo
            
        Returns:
            True se removeu com sucesso
        """
        try:
            df = self._load_csv()
            
            # Remover entrada do grupo
            original_count = len(df)
            df = df[df['group_id'] != group_id]
            
            if len(df) < original_count:
                self._save_csv(df)
                return True
            else:
                return False  # Grupo não foi encontrado
                
        except Exception as e:
            print(f"Erro ao remover configurações do grupo {group_id}: {e}")
            return False
    
    def get_enabled_groups(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna apenas grupos com resumo habilitado
        Returns only groups with summary enabled
        
        Returns:
            Dicionário com grupos habilitados
        """
        all_data = self.load_all_summary_data()
        return {
            group_id: config 
            for group_id, config in all_data.items() 
            if config.get('enabled', False)
        }
    
    def _load_csv(self) -> pd.DataFrame:
        """
        Carrega CSV com fallback
        Loads CSV with fallback
        """
        # Tentar carregar do local principal
        if os.path.exists(self.csv_file_primary):
            try:
                df = pd.read_csv(self.csv_file_primary)
                print(f"CSV carregado de: {self.csv_file_primary}")
                return df
            except Exception as e:
                print(f"Erro ao carregar CSV principal: {e}")
        
        # Fallback para local secundário
        if os.path.exists(self.csv_file_fallback):
            try:
                df = pd.read_csv(self.csv_file_fallback)
                print(f"CSV carregado de: {self.csv_file_fallback}")
                return df
            except Exception as e:
                print(f"Erro ao carregar CSV fallback: {e}")
        
        # Retornar DataFrame vazio com colunas padrão
        print("Nenhum CSV encontrado. Criando DataFrame vazio.")
        return pd.DataFrame(columns=[
            "group_id", "horario", "enabled", "is_links", "is_names",
            "send_to_group", "send_to_personal", "min_messages_summary"
        ])
    
    def _save_csv(self, df: pd.DataFrame):
        """
        Salva CSV no local principal
        Saves CSV to primary location
        """
        try:
            df.to_csv(self.csv_file_primary, index=False)
            print(f"CSV salvo em: {self.csv_file_primary}")
        except Exception as e:
            print(f"Erro ao salvar CSV: {e}")
            raise e
    
    def _get_project_root(self) -> str:
        """
        Obtém diretório raiz do projeto
        Gets project root directory
        """
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(current_dir, '..', '..', '..', '..'))
    
    def backup_csv(self, backup_name: Optional[str] = None) -> str:
        """
        Cria backup do CSV atual
        Creates backup of current CSV
        
        Args:
            backup_name: Nome personalizado do backup
            
        Returns:
            Caminho do arquivo de backup
        """
        from datetime import datetime
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"group_summary_backup_{timestamp}.csv"
        
        backup_dir = os.path.join(self.project_root, "data", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_path = os.path.join(backup_dir, backup_name)
        
        try:
            df = self._load_csv()
            df.to_csv(backup_path, index=False)
            print(f"Backup criado: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            raise e
