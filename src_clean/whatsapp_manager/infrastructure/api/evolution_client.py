"""
Wrapper para Evolution API / Evolution API Wrapper

PT-BR:
Este wrapper encapsula a funcionalidade da Evolution API,
fornecendo uma interface simplificada e tratamento de erros.

EN:
This wrapper encapsulates Evolution API functionality,
providing a simplified interface and error handling.
"""

from typing import List, Dict, Any, Optional
from evolutionapi.client import EvolutionClient
from evolutionapi.exceptions import EvolutionAuthenticationError, EvolutionAPIError
import time


class EvolutionClientWrapper:
    """
    Wrapper para o cliente Evolution API
    Wrapper for Evolution API client
    """
    
    def __init__(self, base_url: str, api_token: str, instance_id: str, instance_token: str):
        """
        Inicializa o wrapper da Evolution API
        Initializes Evolution API wrapper
        """
        self.base_url = base_url
        self.api_token = api_token
        self.instance_id = instance_id
        self.instance_token = instance_token
        
        # Validar parâmetros obrigatórios
        if not all([base_url, api_token, instance_id, instance_token]):
            raise ValueError("Todos os parâmetros de configuração são obrigatórios")
        
        # Inicializar cliente
        self.client = EvolutionClient(base_url=base_url, api_token=api_token)
        
        # Configurações de retry
        self.max_retries = 3
        self.retry_delays = [60, 120, 300]  # Segundos entre tentativas
    
    def fetch_all_groups(self, get_participants: bool = False) -> List[Dict[str, Any]]:
        """
        Busca todos os grupos da instância
        Fetches all groups from instance
        
        Args:
            get_participants: Se deve buscar participantes dos grupos
            
        Returns:
            Lista de grupos
        """
        for attempt in range(self.max_retries):
            try:
                print(f"Tentativa {attempt + 1}: Buscando grupos da API")
                
                groups = self.client.group.fetch_all_groups(
                    instance_id=self.instance_id,
                    instance_token=self.instance_token,
                    get_participants=get_participants
                )
                
                print(f"✅ Sucesso: {len(groups)} grupos encontrados")
                return groups
                
            except EvolutionAuthenticationError as e:
                error_msg = f"Erro de autenticação: {str(e)}"
                print(error_msg)
                raise EvolutionAuthenticationError(error_msg)
                
            except EvolutionAPIError as e:
                if "rate-overlimit" in str(e).lower():
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delays[attempt]
                        print(f"Rate limit atingido. Aguardando {delay}s antes da próxima tentativa...")
                        time.sleep(delay)
                        continue
                    else:
                        raise EvolutionAPIError("Rate limit excedido após múltiplas tentativas")
                else:
                    raise e
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    delay = self.retry_delays[attempt]
                    print(f"Erro na tentativa {attempt + 1}: {str(e)}")
                    print(f"Aguardando {delay}s antes da próxima tentativa...")
                    time.sleep(delay)
                    continue
                else:
                    raise e
        
        raise Exception("Falha ao buscar grupos após múltiplas tentativas")
    
    def get_group_messages(
        self,
        group_id: str,
        timestamp_start: int,
        timestamp_end: int,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Obtém mensagens de um grupo em período específico
        Gets messages from a group in specific period
        
        Args:
            group_id: ID do grupo
            timestamp_start: Timestamp inicial
            timestamp_end: Timestamp final
            limit: Limite de mensagens
            
        Returns:
            Lista de mensagens
        """
        try:
            # Converter timestamps para formato ISO
            start_iso = self._timestamp_to_iso(timestamp_start)
            end_iso = self._timestamp_to_iso(timestamp_end)
            
            messages = self.client.chat.get_messages(
                instance_id=self.instance_id,
                remote_jid=group_id,
                instance_token=self.instance_token,
                timestamp_start=start_iso,
                timestamp_end=end_iso,
                page=1,
                offset=limit
            )
            
            return messages
            
        except Exception as e:
            print(f"Erro ao buscar mensagens do grupo {group_id}: {e}")
            return []
    
    def send_text_message(self, remote_jid: str, text: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto
        Sends text message
        
        Args:
            remote_jid: ID do destinatário (grupo ou contato)
            text: Texto da mensagem
            
        Returns:
            Resposta da API
        """
        try:
            response = self.client.message.send_text_message(
                instance_id=self.instance_id,
                instance_token=self.instance_token,
                remote_jid=remote_jid,
                text=text
            )
            
            return response
            
        except Exception as e:
            print(f"Erro ao enviar mensagem para {remote_jid}: {e}")
            raise e
    
    def check_connection_status(self) -> Dict[str, Any]:
        """
        Verifica status da conexão WhatsApp
        Checks WhatsApp connection status
        
        Returns:
            Status da conexão
        """
        try:
            # Verificar status da instância
            instance_info = self.client.instance.get_status(
                instance_id=self.instance_id,
                instance_token=self.instance_token
            )
            
            # Extrair informações relevantes
            state = instance_info.get("state", "unknown")
            is_connected = state == "open"
            
            return {
                "connected": is_connected,
                "state": state,
                "instance_id": self.instance_id,
                "instance_info": instance_info
            }
            
        except Exception as e:
            print(f"Erro ao verificar status da conexão: {e}")
            return {
                "connected": False,
                "state": "error",
                "error": str(e),
                "instance_id": self.instance_id
            }
    
    def is_instance_connected(self) -> bool:
        """
        Verifica se a instância está conectada.
        Checks if the instance is connected.
        
        Returns:
            True se conectada, False caso contrário.
        """
        status = self.check_connection_status()
        return status.get("connected", False)

    def get_qr_code(self) -> Optional[Dict[str, Any]]:
        """
        Obtém QR code para conexão
        Gets QR code for connection
        
        Returns:
            Dados do QR code ou None
        """
        try:
            qr_data = self.client.instance.get_qr_code(
                instance_id=self.instance_id,
                instance_token=self.instance_token
            )
            
            return qr_data
            
        except Exception as e:
            print(f"Erro ao obter QR code: {e}")
            return None
    
    def _timestamp_to_iso(self, timestamp: int) -> str:
        """
        Converte timestamp para formato ISO
        Converts timestamp to ISO format
        """
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def ping_api(self) -> bool:
        """
        Testa conectividade básica com a API
        Tests basic API connectivity
        """
        try:
            # Tentar uma operação simples
            self.client.instance.get_status(
                instance_id=self.instance_id,
                instance_token=self.instance_token
            )
            return True
        except Exception:
            return False
