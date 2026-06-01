"""
Check 3 — Plate thickness (“Are the steel plates thick enough?”)
================================================================
Computes minimum required thickness tmin.  PASS when tmin ≤ actual plate_thk.
Spreadsheet cells (verified against brief pass condition):
  t1        = te  (edge rubber layer thickness, mm)
  t2        = ti  (internal rubber layer thickness, mm)
  sigma_s   = 290 N/mm²  (steel yield stress, hardcoded)
  tmin      = (1.3 * Vmax*1000 * (t1 + t2)) / (A1 * sigma_s)
  PASS      : tmin <= plate_thk
"""

from dataclasses import dataclass
from typing import Dict, Any

SIGMA_S = 290.0   # N/mm² – steel yield stress (hardcoded in spreadsheet)


@dataclass
class Check3Result:
    """Result for Check 3: required tmin vs supplied plate thickness."""
    tmin: float
    status: str
    intermediates: Dict[str, Any]
    message: str


def check3_plate_thickness(
    Vmax: float, A1: float,
    t1: float, t2: float,
    plate_thk: float,
    sigma_s: float = SIGMA_S,
) -> Check3Result:
    """
    Reinforcing plate thickness check.

    Parameters
    ----------
    Vmax      : float  Maximum vertical load (kN)
    A1        : float  Effective plan area (mm²)  [from Check 2]
    t1        : float  Edge rubber layer thickness te (mm)
    t2        : float  Internal rubber layer thickness ti (mm)
    plate_thk : float  Actual reinforcing plate thickness (mm)
    sigma_s   : float  Steel yield stress (N/mm², default 290)
    """
    tmin = (1.3 * Vmax * 1000 * (t1 + t2)) / (A1 * sigma_s)

    passed = tmin <= plate_thk
    status = "OK" if passed else "FAIL"

    intermediates = {
        "t1 – te (mm)":    round(t1, 4),
        "t2 – ti (mm)":    round(t2, 4),
        "σs (N/mm²)":      round(sigma_s, 2),
        "tmin (mm)":       round(tmin, 4),
        "plate_thk (mm)":  round(plate_thk, 4),
    }

    message = (
        f"tmin = {tmin:.4f} mm  |  "
        f"plate_thk = {plate_thk} mm  |  "
        f"tmin {'≤' if passed else '>'} plate_thk  → {status}"
    )

    return Check3Result(tmin=tmin, status=status,
                        intermediates=intermediates, message=message)
