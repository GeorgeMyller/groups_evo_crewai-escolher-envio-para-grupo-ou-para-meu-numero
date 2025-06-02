"""
Controlador de Grupos do WhatsApp / WhatsApp Groups Controller

PT-BR:
Esta classe gerencia grupos do WhatsApp, incluindo cache local, consultas à API Evolution
e configurações de resumos automáticos. Fornece funcionalidades para buscar, filtrar
e atualizar informações dos grupos.

EN:
This class manages WhatsApp groups, including local caching, Evolution API queries,
and automatic summary settings. Provides functionality to fetch, filter,
and update group information.
"""

import json
import logging
import os
import sys # Keep sys for other potential uses, though path append is removed.
import time
from datetime import datetime

# Third-party library imports
from dotenv import load_dotenv
import pandas as pd
from evolutionapi.client import EvolutionClient
from evolutionapi.exceptions import EvolutionAuthenticationError
from evolutionapi.exceptions import EvolutionAPIError

# Local application/library imports
from .group import Group
from .message_sandeco import MessageSandeco
from whatsapp_manager.utils.task_scheduler import TaskScheduled


# Define Project Root assuming this file is src/whatsapp_manager/core/group_controller.py
# Navigate three levels up to reach the project root from core.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

class GroupController:
    logger = logging.getLogger(__name__)

    def __init__(self):
        """
        PT-BR:
        Inicializa o controlador com configurações do ambiente e validações.
        Configura conexão com API Evolution e caminhos de arquivos locais.

        EN:
        Initializes the controller with environment settings and validations.
        Sets up Evolution API connection and local file paths.
        """
        # Environment setup / Configuração do ambiente
        env_path = os.path.join(PROJECT_ROOT, '.env') # Use PROJECT_ROOT
        load_dotenv(env_path, override=True)

        # API Configuration / Configuração da API
        self.base_url = os.getenv("EVO_BASE_URL", 'http://localhost:8081')
        self.api_token = os.getenv("EVO_API_TOKEN")
        self.instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.instance_token = os.getenv("EVO_INSTANCE_TOKEN")

        # File paths / Caminhos dos arquivos, now relative to PROJECT_ROOT/data
        self.csv_file = os.path.join(PROJECT_ROOT, "data", "group_summary.csv")
        self.cache_file = os.path.join(PROJECT_ROOT, "data", "groups_cache.json")

        if not all([self.api_token, self.instance_id, self.instance_token]):
            raise ValueError("API_TOKEN, INSTANCE_NAME ou INSTANCE_TOKEN não configurados. / API_TOKEN, INSTANCE_NAME or INSTANCE_TOKEN not configured.")
        # Garantir non-null types para o type checker
        assert self.api_token is not None and self.instance_id is not None and self.instance_token is not None

        self.logger.info("Inicializando EvolutionClient com URL: %s", self.base_url)
        self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)
        self.groups = []

    def _load_cache(self):
        """
        PT-BR:
        Carrega dados do cache local para otimizar requisições.
        Retorna None se o cache estiver inválido ou não existir.

        EN:
        Loads data from local cache to optimize requests.
        Returns None if cache is invalid or doesn't exist.
        """
        if not os.path.exists(self.cache_file):
            return None
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except json.decoder.JSONDecodeError as e:
            self.logger.warning("Cache com formato inválido. Removendo o arquivo: %s", e)
            try: # Attempt to remove corrupted cache file
                os.remove(self.cache_file)
            except OSError as oe:
                self.logger.error("Erro ao remover arquivo de cache corrompido %s: %s", self.cache_file, oe, exc_info=True)
            return None
        except Exception as e:
            self.logger.error("Erro ao carregar cache: %s", e, exc_info=True)
            return None

    def _save_cache(self, groups_data):
        """
        PT-BR:
        Salva dados dos grupos no cache com timestamp.
        Garante que os dados sejam serializáveis em JSON.

        Parâmetros:
            groups_data: Dados dos grupos a serem salvos

        EN:
        Saves group data to cache with timestamp.
        Ensures data is JSON serializable.

        Parameters:
            groups_data: Group data to be saved
        """
        try:
            # Verifica se groups_data é do tipo serializável (list ou dict), senão ajusta
            if not isinstance(groups_data, (list, dict)):
                self.logger.warning("groups_data não é serializável. Ajustando para lista vazia.")
                groups_data = []
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'groups': groups_data
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            self.logger.error("Erro ao salvar cache: %s", e, exc_info=True)

    def _fetch_from_api(self):
        """
        PT-BR:
        Busca grupos da API Evolution com sistema de retry.
        Implementa espera exponencial em caso de limite de requisições.

        Raises:
            Exception: Se não conseguir buscar após várias tentativas

        EN:
        Fetches groups from Evolution API with retry system.
        Implements exponential backoff for rate limits.

        Raises:
            Exception: If unable to fetch after several attempts
        """
        # Verifica se as configurações ainda estão válidas
        if '<' in self.base_url or '>' in self.base_url: # Basic check, consider more robust URL validation
            self.logger.warning("URL inválida detectada, redefinindo para padrão: %s", self.base_url)
            self.base_url = 'http://localhost:8081' # Consider making default URL a constant
            assert self.api_token is not None, "API token cannot be None after URL reset" # Should already be asserted in __init__
            self.client = EvolutionClient(base_url=self.base_url, api_token=self.api_token)

        max_retries = 3
        base_delay = 15 # seconds
        for attempt in range(max_retries):
            try:
                self.logger.info("Tentativa %s: Fazendo requisição para %s", attempt + 1, self.base_url)
                # Verify that instance_id and instance_token are not None
                assert self.instance_id is not None, "instance_id cannot be None"
                assert self.instance_token is not None, "instance_token cannot be None"

                groups_raw_data = self.client.group.fetch_all_groups(
                    instance_id=self.instance_id,
                    instance_token=self.instance_token,
                    get_participants=False # Consider making this configurable
                )
                return groups_raw_data

            except EvolutionAuthenticationError as e:
                self.logger.error("Erro de autenticação: %s", e)
                self.logger.error("Verifique suas credenciais no arquivo .env:")
                self.logger.error("- EVO_API_TOKEN: %s", '✓' if self.api_token else '✗')
                self.logger.error("- EVO_INSTANCE_NAME: %s", '✓' if self.instance_id else '✗')
                self.logger.error("- EVO_INSTANCE_TOKEN: %s", '✓' if self.instance_token else '✗')
                self.logger.error("- EVO_BASE_URL: %s", self.base_url)
                raise  # Re-raise the exception after logging
            except EvolutionAPIError as e:
                if 'rate-overlimit' in str(e).lower() and attempt < max_retries - 1: # Check lowercased error string
                    wait_time = base_delay * (2 ** attempt)
                    self.logger.warning("Rate limit atingido. Aguardando %s segundos...", wait_time)
                    time.sleep(wait_time)
                else:
                    self.logger.error("Erro na API: %s", e, exc_info=True)
                    raise # Re-raise the exception
            except Exception as e: # Catch any other unexpected errors during API call
                self.logger.error("Erro inesperado durante _fetch_from_api: %s", e, exc_info=True)
                raise # Re-raise

        self.logger.error("Não foi possível buscar os grupos após %s tentativas", max_retries)
        raise Exception(f"Não foi possível buscar os grupos após {max_retries} tentativas")


    def _create_group_object(self, group_item_data: dict, summary_df: pd.DataFrame) -> Group | None:
        """
        Helper method to create a Group object from raw data and summary information.
        """
        if not isinstance(group_item_data, dict):
            self.logger.warning("group_item_data não é um dicionário. Ignorando: %s", group_item_data)
            return None

        group_id = group_item_data.get("id")
        if not group_id:
            self.logger.warning("Item de grupo sem 'id'. Ignorando: %s", group_item_data)
            return None

        group_subject = group_item_data.get("subject")
        if not group_subject:
            self.logger.warning("Item de grupo sem 'subject' (nome). Ignorando ID: %s", group_id)
            return None

        # Use .loc for safer access and ensure 'group_id' column exists or handle potential KeyError
        try:
            resumo_df_slice = summary_df.loc[summary_df["group_id"] == group_id]
        except KeyError: # If 'group_id' column doesn't exist in summary_df
             self.logger.warning("Coluna 'group_id' não encontrada no DataFrame de resumo. Usando padrões para o grupo %s.", group_id)
             resumo_df_slice = pd.DataFrame() # Empty DataFrame to use defaults

        horario = "22:00"
        enabled = False
        is_links = False
        is_names = False
        send_to_group = True
        send_to_personal = False
        min_messages_summary = 50 # Default value from Group class or a constant

        if not resumo_df_slice.empty:
            resumo_dict = resumo_df_slice.iloc[0].to_dict()
            horario = resumo_dict.get("horario", horario)
            enabled = resumo_dict.get("enabled", enabled)
            is_links = resumo_dict.get("is_links", is_links)
            is_names = resumo_dict.get("is_names", is_names)
            send_to_group = resumo_dict.get("send_to_group", send_to_group)
            send_to_personal = resumo_dict.get("send_to_personal", send_to_personal)
            min_messages_summary = resumo_dict.get("min_messages_summary", min_messages_summary)


        try:
            group_obj = Group(
                group_id=group_id,
                name=group_subject, # Use extracted subject
                subject_owner=group_item_data.get("subjectOwner", "remoteJid"), # Provide default if missing
                subject_time=group_item_data.get("subjectTime", 0), # Provide default
                picture_url=group_item_data.get("pictureUrl"),
                size=group_item_data.get("size", 0), # Provide default
                creation=group_item_data.get("creation", 0), # Provide default
                owner=group_item_data.get("owner"),
                restrict=group_item_data.get("restrict", False), # Provide default
                announce=group_item_data.get("announce", False), # Provide default
                is_community=group_item_data.get("isCommunity", False), # Provide default
                is_community_announce=group_item_data.get("isCommunityAnnounce", False), # Provide default
                horario=horario,
                enabled=enabled,
                is_links=is_links,
                is_names=is_names,
                send_to_group=send_to_group,
                send_to_personal=send_to_personal,
                min_messages_summary=min_messages_summary
            )
            return group_obj
        except Exception as e:
            self.logger.error("Erro ao criar objeto Group para ID %s: %s", group_id, e, exc_info=True)
            return None

    def fetch_groups(self, force_refresh=False):
        """
        PT-BR:
        Obtém lista de grupos usando cache ou API.

        Parâmetros:
            force_refresh: Força atualização da API ignorando cache

        Retorna:
            List[Group]: Lista de objetos Group

        EN:
        Gets group list using cache or API.

        Parameters:
            force_refresh: Forces API update ignoring cache

        Returns:
            List[Group]: List of Group objects
        """
        summary_data = self.load_summary_info() # Load summary data once
        groups_api_data = None # Renamed to avoid confusion with self.groups (list of Group objects)

        if not force_refresh:
            cache_data = self._load_cache()
            if cache_data and "groups" in cache_data: # Ensure 'groups' key exists
                self.logger.info("Usando dados do cache...")
                groups_api_data = cache_data["groups"]
            else:
                self.logger.info("Cache não encontrado ou inválido. Buscando da API...")
                groups_api_data = self._fetch_from_api()
                if groups_api_data is not None: # Save only if API call was successful
                    self._save_cache(groups_api_data)
        else:
            try:
                self.logger.info("Forçando atualização da API...")
                groups_api_data = self._fetch_from_api()
                if groups_api_data is not None:
                    self._save_cache(groups_api_data)
            except Exception as e: # Catching generic Exception from _fetch_from_api
                self.logger.error("Erro ao forçar atualização da API: %s. Tentando fallback para cache.", e, exc_info=True)
                # Fallback to cache if forced refresh fails
                cache_data = self._load_cache()
                if cache_data and "groups" in cache_data:
                    self.logger.warning("Rate limit atingido. Verificando cache para fallback...")
                    groups_api_data = cache_data["groups"]
                else:
                    self.logger.error("Fallback para cache falhou. Nenhum dado de grupo disponível.")
                    # Depending on desired behavior, could raise e here or return empty list
                    self.groups = []
                    return self.groups # Return empty list if API and cache fail

        self.groups = [] # Reset current groups list
        if groups_api_data:
            if not isinstance(groups_api_data, list): # Ensure API data is a list
                self.logger.error("Dados da API não são uma lista: %s", type(groups_api_data))
                return self.groups # Return empty list

            for group_item_data in groups_api_data:
                group_obj = self._create_group_object(group_item_data, summary_data)
                if group_obj:
                    self.groups.append(group_obj)
        else:
            self.logger.info("Nenhum dado de grupo recebido da API ou cache.")

        return self.groups

    def load_summary_info(self):
        """
        PT-BR:
        Carrega ou cria DataFrame com informações de resumo dos grupos.

        Retorna:
            DataFrame: Contém configurações de resumo de todos os grupos

        EN:
        Loads or creates DataFrame with group summary information.

        Returns:
            DataFrame: Contains summary settings for all groups
        """
        try:
            return pd.read_csv(self.csv_file)
        except FileNotFoundError:
            return pd.DataFrame(columns=[
                "group_id", "dias", "horario", "enabled",
                "is_links", "is_names", "send_to_group",
                "send_to_personal", "min_messages_summary"
            ])

    def load_data_by_group(self, group_id):
        """
        PT-BR:
        Carrega configurações de resumo para um grupo específico.

        Parâmetros:
            group_id: Identificador do grupo

        Retorna:
            dict/False: Dicionário com configurações ou False se não encontrado

        EN:
        Loads summary settings for a specific group.

        Parameters:
            group_id: Group identifier

        Returns:
            dict/False: Dictionary with settings or False if not found
        """
        try:
            df = self.load_summary_info()
            # Use .loc for safer access and ensure 'group_id' column exists or handle potential KeyError
            resumo_df_slice = df.loc[df["group_id"] == group_id]
            return resumo_df_slice.iloc[0].to_dict() if not resumo_df_slice.empty else False
        except KeyError: # Handle case where 'group_id' column might be missing
            self.logger.warning("Coluna 'group_id' não encontrada no DataFrame de resumo ao carregar para grupo %s.", group_id)
            return False
        except Exception as e:
            self.logger.error(f"Erro ao carregar dados de resumo para o grupo {group_id}: {e}", exc_info=True)
            return False

    def update_summary(self, group_id, horario, enabled, is_links, is_names, script, send_to_group=True, send_to_personal=False, start_date=None, start_time=None, end_date=None, end_time=None, min_messages_summary=50):
        """
        PT-BR:
        Atualiza configurações de resumo de um grupo no CSV.

        Parâmetros:
            group_id: ID do grupo
            horario: Horário de execução
            enabled: Resumo ativado
            is_links: Incluir links
            is_names: Incluir nomes
            script: Caminho do script
            send_to_group: Enviar para o grupo
            send_to_personal: Enviar para número pessoal
            start_date: Data inicial (opcional)
            start_time: Hora inicial (opcional)
            end_date: Data final (opcional)
            end_time: Hora final (opcional)
            min_messages_summary: Mínimo de mensagens para gerar resumo (opcional)

        Retorna:
            bool: True se atualizado com sucesso

        EN:
        Updates group summary settings in CSV.

        Parameters:
            group_id: Group ID
            horario: Execution time
            enabled: Summary enabled
            is_links: Include links
            is_names: Include names
            script: Script path
            send_to_group: Send to group
            send_to_personal: Send to personal number
            start_date: Start date (optional)
            start_time: Start time (optional)
            end_date: End date (optional)
            end_time: End time (optional)
            min_messages_summary: Minimum messages to generate summary (optional)

        Returns:
            bool: True if successfully updated
        """
        try:
            df = pd.read_csv(self.csv_file)
        except FileNotFoundError:
            df = pd.DataFrame(columns=["group_id", "horario", "enabled", "is_links", "is_names", "script",
                                     "send_to_group", "send_to_personal",
                                     "start_date", "start_time", "end_date", "end_time", "min_messages_summary"])

        df = df[df['group_id'] != group_id]

        nova_config = {
            "group_id": group_id,
            "horario": horario,
            "enabled": enabled,
            "is_links": is_links,
            "is_names": is_names,
            "script": script,
            "send_to_group": send_to_group,
            "send_to_personal": send_to_personal,
            "start_date": start_date if start_date else None,
            "start_time": start_time if start_time else None,
            "end_date": end_date if end_date else None,
            "end_time": end_time if end_time else None,
            "min_messages_summary": min_messages_summary
        }

        df = pd.concat([df, pd.DataFrame([nova_config])], ignore_index=True)
        df.to_csv(self.csv_file, index=False)

        return True

    def get_groups(self):
        """
        PT-BR:
        Retorna lista de grupos processada.

        Retorna:
            List[Group]: Lista atual de objetos Group

        EN:
        Returns processed group list.

        Returns:
            List[Group]: Current list of Group objects
        """
        return self.groups

    def find_group_by_id(self, group_id):
        """
        PT-BR:
        Localiza um grupo pelo seu ID.

        Parâmetros:
            group_id: ID do grupo a ser encontrado

        Retorna:
            Group/None: Objeto Group ou None se não encontrado

        EN:
        Finds a group by its ID.

        Parameters:
            group_id: Group ID to find

        Returns:
            Group/None: Group object or None if not found

        Note: This method will call `self.fetch_groups()` if `self.groups` is currently empty.
        This ensures that group data is loaded but may involve an API call if the cache is empty or stale.
        """
        if not self.groups:
            self.fetch_groups() # This might call fetch_groups if groups is empty
        for group_instance in self.groups: # Renamed to avoid conflict
            if group_instance.group_id == group_id:
                return group_instance
        return None

    def filter_groups_by_owner(self, owner):
        """
        PT-BR:
        Filtra grupos por proprietário.

        Parâmetros:
            owner: ID do proprietário

        Retorna:
            List[Group]: Lista de grupos do proprietário

        EN:
        Filters groups by owner.

        Parameters:
            owner: Owner ID

        Returns:
            List[Group]: List of owner's groups
        """
        return [group_instance for group_instance in self.groups if group_instance.owner == owner] # Renamed to avoid conflict

    def get_messages(self, group_id, start_date, end_date):
        """
        PT-BR:
        Obtém e filtra mensagens de um grupo em um período.

        Parâmetros:
            group_id: ID do grupo
            start_date: Data inicial (formato: YYYY-MM-DD HH:MM:SS)
            end_date: Data final (formato: YYYY-MM-DD HH:MM:SS)

        Retorna:
            List[Message]: Lista de mensagens filtradas

        EN:
        Gets and filters group messages within a period.

        Parameters:
            group_id: Group ID
            start_date: Start date (format: YYYY-MM-DD HH:MM:SS)
            end_date: End date (format: YYYY-MM-DD HH:MM:SS)

        Returns:
            List[Message]: List of filtered messages
        """
        self.logger.info(f"Fetching messages for group {group_id} from {start_date} to {end_date}")

        def to_iso8601(date_str):
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        timestamp_start_iso = to_iso8601(start_date)
        timestamp_end_iso = to_iso8601(end_date)

        assert self.instance_id is not None, "instance_id cannot be None"
        assert self.instance_token is not None, "instance_token cannot be None"

        group_mensagens_raw = None
        msgs_processed = []
        msgs_filtradas = []

        try:
            self.logger.info(f"Calling Evolution API: client.chat.get_messages for group {group_id}")
            group_mensagens_raw = self.client.chat.get_messages(
                instance_id=self.instance_id,
                remote_jid=group_id,
                instance_token=self.instance_token,
                timestamp_start=timestamp_start_iso,
                timestamp_end=timestamp_end_iso,
                page=1,
                offset=1000
            )
            self.logger.debug(f"Raw API response for group {group_id}: {group_mensagens_raw}")

            msgs_processed = MessageSandeco.get_messages(group_mensagens_raw)
            self.logger.info(f"Processed {len(msgs_processed)} messages by MessageSandeco for group {group_id}.")
            self.logger.debug(f"Processed messages content (first few if many): {msgs_processed[:3]}")

            data_obj = datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S")
            timestamp_limite = int(data_obj.timestamp())

            valid_messages_for_filtering = []
            for msg in msgs_processed:
                if hasattr(msg, 'message_timestamp') and msg.message_timestamp is not None:
                    try:
                        if int(msg.message_timestamp) >= timestamp_limite:
                            valid_messages_for_filtering.append(msg)
                    except ValueError:
                        self.logger.warning(f"Could not convert msg.message_timestamp '{msg.message_timestamp}' to int for comparison.")
                else:
                    self.logger.warning(f"Message object lacks 'message_timestamp' or it is None. Msg: {msg}")

            msgs_filtradas = valid_messages_for_filtering
            self.logger.info(f"Filtered messages for group {group_id}: {len(msgs_filtradas)} messages after timestamp limit.")
            self.logger.debug(f"Filtered messages content (first few if many): {msgs_filtradas[:3]}")

        except EvolutionAPIError as e:
            self.logger.error(f"Evolution API error while fetching messages for group {group_id}: {e}", exc_info=True)
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching or processing messages for group {group_id}: {e}", exc_info=True)

        return msgs_filtradas
