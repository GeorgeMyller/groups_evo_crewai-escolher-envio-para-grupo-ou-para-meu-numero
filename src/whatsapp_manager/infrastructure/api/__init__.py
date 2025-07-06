"""
API - Clientes para APIs Externas
API - External API Clients

Wrappers e adaptadores para APIs externas como Evolution API.
Wrappers and adapters for external APIs like Evolution API.
"""

from .evolution_client import EvolutionClientWrapper

# Alias for backward compatibility
EvolutionAPIClient = EvolutionClientWrapper

__all__ = [
    'EvolutionClientWrapper',
    'EvolutionAPIClient'
]
