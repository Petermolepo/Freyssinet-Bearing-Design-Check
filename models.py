"""
BearingInput – the single data model for all 15 input parameters.
All units are as specified in the brief (mm, kN, N/mm², radians).
"""

from dataclasses import dataclass


@dataclass
class BearingInput:
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
