"""
Source Package

PT-BR:
Este é o pacote principal do código fonte do sistema de gerenciamento
de grupos WhatsApp.

EN:
This is the main source code package for the WhatsApp group
management system.
"""

from .core import Group, SummaryRequest, GroupStats, MessageData, SummaryResult, APIResponse

__all__ = [
    'Group', 
    'SummaryRequest', 
    'GroupStats',
    'MessageData',
    'SummaryResult',
    'APIResponse'
]
