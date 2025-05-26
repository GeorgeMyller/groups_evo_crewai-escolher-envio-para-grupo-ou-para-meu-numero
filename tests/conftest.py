"""
Configuração pytest para testes / Pytest configuration for tests
"""
import sys
import os

# Adiciona o diretório raiz do projeto ao Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configurações do pytest
def pytest_configure():
    """Configuração inicial do pytest"""
    pass
