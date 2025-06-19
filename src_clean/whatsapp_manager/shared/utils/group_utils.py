"""
Utilitários para Gerenciamento de Grupos / Group Management Utilities

PT-BR:
Esta classe fornece ferramentas para manipulação de imagens de grupos,
formatação de datas, e apresentação de informações na interface do usuário.

EN:
This class provides tools for handling group images, date formatting,
and presenting information in the user interface.
"""

import base64
from datetime import datetime
from io import BytesIO
from typing import Optional, Tuple, Union, Any
import logging

# Third-party library imports
import pandas as pd
import requests

# Optional imports for UI functionality
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None


# Set up logging
logger = logging.getLogger(__name__)


class GroupUtilsService:
    """
    Group management utilities service providing image processing,
    date formatting, and UI helper functions.
    """
    
    def __init__(self):
        """Initialize the group utils service."""
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check for optional dependencies and log warnings if missing."""
        if not PIL_AVAILABLE:
            logger.warning("PIL (Pillow) not available. Image processing features will be limited.")
        
        if not STREAMLIT_AVAILABLE:
            logger.warning("Streamlit not available. UI features will be limited.")
    
    def resized_image_to_base64(self, image: Any) -> str:
        """
        PT-BR:
        Converte uma imagem redimensionada para string base64.
        
        Parâmetros:
            image: Imagem PIL para converter
            
        Retorna:
            str: String base64 da imagem

        EN:
        Converts a resized image to base64 string.
        
        Parameters:
            image: PIL Image to convert
            
        Returns:
            str: Base64 string of the image
            
        Raises:
            ValueError: If PIL is not available or image is invalid
        """
        if not PIL_AVAILABLE:
            raise ValueError("PIL (Pillow) is required for image processing")
        
        if not image:
            raise ValueError("Invalid image provided")
        
        try:
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to convert image to base64: {str(e)}") from e
    
    def format_date(self, timestamp: Union[int, str, float]) -> str:
        """
        PT-BR:
        Formata um timestamp Unix para data legível.
        
        Parâmetros:
            timestamp: Timestamp Unix
            
        Retorna:
            str: Data formatada (DD-MM-YYYY HH:MM)

        EN:
        Formats a Unix timestamp to readable date.
        
        Parameters:
            timestamp: Unix timestamp
            
        Returns:
            str: Formatted date (DD-MM-YYYY HH:MM)
        """
        try:
            # Handle different timestamp formats
            if isinstance(timestamp, str):
                timestamp = float(timestamp)
            elif isinstance(timestamp, int):
                timestamp = float(timestamp)
            
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime("%d-%m-%Y %H:%M")
        except (ValueError, TypeError, OSError) as e:
            logger.warning(f"Failed to format timestamp {timestamp}: {str(e)}")
            return "Data inválida / Invalid date"
    
    def get_image(self, url: str, size: Tuple[int, int] = (30, 30)) -> Optional[Any]:
        """
        PT-BR:
        Obtém e redimensiona uma imagem de uma URL.
        
        Parâmetros:
            url: URL da imagem
            size: Tuple com dimensões desejadas (largura, altura)
            
        Retorna:
            Image: Imagem PIL processada ou None se houver erro

        EN:
        Obtains and resizes an image from a URL.
        
        Parameters:
            url: Image URL
            size: Tuple with desired dimensions (width, height)
            
        Returns:
            Image: Processed PIL Image or None if error
        """
        if not PIL_AVAILABLE:
            logger.warning("PIL (Pillow) is required for image processing")
            return None
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            if Image is not None:
                image = Image.open(BytesIO(response.content))
                image = image.resize(size, Image.Resampling.LANCZOS)
                return image
            else:
                return None
            
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch image from {url}: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Failed to process image from {url}: {str(e)}")
            return None
    
    def format_group_info(self, group_data: dict) -> dict:
        """
        PT-BR:
        Formata informações do grupo para exibição.
        
        Parâmetros:
            group_data: Dados brutos do grupo
            
        Retorna:
            dict: Dados formatados do grupo

        EN:
        Formats group information for display.
        
        Parameters:
            group_data: Raw group data
            
        Returns:
            dict: Formatted group data
        """
        try:
            formatted_data = group_data.copy()
            
            # Format timestamps if present
            timestamp_fields = ['creation_time', 'last_message_time', 'updated_at']
            for field in timestamp_fields:
                if field in formatted_data and formatted_data[field]:
                    formatted_data[f"{field}_formatted"] = self.format_date(formatted_data[field])
            
            # Ensure required fields have default values
            defaults = {
                'name': 'Unnamed Group',
                'description': 'No description available',
                'participant_count': 0,
                'message_count': 0
            }
            
            for key, default_value in defaults.items():
                if key not in formatted_data or formatted_data[key] is None:
                    formatted_data[key] = default_value
            
            return formatted_data
            
        except Exception as e:
            logger.error(f"Failed to format group info: {str(e)}")
            return group_data
    
    def create_group_summary_df(self, groups_data: list) -> pd.DataFrame:
        """
        PT-BR:
        Cria um DataFrame pandas com resumo dos grupos.
        
        Parâmetros:
            groups_data: Lista de dados dos grupos
            
        Retorna:
            DataFrame: Resumo dos grupos em formato tabular

        EN:
        Creates a pandas DataFrame with group summary.
        
        Parameters:
            groups_data: List of group data
            
        Returns:
            DataFrame: Group summary in tabular format
        """
        try:
            if not groups_data:
                return pd.DataFrame()
            
            # Format each group
            formatted_groups = [self.format_group_info(group) for group in groups_data]
            
            # Create DataFrame
            df = pd.DataFrame(formatted_groups)
            
            # Select and rename columns for display
            display_columns = {
                'name': 'Nome do Grupo / Group Name',
                'participant_count': 'Participantes / Participants',
                'message_count': 'Mensagens / Messages',
                'creation_time_formatted': 'Criado em / Created at',
                'last_message_time_formatted': 'Última Mensagem / Last Message'
            }
            
            # Filter and rename columns that exist
            available_columns = {k: v for k, v in display_columns.items() if k in df.columns}
            df = df[list(available_columns.keys())].rename(columns=available_columns)
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to create group summary DataFrame: {str(e)}")
            return pd.DataFrame()
    
    def display_group_card(self, group_data: dict) -> None:
        """
        PT-BR:
        Exibe um cartão de grupo usando Streamlit (se disponível).
        
        Parâmetros:
            group_data: Dados do grupo para exibir

        EN:
        Displays a group card using Streamlit (if available).
        
        Parameters:
            group_data: Group data to display
        """
        if not STREAMLIT_AVAILABLE:
            logger.warning("Streamlit not available. Cannot display group card.")
            return
        
        try:
            formatted_data = self.format_group_info(group_data)
            
            if st is not None:
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    
                    with col1:
                        # Display group image if available
                        if 'image_url' in formatted_data and formatted_data['image_url']:
                            image = self.get_image(formatted_data['image_url'])
                            if image:
                                st.image(image, width=60)
                        else:
                            st.write("📱")  # Default icon
                    
                    with col2:
                        st.subheader(formatted_data['name'])
                        st.write(f"**Participantes:** {formatted_data['participant_count']}")
                        st.write(f"**Mensagens:** {formatted_data['message_count']}")
                        
                        if 'creation_time_formatted' in formatted_data:
                            st.write(f"**Criado:** {formatted_data['creation_time_formatted']}")
                        
                        if 'description' in formatted_data and formatted_data['description']:
                            st.write(f"**Descrição:** {formatted_data['description']}")
                    
                    st.divider()
                
        except Exception as e:
            logger.error(f"Failed to display group card: {str(e)}")
            if st is not None:
                st.error(f"Erro ao exibir grupo: {str(e)}")
    
    def validate_image_url(self, url: str) -> bool:
        """
        PT-BR:
        Valida se uma URL de imagem é acessível.
        
        Parâmetros:
            url: URL da imagem para validar
            
        Retorna:
            bool: True se a URL é válida e acessível

        EN:
        Validates if an image URL is accessible.
        
        Parameters:
            url: Image URL to validate
            
        Returns:
            bool: True if URL is valid and accessible
        """
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200 and 'image' in response.headers.get('content-type', '')
        except Exception:
            return False

    def create_group_options_map(self, groups: list[Any]) -> Tuple[dict, list]:
        """
        Creates a map of group IDs to group objects and a list of options for selectbox.
        """
        if not groups:
            return {}, []
        group_map = {group.group_id: group for group in groups}
        options = [(group.name, group.group_id) for group in groups]
        return group_map, options

    def create_group_header_display(self, group_name: str, picture_url: Optional[str]) -> str:
        """
        Creates an HTML string for displaying the group header with an image.
        """
        image_html = ""
        if picture_url and self.validate_image_url(picture_url):
            try:
                image = self.get_image(picture_url, size=(50, 50))
                if image:
                    b64_image = self.resized_image_to_base64(image)
                    image_html = f'<img src="data:image/png;base64,{b64_image}" style="border-radius:50%; margin-right:10px; vertical-align:middle;">'
            except Exception as e:
                logger.error(f"Failed to process image for group header: {e}")
                image_html = "🖼️"  # Fallback emoji
        else:
            image_html = "🖼️"

        return f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                {image_html}
                <h2 style="margin: 0;">{group_name}</h2>
            </div>
        """

    def display_group_details(self, group: Any) -> None:
        """
        Displays detailed information about a group using Streamlit.
        """
        if not STREAMLIT_AVAILABLE:
            logger.warning("Streamlit not available. Cannot display group details.")
            return

        if st:
            st.write(f"**ID do Grupo:** `{group.group_id}`")
            st.write(f"**Participantes:** {getattr(group, 'participants_count', 'N/A')}")
            if getattr(group, 'creation_date', None):
                st.write(f"**Data de Criação:** {self.format_date(group.creation_date)}")
            if getattr(group, 'description', None):
                with st.expander("Descrição do Grupo"):
                    st.write(group.description)
