"""
Compatibility layer for legacy GroupController class

This file provides backward compatibility during migration.
Use 'from src.core.controllers import GroupController' for new code.
"""

import warnings
from src.core.controllers import GroupController

warnings.warn(
    "Importing from 'group_controller.py' is deprecated. Use 'from src.core.controllers import GroupController' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['GroupController']
