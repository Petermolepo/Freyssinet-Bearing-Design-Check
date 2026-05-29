"""
Check 4 – Stability
====================
Spreadsheet cells:
  D88  = V/A1    = Vmax*1000 / A1              (stress check)
  F90  = (2*be*G*S') / (3*sum_ti)             (stability limit)
           where S' = S (shape factor, same variable, spreadsheet reuses D39)
  D92  = be/4                                  (geometry limit)
  D94  = IF((D88 < F90) AND (D28 < D92), "OK!", "FAILS!")
           i.e.: V/A1 < stability_limit  AND  sum_ti < be/4

  Both sub-conditions must be true to pass.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Check4Result:
    status: str
    intermediates: Dict[str, Any]
    message: str


def check4_stability(
    Vmax: float, A1: float,
    be: float, G: float, S: float,
    sum_ti: float,
) -> Check4Result:
    """
    Stability check.

    Parameters
    ----------
    Vmax    : float  Maximum vertical load (kN)
    A1      : float  Effective plan area (mm²)
    be      : float  Effective width (mm)
    G       : float  Shear modulus (N/mm²)
    S       : float  Shape factor
    sum_ti  : float  Total internal rubber thickness (mm)
    """
    stress = Vmax * 1000 / A1                    # D88  (N/mm²)
    stability_limit = 2 * be * G * S / (3 * sum_ti)  # F90
    geometry_limit = be / 4                       # D92

    cond_stress = stress < stability_limit        # D88 < F90
    cond_geom = sum_ti < geometry_limit           # D28 < D92

    passed = cond_stress and cond_geom
    status = "OK" if passed else "FAIL"

    intermediates = {
        "V/A1 (N/mm²)": round(stress, 4),
        "(2·be·G·S')/(3·Σti)": round(stability_limit, 4),
        "be/4 (mm)": round(geometry_limit, 4),
        "Σti (mm)": round(sum_ti, 4),
        "Stress check (V/A1 < limit)": cond_stress,
        "Geometry check (Σti < be/4)": cond_geom,
    }

    message = (
        f"V/A1 = {stress:.4f} N/mm²  |  "
        f"limit = {stability_limit:.4f}  |  "
        f"Σti = {sum_ti:.1f} mm  |  "
        f"be/4 = {geometry_limit:.1f} mm  |  "
        f"{'Stress ✓' if cond_stress else 'Stress ✗'}  "
        f"{'Geom ✓' if cond_geom else 'Geom ✗'}  "
        f"→ {status}"
    )

    return Check4Result(status=status, intermediates=intermediates,
                        message=message)
