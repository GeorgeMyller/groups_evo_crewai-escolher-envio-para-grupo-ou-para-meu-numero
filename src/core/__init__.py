"""
Core Package

PT-BR:
Este pacote contém os componentes principais do sistema de gerenciamento
de grupos WhatsApp.

EN:
This package contains the core components of the WhatsApp group
management system.
"""

# Import models without controllers to avoid dependency issues
from .models import Group, SummaryRequest, GroupStats, MessageData, SummaryResult, APIResponse

__all__ = [
    'Group', 
    'SummaryRequest', 
    'GroupStats', 
    'MessageData', 
    'SummaryResult', 
    'APIResponse'
]
