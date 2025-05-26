"""
Testes unitários para GroupController / Unit tests for GroupController
"""
import pytest
import sys
import os
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from group_controller import GroupController
from group import Group


class TestGroupController:
    """Testes para a classe GroupController"""
    
    @pytest.fixture
    def mock_controller(self):
        """Fixture para criar um controller com configurações mockadas"""
        with patch.dict(os.environ, {
            'EVO_BASE_URL': 'http://localhost:8081',
            'EVO_API_TOKEN': 'test_token',
            'EVO_INSTANCE_NAME': 'test_instance',
            'EVO_INSTANCE_TOKEN': 'test_instance_token'
        }):
            controller = GroupController()
            return controller
    
    @pytest.fixture
    def sample_group_data(self):
        """Dados de exemplo para testes"""
        return {
            'group_id': '120363398170141701@g.us',
            'name': 'Test Group',
            'subject_owner': 'owner@s.whatsapp.net',
            'subject_time': 1640995200,
            'picture_url': 'https://example.com/pic.jpg',
            'size': 50,
            'creation': 1640995200,
            'owner': 'admin@s.whatsapp.net',
            'restrict': False,
            'announce': False,
            'is_community': False,
            'is_community_announce': False
        }
    
    def test_environment_validation(self, mock_controller):
        """Teste de validação das variáveis de ambiente"""
        assert mock_controller.base_url == 'http://localhost:8081'
        assert mock_controller.api_token == 'test_token'
        assert mock_controller.instance_id == 'test_instance'
        assert mock_controller.instance_token == 'test_instance_token'
    
    @patch('pandas.read_csv')
    def test_load_summary_info_existing_file(self, mock_read_csv, mock_controller):
        """Teste de carregamento de arquivo CSV existente"""
        # Arrange
        mock_df = pd.DataFrame({
            'group_id': ['120363398170141701@g.us'],
            'horario': ['22:00'],
            'enabled': [True],
            'is_links': [False],
            'is_names': [False],
            'send_to_group': [True],
            'send_to_personal': [False],
            'min_messages_summary': [50]
        })
        mock_read_csv.return_value = mock_df
        
        # Act
        result = mock_controller.load_summary_info()
        
        # Assert
        assert not result.empty
        assert len(result) == 1
        assert result.iloc[0]['group_id'] == '120363398170141701@g.us'
    
    @patch('pandas.read_csv')
    def test_load_summary_info_file_not_found(self, mock_read_csv, mock_controller):
        """Teste quando arquivo CSV não existe"""
        # Arrange
        mock_read_csv.side_effect = FileNotFoundError()
        
        # Act
        result = mock_controller.load_summary_info()
        
        # Assert
        assert result.empty
        expected_columns = [
            "group_id", "dias", "horario", "enabled", 
            "is_links", "is_names", "send_to_group", 
            "send_to_personal", "min_messages_summary"
        ]
        assert list(result.columns) == expected_columns
    
    @patch('pandas.DataFrame.to_csv')
    @patch('pandas.read_csv')
    def test_update_summary_new_group(self, mock_read_csv, mock_to_csv, mock_controller):
        """Teste de atualização de resumo para novo grupo"""
        # Arrange
        mock_read_csv.side_effect = FileNotFoundError()
        
        # Act
        result = mock_controller.update_summary(
            group_id='120363398170141701@g.us',
            horario='22:00',
            enabled=True,
            is_links=False,
            is_names=False,
            script='/path/to/script.py',
            send_to_group=True,
            send_to_personal=False,
            min_messages_summary=50
        )
        
        # Assert
        assert result == True
        mock_to_csv.assert_called_once()
    
    @patch('pandas.DataFrame.to_csv')
    @patch('pandas.read_csv')
    def test_update_summary_existing_group(self, mock_read_csv, mock_to_csv, mock_controller):
        """Teste de atualização de resumo para grupo existente"""
        # Arrange
        existing_df = pd.DataFrame({
            'group_id': ['120363398170141701@g.us', 'other_group@g.us'],
            'horario': ['21:00', '20:00'],
            'enabled': [False, True],
            'is_links': [True, False],
            'is_names': [True, False],
            'script': ['/old/script.py', '/other/script.py'],
            'send_to_group': [True, True],
            'send_to_personal': [False, False],
            'start_date': [None, None],
            'start_time': [None, None],
            'end_date': [None, None],
            'end_time': [None, None],
            'min_messages_summary': [30, 50]
        })
        mock_read_csv.return_value = existing_df
        
        # Act
        result = mock_controller.update_summary(
            group_id='120363398170141701@g.us',
            horario='22:00',
            enabled=True,
            is_links=False,
            is_names=False,
            script='/new/script.py',
            send_to_group=True,
            send_to_personal=True,
            min_messages_summary=75
        )
        
        # Assert
        assert result == True
        mock_to_csv.assert_called_once()
    
    @patch('pandas.read_csv')
    def test_load_data_by_group_found(self, mock_read_csv, mock_controller):
        """Teste de carregamento de dados por grupo - grupo encontrado"""
        # Arrange
        mock_df = pd.DataFrame({
            'group_id': ['120363398170141701@g.us', 'other_group@g.us'],
            'horario': ['22:00', '20:00'],
            'enabled': [True, False],
            'is_links': [False, True],
            'is_names': [False, True],
            'min_messages_summary': [50, 30]
        })
        mock_read_csv.return_value = mock_df
        
        # Act
        result = mock_controller.load_data_by_group('120363398170141701@g.us')
        
        # Assert
        assert result is not False
        assert result['group_id'] == '120363398170141701@g.us'
        assert result['horario'] == '22:00'
        assert result['enabled'] == True
    
    @patch('pandas.read_csv')
    def test_load_data_by_group_not_found(self, mock_read_csv, mock_controller):
        """Teste de carregamento de dados por grupo - grupo não encontrado"""
        # Arrange
        mock_df = pd.DataFrame({
            'group_id': ['other_group@g.us'],
            'horario': ['20:00'],
            'enabled': [False]
        })
        mock_read_csv.return_value = mock_df
        
        # Act
        result = mock_controller.load_data_by_group('nonexistent@g.us')
        
        # Assert
        assert result is False
    
    def test_find_group_by_id_found(self, mock_controller):
        """Teste de busca de grupo por ID - grupo encontrado"""
        # Arrange
        sample_group = Group(
            group_id='120363398170141701@g.us',
            name='Test Group',
            subject_owner='owner@s.whatsapp.net',
            subject_time=1640995200,
            picture_url='https://example.com/pic.jpg',
            size=50,
            creation=1640995200,
            owner='admin@s.whatsapp.net',
            restrict=False,
            announce=False,
            is_community=False,
            is_community_announce=False
        )
        mock_controller.groups = [sample_group]
        
        # Act
        result = mock_controller.find_group_by_id('120363398170141701@g.us')
        
        # Assert
        assert result is not None
        assert result.group_id == '120363398170141701@g.us'
        assert result.name == 'Test Group'
    
    def test_find_group_by_id_not_found(self, mock_controller):
        """Teste de busca de grupo por ID - grupo não encontrado"""
        # Arrange
        mock_controller.groups = []
        
        # Act
        result = mock_controller.find_group_by_id('nonexistent@g.us')
        
        # Assert
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__])
