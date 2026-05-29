"""
Check 2 – Maximum Design Strain
================================
Spreadsheet cells:
  D51 = A1  = Ae * (1 - (delta_b/be) - (delta_l/le))
  D52 = Ec  = 1.5 * Vmax*1000 / (G * A1 * S)
  D54 = Ea  = ((be^2 * alpha_b) + (le^2 * alpha_l)) / (2 * ti * sum_ti)
  D56 = k   = ((1.5 * Vll) + (1 * Vdl)) / Vmax
  D58 = Et  = k * (Ec + Eq + Ea)
  F58 = IF(D58 < 5, "OK!", "FAILS!")

  NOTE: Brief says pass condition is Et <= 7.0 but spreadsheet uses < 5.
  Spreadsheet is authoritative. Sample gives Et = 5.43 → FAILS (>= 5).
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Check2Result:
    Et: float
    status: str
    intermediates: Dict[str, Any]
    message: str


def check2_max_design_strain(
    Ae: float, delta_b: float, delta_l: float,
    be: float, le: float,
    Vmax: float, Vdl: float, Vll: float,
    G: float, S: float,
    alpha_b: float, alpha_l: float,
    ti: float, sum_ti: float,
    Eq: float,
    et_limit: float = 5.0,
):
    """
    Maximum design strain check.

    All forces in kN; converted to N (×1000) where needed.
    All lengths in mm.
    """
    # D51 – effective plan area (reduced for shear displacement)
    A1 = Ae * (1 - (delta_b / be) - (delta_l / le))

    # D52 – compressive strain
    Ec = 1.5 * Vmax * 1000 / (G * A1 * S)

    # D54 – rotational strain
    Ea = ((be ** 2) * alpha_b + (le ** 2) * alpha_l) / (2 * ti * sum_ti)

    # D56 – load combination factor
    k = (1.5 * Vll + 1.0 * Vdl) / Vmax

    # D58 – total equivalent strain
    Et = k * (Ec + Eq + Ea)

    LIMIT = et_limit
    passed = Et < LIMIT
    status = "OK" if passed else "FAIL"

    intermediates = {
        "A1 (mm²)": round(A1, 4),
        "Ec": round(Ec, 4),
        "Eα": round(Ea, 6),
        "k": round(k, 4),
        "Et": round(Et, 4),
    }

    message = f"Et = {Et:.4f} {'<' if passed else '>='} {LIMIT} → {status}"

    return Check2Result(Et=Et, status=status,
                        intermediates=intermediates, message=message)
