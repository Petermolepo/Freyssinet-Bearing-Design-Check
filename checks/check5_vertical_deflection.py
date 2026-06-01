"""
Check 5 — Vertical deflection (“How much does the bearing squash?”)
===================================================================
Total sag ▲Total across all rubber layers.  PASS when ▲Total < 0.15 × ti.
Spreadsheet cells:
  D99  = Eb = 2000 N/mm²  (bulk modulus, hardcoded)
  D101 = delta = ((Vmax*1000*ti) / (5*Ae*G*S^2))
                 + ((Vmax*1000*ti) / (Ae*Eb))
  F103 = delta_total = delta * no_layers        (D101 * E24)
  D105 = 0.15 * ti
  D107 = IF(F103 < D105, "OK!", "FAILS!")

  Pass condition: delta_total < 0.15 * ti
"""

from dataclasses import dataclass
from typing import Dict, Any

EB_DEFAULT = 2000.0   # N/mm² – bulk modulus, hardcoded in spreadsheet D99


@dataclass
class Check5Result:
    """Result for Check 5: total vertical movement ▲Total."""
    delta_total: float
    status: str
    intermediates: Dict[str, Any]
    message: str


def check5_vertical_deflection(
    Vmax: float, ti: float, Ae: float, G: float, S: float,
    no_layers: int, Eb: float = EB_DEFAULT,
) -> Check5Result:
    """
    Vertical deflection check.

    Parameters
    ----------
    Vmax      : float  Maximum vertical load (kN)
    ti        : float  Internal rubber layer thickness (mm)
    Ae        : float  Plan area le*be (mm²)   [NOTE: spreadsheet uses Ae=D29, not A1]
    G         : float  Shear modulus (N/mm²)
    S         : float  Shape factor
    no_layers : int    Number of rubber layers
    Eb        : float  Bulk modulus (N/mm², default 2000)
    """
    # D101 – deflection per layer
    delta = (
        (Vmax * 1000 * ti) / (5 * Ae * G * S ** 2)
        + (Vmax * 1000 * ti) / (Ae * Eb)
    )

    # F103 – total deflection
    delta_total = delta * no_layers   # D101 * E24

    # D105
    limit = 0.15 * ti

    passed = delta_total < limit
    status = "OK" if passed else "FAIL"

    intermediates = {
        "Eb (N/mm²)": Eb,
        "δ per layer (mm)": round(delta, 6),
        "▲Total (mm)": round(delta_total, 4),
        "0.15·ti (mm)": round(limit, 4),
    }

    message = (
        f"▲Total = {delta_total:.4f} mm  |  "
        f"limit (0.15·ti) = {limit:.4f} mm  |  "
        f"→ {status}"
    )

    return Check5Result(delta_total=delta_total, status=status,
                        intermediates=intermediates, message=message)
