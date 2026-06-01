"""
models.py — Input data container
================================
One class holds every number the engineer types in (15 fields).
Used by CLI, web API, batch CSV, and all checks.
Units: mm, kN, N/mm², radians (same as the Freyssinet spreadsheet).
"""

from dataclasses import dataclass


@dataclass
class BearingInput:
    """
    All bearing inputs in one place.
    The engine never reads raw dicts — it always uses this class.
    """
    # --- Bearing dimensions ---
    l: float           # Bearing length (mm)
    b: float           # Bearing width (mm)
    T: float           # Total bearing height (mm)

    # --- Plate geometry ---
    plate_thk: float   # Reinforcing steel plate thickness (mm)
    no_plates: int     # Number of steel plates
    # no_layers is derived: no_plates - 1

    # --- Rubber layer thicknesses ---
    te: float          # Edge rubber layer thickness (mm)
    ti: float          # Internal rubber layer thickness (mm)

    # --- Material ---
    G: float           # Shear modulus of rubber (N/mm²)

    # --- Vertical forces ---
    Vmax: float        # Maximum vertical force (kN)
    Vdl: float         # Dead load vertical force (kN)
    Vll: float         # Live load vertical force (kN)

    # --- Horizontal shear forces ---
    Hs: float          # Longitudinal horizontal shear force (kN)
    Ht: float          # Transverse horizontal shear force (kN)

    # --- Applied movements ---
    long_mvmt: float   # Longitudinal movement (mm)
    trans_mvmt: float  # Transverse movement (mm)

    # --- Applied rotations ---
    alpha_b: float     # Rotation about transverse axis (radians)
    alpha_l: float     # Rotation about longitudinal axis (radians)
