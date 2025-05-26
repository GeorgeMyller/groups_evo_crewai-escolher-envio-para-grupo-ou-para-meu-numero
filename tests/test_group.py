"""
Testes unitários para a classe Group / Unit tests for Group class
"""
import pytest
import sys
import os
from datetime import datetime

# Adiciona o diretório pai ao path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from group import Group


class TestGroup:
    """Testes para a classe Group"""
    
    def test_group_creation_with_defaults(self):
        """Teste de criação de grupo com valores padrão"""
        group = Group(
            group_id="120363398170141701@g.us",
            name="Teste Group",
            subject_owner="owner@s.whatsapp.net",
            subject_time=1640995200,
            picture_url="https://example.com/pic.jpg",
            size=50,
            creation=1640995200,
            owner="admin@s.whatsapp.net",
            restrict=False,
            announce=False,
            is_community=False,
            is_community_announce=False
        )
        
        # Verificar valores padrão
        assert group.group_id == "120363398170141701@g.us"
        assert group.name == "Teste Group"
        assert group.dias == 1
        assert group.horario == "22:00"
        assert group.enabled == False
        assert group.is_links == False
        assert group.is_names == False
        assert group.send_to_group == True
        assert group.send_to_personal == False
        assert group.min_messages_summary == 50
    
    def test_group_creation_with_custom_values(self):
        """Teste de criação de grupo com valores customizados"""
        group = Group(
            group_id="120363398170141701@g.us",
            name="Custom Group",
            subject_owner="owner@s.whatsapp.net",
            subject_time=1640995200,
            picture_url="https://example.com/pic.jpg",
            size=100,
            creation=1640995200,
            owner="admin@s.whatsapp.net",
            restrict=True,
            announce=True,
            is_community=True,
            is_community_announce=True,
            dias=7,
            horario="18:30",
            enabled=True,
            is_links=True,
            is_names=True,
            send_to_group=False,
            send_to_personal=True,
            min_messages_summary=100
        )
        
        # Verificar valores customizados
        assert group.dias == 7
        assert group.horario == "18:30"
        assert group.enabled == True
        assert group.is_links == True
        assert group.is_names == True
        assert group.send_to_group == False
        assert group.send_to_personal == True
        assert group.min_messages_summary == 100
    
    def test_group_repr(self):
        """Teste da representação string do grupo"""
        group = Group(
            group_id="120363398170141701@g.us",
            name="Test Group",
            subject_owner="owner@s.whatsapp.net",
            subject_time=1640995200,
            picture_url="https://example.com/pic.jpg",
            size=25,
            creation=1640995200,
            owner="admin@s.whatsapp.net",
            restrict=False,
            announce=False,
            is_community=False,
            is_community_announce=False
        )
        
        repr_str = repr(group)
        assert "Test Group" in repr_str
        assert "120363398170141701@g.us" in repr_str


if __name__ == "__main__":
    pytest.main([__file__])
