"""
Check 1 – Shear Strain
======================
Spreadsheet cells:
  D44 = Eq = delta_r / tq       (F38 / D27)
  F44 = IF(D44 < 0.7, "OK!", "FAILS!")

NOTE: The assessment brief states the pass condition is Eq <= 1.0,
but the spreadsheet formula is strictly < 0.7. The spreadsheet is the
authoritative source for this tool; the brief is a summary document.
The sample input produces Eq = 0.8016, which FAILS the 0.7 threshold.
This matches the expected "Check 1: FAILS" verification result.
"""

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Check1Result:
    Eq: float
    status: str          # "OK" | "FAIL"
    intermediates: Dict[str, Any]
    message: str


def check1_shear_strain(delta_r, delta_b, delta_l, S, tq, eq_limit=0.7):
    """
    Shear strain check.

    Parameters
    ----------
    delta_r : float   Resultant shear displacement (mm)  [F38]
    delta_b : float   Longitudinal shear displacement (mm) [D36]
    delta_l : float   Transverse shear displacement (mm)  [D37]
    S       : float   Shape factor (dimensionless)        [D39]
    tq      : float   Total rubber thickness (mm)         [D27]

    Returns
    -------
    Check1Result
    """
    Eq = delta_r / tq   # D44

    # Spreadsheet threshold is 0.7 (not 1.0 as the brief summary states)
    LIMIT = eq_limit
    passed = Eq < LIMIT
    status = "OK" if passed else "FAIL"

    intermediates = {
        "delta_b (mm)": round(delta_b, 4),
        "delta_l (mm)": round(delta_l, 4),
        "delta_r (mm)": round(delta_r, 4),
        "S": round(S, 4),
        "tq (mm)": round(tq, 4),
        "Eq": round(Eq, 4),
    }

    message = (
        f"Eq = {Eq:.4f} {'<' if passed else '>='} {LIMIT} → {status}"
    )

    return Check1Result(Eq=Eq, status=status,
                        intermediates=intermediates, message=message)
