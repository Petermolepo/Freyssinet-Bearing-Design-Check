"""
bearing_types/registry.py
==========================
Extensible bearing type registry.

Each bearing type can override geometry constants (e.g. cover strip size,
bulk modulus) and check thresholds that differ from the Freyssinet plain pad
bearing defaults.

Currently implemented:
  PAD_BEARING       – Freyssinet plain elastomeric pad (fully verified)
  LAMINATED_BEARING – Laminated (steel-reinforced) bearing (same checks, different
                      geometry convention — stub, ready for calibration)

To add a new type:
  1. Define a BearingType dataclass instance below.
  2. Register it in REGISTRY.
  3. Pass --type <name> on the CLI.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class BearingType:
    """
    Encapsulates the constants and threshold overrides for a bearing type.

    Attributes
    ----------
    name            : str   Display name
    code            : str   CLI/API identifier (lowercase, underscores)
    description     : str   One-line description
    cover_strip_mm  : float Reduction applied each side of l and b to get le/be
    bulk_modulus    : float Eb (N/mm²) for vertical deflection check
    steel_yield     : float σs (N/mm²) for plate thickness check
    eq_limit        : float Shear strain pass threshold (Check 1)
    et_limit        : float Max design strain pass threshold (Check 2)
    notes           : str   Any caveats about this type
    """
    name:           str
    code:           str
    description:    str
    cover_strip_mm: float = 5.0      # each side → le = l - 2*cover_strip
    bulk_modulus:   float = 2000.0   # N/mm²
    steel_yield:    float = 290.0    # N/mm²
    eq_limit:       float = 0.7      # Check 1
    et_limit:       float = 5.0      # Check 2
    notes:          str   = ""

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name":           self.name,
            "code":           self.code,
            "description":    self.description,
            "cover_strip_mm": self.cover_strip_mm,
            "bulk_modulus":   self.bulk_modulus,
            "steel_yield":    self.steel_yield,
            "eq_limit":       self.eq_limit,
            "et_limit":       self.et_limit,
            "notes":          self.notes,
        }


# ── Type definitions ────────────────────────────────────────────────────────

PAD_BEARING = BearingType(
    name           = "Plain Elastomeric Pad Bearing",
    code           = "pad",
    description    = "Standard Freyssinet plain elastomeric pad bearing (fully verified)",
    cover_strip_mm = 5.0,
    bulk_modulus   = 2000.0,
    steel_yield    = 290.0,
    eq_limit       = 0.7,
    et_limit       = 5.0,
    notes          = "Default type. All checks calibrated against Freyssinet design manual.",
)

LAMINATED_BEARING = BearingType(
    name           = "Laminated Elastomeric Bearing",
    code           = "laminated",
    description    = "Steel-reinforced laminated bearing (stub — thresholds to be calibrated)",
    cover_strip_mm = 6.0,    # slightly larger cover strip for laminated type
    bulk_modulus   = 2000.0,
    steel_yield    = 355.0,  # higher-grade steel typically used
    eq_limit       = 0.7,
    et_limit       = 5.0,
    notes          = "STUB: geometry uses 6 mm cover strip and 355 N/mm² steel. "
                     "Thresholds identical to PAD_BEARING pending calibration.",
)

POT_BEARING = BearingType(
    name           = "Pot Bearing (stub)",
    code           = "pot",
    description    = "Pot bearing — structural placeholder, not yet implemented",
    cover_strip_mm = 5.0,
    bulk_modulus   = 2000.0,
    steel_yield    = 290.0,
    eq_limit       = 0.7,
    et_limit       = 5.0,
    notes          = "STUB: Not yet implemented. Checks will run using PAD_BEARING logic.",
)


# ── Registry ────────────────────────────────────────────────────────────────

REGISTRY: Dict[str, BearingType] = {
    bt.code: bt for bt in [PAD_BEARING, LAMINATED_BEARING, POT_BEARING]
}


def get_bearing_type(code: str) -> BearingType:
    """Return a BearingType by code. Raises ValueError if unknown."""
    code = code.lower().strip()
    if code not in REGISTRY:
        valid = ", ".join(REGISTRY.keys())
        raise ValueError(
            f"Unknown bearing type '{code}'. Valid options: {valid}"
        )
    return REGISTRY[code]


def list_bearing_types() -> list:
    """Return a list of all registered bearing types as dicts."""
    return [bt.as_dict() for bt in REGISTRY.values()]
