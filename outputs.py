"""
outputs.py — How results are shown to the user
==============================================
Turns BearingResult into readable text: summary table, full detail,
JSON for APIs, or the formula sheet (--explain).
No maths here — only formatting and colours.
"""

import json
from engine import BearingResult


# ANSI colours (disabled automatically on non-TTY / Windows)
import sys
_USE_COLOUR = sys.stdout.isatty()

_GREEN  = "\033[92m" if _USE_COLOUR else ""
_RED    = "\033[91m" if _USE_COLOUR else ""
_BOLD   = "\033[1m"  if _USE_COLOUR else ""
_RESET  = "\033[0m"  if _USE_COLOUR else ""


def _status_str(status: str) -> str:
    if status == "OK":
        return f"{_GREEN}OK  {_RESET}"
    return f"{_RED}FAIL{_RESET}"


def format_table(result: BearingResult) -> str:
    """Compact one-line-per-check table (default CLI output)."""
    checks = [
        ("1", "Shear Strain",          result.check1),
        ("2", "Max Design Strain",     result.check2),
        ("3", "Plate Thickness",       result.check3),
        ("4", "Stability",             result.check4),
        ("5", "Vertical Deflection",   result.check5),
        ("6", "Rotational Limit",      result.check6),
        ("7", "Fixing of Bearings",    result.check7),
    ]

    lines = []
    sep = "─" * 78
    lines.append(sep)
    lines.append(f"{'CHECK':<4}  {'NAME':<26}  {'STATUS':<6}  KEY VALUES")
    lines.append(sep)

    for num, name, chk in checks:
        status_col = _status_str(chk.status)
        # Build a compact key-values string from intermediates
        kv_items = []
        for k, v in chk.intermediates.items():
            if isinstance(v, bool):
                kv_items.append(f"{k}={'✓' if v else '✗'}")
            elif isinstance(v, float):
                kv_items.append(f"{k}={v:.4f}")
            else:
                kv_items.append(f"{k}={v}")
        kv_str = "  |  ".join(kv_items[:4])   # cap at 4 items for width
        lines.append(f"{num:<4}  {name:<26}  {status_col}    {kv_str}")

    lines.append(sep)

    # Overall verdict
    if result.overall == "BEARING PASSES":
        verdict = f"{_GREEN}{_BOLD}✔  BEARING PASSES{_RESET}"
    else:
        verdict = f"{_RED}{_BOLD}✘  BEARING FAILS{_RESET}"

    lines.append(f"\n  OVERALL RESULT:  {verdict}\n")
    lines.append(sep)
    return "\n".join(lines)


def format_full(result: BearingResult) -> str:
    """Verbose per-check output with all intermediate values."""
    checks = [
        ("Check 1 – Shear Strain",          result.check1),
        ("Check 2 – Max Design Strain",     result.check2),
        ("Check 3 – Plate Thickness",       result.check3),
        ("Check 4 – Stability",             result.check4),
        ("Check 5 – Vertical Deflection",   result.check5),
        ("Check 6 – Rotational Limit",      result.check6),
        ("Check 7 – Fixing of Bearings",    result.check7),
    ]

    lines = []
    sep = "═" * 60

    for title, chk in checks:
        lines.append(sep)
        status_col = _status_str(chk.status)
        lines.append(f"  {_BOLD}{title}{_RESET}   [{status_col}]")
        lines.append("")
        for k, v in chk.intermediates.items():
            if isinstance(v, bool):
                lines.append(f"    {k:<35} {'✓' if v else '✗'}")
            elif isinstance(v, float):
                lines.append(f"    {k:<35} {v:.6f}")
            else:
                lines.append(f"    {k:<35} {v}")
        lines.append(f"\n    → {chk.message}")
        lines.append("")

    lines.append(sep)
    if result.overall == "BEARING PASSES":
        verdict = f"{_GREEN}{_BOLD}✔  BEARING PASSES{_RESET}"
    else:
        verdict = f"{_RED}{_BOLD}✘  BEARING FAILS{_RESET}"
    lines.append(f"\n  OVERALL RESULT:  {verdict}\n")
    lines.append(sep)
    return "\n".join(lines)


def format_json(result: BearingResult) -> str:
    """Serialise result to JSON."""
    def _chk_dict(chk):
        d = {
            "status": chk.status,
            "intermediates": chk.intermediates,
            "message": chk.message,
        }
        for attr in ("Eq", "Et", "tmin", "delta_total", "rot_limit"):
            if hasattr(chk, attr):
                d[attr] = getattr(chk, attr)
        return d

    payload = {
        "check1_shear_strain":        _chk_dict(result.check1),
        "check2_max_design_strain":   _chk_dict(result.check2),
        "check3_plate_thickness":     _chk_dict(result.check3),
        "check4_stability":           _chk_dict(result.check4),
        "check5_vertical_deflection": _chk_dict(result.check5),
        "check6_rotational_limit":    _chk_dict(result.check6),
        "check7_fixing_of_bearings":  _chk_dict(result.check7),
        "overall": result.overall,
    }
    return json.dumps(payload, indent=2)


FORMULAS = """
════════════════════════════════════════════════════════════════
  FORMULA REFERENCE  (all lengths mm, forces kN, stress N/mm²)
════════════════════════════════════════════════════════════════

  GEOMETRY (derived)
    le          = l - 10
    be          = b - 10
    no_layers   = no_plates - 1
    tq          = T - (no_plates × plate_thk)
    Σti         = ti × no_layers
    Ae          = le × be
    lp          = 2 × (le + be)
    S           = Ae / (lp × te)
    δbH         = Hs×1000×tq / (l×b×G)
    δlH         = Ht×1000×tq / (l×b×G)
    δb          = long_mvmt + δbH
    δl          = trans_mvmt + δlH
    δr          = √(δb² + δl²)

  CHECK 1 – Shear Strain
    Eq          = δr / tq         PASS: Eq < 0.7

  CHECK 2 – Maximum Design Strain
    A1          = Ae × (1 - δb/be - δl/le)
    Ec          = 1.5 × Vmax×1000 / (G × A1 × S)
    Eα          = (be²×αb + le²×αl) / (2×ti×Σti)
    k           = (1.5×Vll + 1.0×Vdl) / Vmax
    Et          = k × (Ec + Eq + Eα)   PASS: Et < 5

  CHECK 3 – Plate Thickness
    tmin        = 1.3×Vmax×1000×(te+ti) / (A1×σs)   [σs=290 N/mm²]
    PASS: tmin > 2  AND  tmin < plate_thk  AND  plate_thk > 2

  CHECK 4 – Stability
    V/A1        = Vmax×1000 / A1
    limit       = 2×be×G×S / (3×Σti)
    PASS: V/A1 < limit  AND  Σti < be/4

  CHECK 5 – Vertical Deflection
    Eb          = 2000 N/mm²  (constant)
    δ           = (Vmax×1000×ti)/(5×Ae×G×S²) + (Vmax×1000×ti)/(Ae×Eb)
    ▲Total      = δ × no_layers   PASS: ▲Total < 0.15×ti

  CHECK 6 – Rotational Limit
    rot_limit   = (be×αb + le×αl) / 3
    PASS: ▲Total > rot_limit

  CHECK 7 – Fixing of Bearings
    H           = l×b×G×δr / tq
    a) PASS: H < 0.1×(Vmax×1000 + 2×A1)
    b) PASS: Vdl×1000/A1 > 2
════════════════════════════════════════════════════════════════
"""


def format_explain() -> str:
    return FORMULAS
