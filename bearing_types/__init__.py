"""
bearing_types/ package — Pad, laminated, pot bearing settings
===========================================================
Each type can change cover strip, steel grade, and pass limits.
See bearing_types/README.md and registry.py.
"""

from .registry import BearingType, get_bearing_type, list_bearing_types

# Mark as public API for consumers; also avoids pyflakes "imported but unused".
__all__ = ["BearingType", "get_bearing_type", "list_bearing_types"]
_ = (BearingType, get_bearing_type, list_bearing_types)
