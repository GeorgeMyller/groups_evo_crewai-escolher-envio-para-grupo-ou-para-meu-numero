"""
Compatibility layer for legacy Group class

This file provides backward compatibility during migration.
Use 'from src.core.models import Group' for new code.
"""

import warnings
from src.core.models import Group

warnings.warn(
    "Importing from 'group.py' is deprecated. Use 'from src.core.models import Group' instead.",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ['Group']
