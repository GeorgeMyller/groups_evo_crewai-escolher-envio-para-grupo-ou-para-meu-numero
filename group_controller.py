"""
Compatibility layer for legacy GroupController class with cache integration

This file provides backward compatibility during migration with enhanced scalability features.
"""

import warnings
from src.core.controllers.group_controller import GroupController as NewGroupController
from infrastructure_service import get_infrastructure

class GroupController(NewGroupController):
    """Legacy GroupController with cache integration."""
    
    def __init__(self):
        # Obter serviço de cache da infraestrutura
        infrastructure = get_infrastructure()
        cache_service = infrastructure.get_cache() if infrastructure else None
        
        super().__init__(cache_service=cache_service)

warnings.warn(
    "Importing from 'group_controller.py' is deprecated. Use 'from src.core.controllers import GroupController' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['GroupController']
