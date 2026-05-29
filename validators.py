"""
validators.py
=============
Validates a raw dict (from CLI / JSON) before constructing BearingInput.
Returns a list of error strings. Empty list means input is clean.
"""

from typing import Any, Dict, List


# Parameters that must be strictly positive (> 0)
_POSITIVE_FIELDS = [
    "l", "b", "T", "plate_thk", "no_plates",
    "te", "ti", "G", "Vmax",
]

# Parameters that must be non-negative (>= 0)
_NON_NEG_FIELDS = [
    "Vdl", "Vll", "Hs", "Ht",
    "long_mvmt", "trans_mvmt",
    "alpha_b", "alpha_l",
]

_ALL_FIELDS = _POSITIVE_FIELDS + _NON_NEG_FIELDS

# Human-readable descriptions for error messages
_DESCRIPTIONS: Dict[str, str] = {
    "l":          "Bearing length (mm)",
    "b":          "Bearing width (mm)",
    "T":          "Total bearing height (mm)",
    "plate_thk":  "Steel plate thickness (mm)",
    "no_plates":  "Number of steel plates",
    "te":         "Edge rubber layer thickness (mm)",
    "ti":         "Internal rubber layer thickness (mm)",
    "G":          "Shear modulus (N/mm²)",
    "Vmax":       "Maximum vertical load (kN)",
    "Vdl":        "Dead load vertical force (kN)",
    "Vll":        "Live load vertical force (kN)",
    "Hs":         "Longitudinal horizontal shear force (kN)",
    "Ht":         "Transverse horizontal shear force (kN)",
    "long_mvmt":  "Longitudinal movement (mm)",
    "trans_mvmt": "Transverse movement (mm)",
    "alpha_b":    "Rotation alpha_b (radians)",
    "alpha_l":    "Rotation alpha_l (radians)",
}


def validate(data: Dict[str, Any]) -> List[str]:
    """
    Validate raw input dictionary.

    Returns
    -------
    List[str]
        List of human-readable error messages. Empty = valid.
    """
    errors: List[str] = []

    # 1. Check all required fields are present
    for field in _ALL_FIELDS:
        if field not in data:
            errors.append(
                f"MISSING: '{field}' ({_DESCRIPTIONS.get(field, field)}) is required."
            )

    if errors:
        return errors   # No point continuing if fields are missing

    # 2. Check types are numeric
    for field in _ALL_FIELDS:
        val = data[field]
        if field == "no_plates":
            try:
                int(val)
            except (TypeError, ValueError):
                errors.append(
                    f"TYPE ERROR: '{field}' must be an integer, got {repr(val)}."
                )
        else:
            try:
                float(val)
            except (TypeError, ValueError):
                errors.append(
                    f"TYPE ERROR: '{field}' ({_DESCRIPTIONS.get(field, field)}) "
                    f"must be a number, got {repr(val)}."
                )

    if errors:
        return errors

    # 3. Range checks
    for field in _POSITIVE_FIELDS:
        val = float(data[field])
        if val <= 0:
            errors.append(
                f"RANGE ERROR: '{field}' ({_DESCRIPTIONS[field]}) must be > 0, got {val}."
            )

    for field in _NON_NEG_FIELDS:
        val = float(data[field])
        if val < 0:
            errors.append(
                f"RANGE ERROR: '{field}' ({_DESCRIPTIONS[field]}) must be >= 0, got {val}."
            )

    # 4. Logical consistency checks
    no_plates = int(data["no_plates"])
    if no_plates < 2:
        errors.append(
            "LOGIC ERROR: 'no_plates' must be >= 2 "
            "(at least 2 plates needed for 1 rubber layer)."
        )

    Vmax = float(data["Vmax"])
    Vdl  = float(data["Vdl"])
    Vll  = float(data["Vll"])

    if Vdl > Vmax:
        errors.append(
            f"LOGIC ERROR: 'Vdl' ({Vdl} kN) cannot exceed 'Vmax' ({Vmax} kN)."
        )
    if Vll > Vmax:
        errors.append(
            f"LOGIC ERROR: 'Vll' ({Vll} kN) cannot exceed 'Vmax' ({Vmax} kN)."
        )

    T        = float(data["T"])
    plate_thk = float(data["plate_thk"])
    te       = float(data["te"])
    ti       = float(data["ti"])

    # Total rubber thickness must be positive
    tq = T - (no_plates * plate_thk)
    if tq <= 0:
        errors.append(
            f"LOGIC ERROR: Computed total rubber thickness tq = T - (no_plates × plate_thk) "
            f"= {T} - ({no_plates} × {plate_thk}) = {tq:.2f} mm. Must be > 0."
        )

    # te and ti must not exceed tq
    if te > T:
        errors.append(
            f"LOGIC ERROR: 'te' ({te} mm) exceeds total height T ({T} mm)."
        )
    if ti > T:
        errors.append(
            f"LOGIC ERROR: 'ti' ({ti} mm) exceeds total height T ({T} mm)."
        )

    return errors
