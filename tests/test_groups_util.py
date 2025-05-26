"""
Testes unitários para GroupsUtil / Unit tests for GroupsUtil class
"""
import pytest
import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groups_util import GroupUtils
from group import Group


class TestGroupUtils:
    """Testes para a classe GroupUtils"""
    
    def setUp(self):
        """Setup para os testes"""
        self.utils = GroupUtils()
    
    def test_format_date(self):
        """Teste de formatação de data"""
        utils = GroupUtils()
        
        # Teste com timestamp
        timestamp = 1640995200
        formatted = utils.format_date(timestamp)
        
        assert isinstance(formatted, str)
        assert len(formatted) > 0
    
    def test_status_icon(self):
        """Teste de ícones de status"""
        utils = GroupUtils()
        
        # Teste com valor True
        assert utils.status_icon(True) == "✅"
        
        # Teste com valor False
        assert utils.status_icon(False) == "❌"
    
    def test_map_groups(self):
        """Teste de mapeamento de grupos"""
        utils = GroupUtils()
        
        # Criar grupos de teste
        groups = [
            Group(
                group_id="120363398170141701@g.us",
                name="Grupo Teste 1",
                subject_owner="owner1@s.whatsapp.net",
                subject_time=1640995200,
                picture_url="https://example.com/pic1.jpg",
                size=25,
                creation=1640995200,
                owner="admin1@s.whatsapp.net",
                restrict=False,
                announce=False,
                is_community=False,
                is_community_announce=False
            ),
            Group(
                group_id="120363398170141702@g.us",
                name="Grupo Teste 2",
                subject_owner="owner2@s.whatsapp.net",
                subject_time=1640995200,
                picture_url="https://example.com/pic2.jpg",
                size=50,
                creation=1640995200,
                owner="admin2@s.whatsapp.net",
                restrict=False,
                announce=False,
                is_community=False,
                is_community_announce=False
            )
        ]
        
        group_map, options = utils.map(groups)
        
        # Verificar se o mapeamento foi criado corretamente
        assert isinstance(group_map, dict)
        assert isinstance(options, list)
        assert len(group_map) == 2
        assert len(options) == 2
        assert "Grupo Teste 1" in options
        assert "Grupo Teste 2" in options


if __name__ == "__main__":
    pytest.main([__file__])
