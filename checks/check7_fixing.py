"""
Check 7 – Fixing of Bearings
==============================
Two sub-checks:

a) Under all loading (D147, F149, D151):
   H      = l * b * G * delta_r / tq          [D17*D18*D31*F38/D27]
   0.1(V+2A1) = 0.1 * (Vmax*1000 + 2*A1)     [F149]
   Pass: H < 0.1*(Vmax*1000 + 2*A1)           [D151]

b) Under permanent loads (D156, D158):
   V/A1   = Vdl*1000 / A1                     [D156]
   Pass: V/A1 > 2                              [D158]

Both sub-checks must pass for Check 7 to be OK.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Check7Result:
    status: str
    intermediates: Dict[str, Any]
    message: str


def check7_fixing(
    l: float, b: float, G: float,
    delta_r: float, tq: float,
    Vmax: float, Vdl: float, A1: float,
) -> Check7Result:
    """
    Fixing of bearings check.

    Parameters
    ----------
    l       : float  Bearing length (mm)
    b       : float  Bearing width (mm)
    G       : float  Shear modulus (N/mm²)
    delta_r : float  Resultant shear displacement (mm)
    tq      : float  Total rubber thickness (mm)
    Vmax    : float  Maximum vertical load (kN)
    Vdl     : float  Dead load vertical force (kN)
    A1      : float  Effective plan area (mm²)
    """
    # a) Under all loading
    H = l * b * G * delta_r / tq                     # D147
    limit_a = 0.1 * (Vmax * 1000 + 2 * A1)          # F149
    sub_a_ok = H < limit_a                            # D151

    # b) Under permanent loads
    vdl_stress = Vdl * 1000 / A1                     # D156
    sub_b_ok = vdl_stress > 2                         # D158

    passed = sub_a_ok and sub_b_ok
    status = "OK" if passed else "FAIL"

    intermediates = {
        "H (kN)": round(H, 4),
        "0.1·(V + 2·A1) (kN)": round(limit_a, 4),
        "Sub-check a (H < limit)": sub_a_ok,
        "V/A1 permanent (N/mm²)": round(vdl_stress, 4),
        "Sub-check b (V/A1 > 2)": sub_b_ok,
    }

    message = (
        f"H = {H:.2f} kN  |  limit = {limit_a:.2f} kN  "
        f"{'✓' if sub_a_ok else '✗'}  |  "
        f"V/A1(perm) = {vdl_stress:.4f} N/mm²  "
        f"{'✓' if sub_b_ok else '✗'}  → {status}"
    )

    return Check7Result(status=status, intermediates=intermediates,
                        message=message)
