"""
Check 6 — Rotational limit (“Is there enough sag to absorb rotation?”)
======================================================================
PASS when ▲Total > (be·αb + le·αl)/3 — deflection must exceed rotation demand.
Spreadsheet cells:
  D112 = ▲ = delta_total (same value as F103 from Check 5)
  F114 = (be*alpha_b + le*alpha_l) / 3
  D116 = IF(D112 > F114, "OK!", "FAILS!")

  IMPORTANT: The spreadsheet condition is D112 > F114 → "OK!"
  This means: delta_total > rotational_limit → PASS
  Which is the OPPOSITE of what the brief summary implies.
  The brief says "▲ ≤ (be·αb + le·αl)/3" but the spreadsheet
  says IF(D112 > F114, "OK!") meaning larger delta_total is better.
  This is correct in context: the rotational allowance must be LESS THAN
  the deflection capacity. The spreadsheet is authoritative.

  Sample produces delta_total=1.589, rot_limit=0.00813 → 1.589 > 0.00813 → OK
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Check6Result:
    """Result for Check 6: compares Check 5 ▲Total to rotational limit."""
    delta_total: float
    rot_limit: float
    status: str
    intermediates: Dict[str, Any]
    message: str


def check6_rotational_limit(
    delta_total: float, be: float, le: float,
    alpha_b: float, alpha_l: float,
) -> Check6Result:
    """
    Rotational limit check.

    Parameters
    ----------
    delta_total : float  Total vertical deflection (mm) [from Check 5]
    be          : float  Effective width (mm)
    le          : float  Effective length (mm)
    alpha_b     : float  Applied rotation about transverse axis (rad)
    alpha_l     : float  Applied rotation about longitudinal axis (rad)
    """
    # F114
    rot_limit = (be * alpha_b + le * alpha_l) / 3

    # D116: IF(D112 > F114, "OK!", "FAILS!")
    passed = delta_total > rot_limit
    status = "OK" if passed else "FAIL"

    intermediates = {
        "▲ (mm)": round(delta_total, 4),
        "(be·αb + le·αl)/3": round(rot_limit, 6),
    }

    message = (
        f"▲ = {delta_total:.4f} mm  |  "
        f"rot limit = {rot_limit:.6f}  |  "
        f"▲ {'>' if passed else '≤'} rot_limit  → {status}"
    )

    return Check6Result(delta_total=delta_total, rot_limit=rot_limit,
                        status=status, intermediates=intermediates,
                        message=message)
