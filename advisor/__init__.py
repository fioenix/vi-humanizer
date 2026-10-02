"""Optional TypeSafe advisor for vi-humanizer.

The Markdown skill remains fully usable without importing this package.
"""

from .models import PINNED_MODEL, SCHEMA_VERSION

__all__ = ["PINNED_MODEL", "SCHEMA_VERSION"]
