"""
compare.py
==========
Side-by-side comparison of two bearing designs.
Highlights which bearing wins on each check and overall.
"""

import sys
from engine import BearingResult
from models import BearingInput

_USE_COLOUR = sys.stdout.isatty()
_GREEN  = "\033[92m" if _USE_COLOUR else ""
_RED    = "\033[91m" if _USE_COLOUR else ""
_YELLOW = "\033[93m" if _USE_COLOUR else ""
_BOLD   = "\033[1m"  if _USE_COLOUR else ""
_RESET  = "\033[0m"  if _USE_COLOUR else ""


def _status(s: str) -> str:
    if s == "OK":
        return f"{_GREEN}OK  {_RESET}"
    return f"{_RED}FAIL{_RESET}"


def _winner(s1: str, s2: str) -> str:
    if s1 == s2:
        return "TIE "
    if s1 == "OK":
        return f"{_GREEN}A ✓ {_RESET}"
    return f"{_GREEN}B ✓ {_RESET}"


def format_comparison(
    inp_a: BearingInput, res_a: BearingResult, label_a: str,
    inp_b: BearingInput, res_b: BearingResult, label_b: str,
) -> str:

    checks_a = [res_a.check1, res_a.check2, res_a.check3, res_a.check4,
                res_a.check5, res_a.check6, res_a.check7]
    checks_b = [res_b.check1, res_b.check2, res_b.check3, res_b.check4,
                res_b.check5, res_b.check6, res_b.check7]

    names = [
        "Shear Strain",
        "Max Design Strain",
        "Plate Thickness",
        "Stability",
        "Vertical Deflection",
        "Rotational Limit",
        "Fixing of Bearings",
    ]

    # Key values for each check
    def key_val(chk, idx):
        if idx == 0: return f"Eq={chk.Eq:.4f}"
        if idx == 1: return f"Et={chk.Et:.4f}"
        if idx == 2: return f"tmin={chk.tmin:.4f}"
        if idx == 3: return f"V/A1={chk.intermediates['V/A1 (N/mm²)']:.2f}"
        if idx == 4: return f"▲={chk.delta_total:.4f}"
        if idx == 5: return f"▲={chk.delta_total:.4f}"
        if idx == 6: return f"H={chk.intermediates['H (kN)']:.1f}"
        return ""

    sep = "─" * 82
    lines = []
    lines.append(sep)
    lines.append(
        f"{'':4}  {'CHECK':<24}  "
        f"{_BOLD}{label_a[:18]:<18}{_RESET}  "
        f"{_BOLD}{label_b[:18]:<18}{_RESET}  "
        f"{'WIN':<6}"
    )
    lines.append(sep)

    for i, (name, ca, cb) in enumerate(zip(names, checks_a, checks_b)):
        kva = key_val(ca, i)
        kvb = key_val(cb, i)
        lines.append(
            f"{i+1:<4}  {name:<24}  "
            f"{_status(ca.status)} {kva:<14}  "
            f"{_status(cb.status)} {kvb:<14}  "
            f"{_winner(ca.status, cb.status)}"
        )

    lines.append(sep)

    # Dimension comparison
    lines.append(f"\n  {'DIMENSION':<24}  {label_a[:18]:<18}  {label_b[:18]:<18}")
    lines.append("  " + "─" * 64)
    dim_rows = [
        ("l × b × T (mm)",    f"{inp_a.l}×{inp_a.b}×{inp_a.T}",
                               f"{inp_b.l}×{inp_b.b}×{inp_b.T}"),
        ("Vmax (kN)",          str(inp_a.Vmax),  str(inp_b.Vmax)),
        ("G (N/mm²)",          str(inp_a.G),     str(inp_b.G)),
        ("plate_thk (mm)",     str(inp_a.plate_thk), str(inp_b.plate_thk)),
        ("te / ti (mm)",       f"{inp_a.te}/{inp_a.ti}", f"{inp_b.te}/{inp_b.ti}"),
    ]
    for label, va, vb in dim_rows:
        lines.append(f"  {label:<24}  {va:<18}  {vb:<18}")

    lines.append(sep)

    # Overall
    a_passes = sum(1 for c in checks_a if c.status == "OK")
    b_passes = sum(1 for c in checks_b if c.status == "OK")

    def verdict(res):
        if res.overall == "BEARING PASSES":
            return f"{_GREEN}{_BOLD}PASSES ({a_passes}/7){_RESET}" if res is res_a \
                   else f"{_GREEN}{_BOLD}PASSES ({b_passes}/7){_RESET}"
        fails_a = sum(1 for c in checks_a if c.status != "OK")
        fails_b = sum(1 for c in checks_b if c.status != "OK")
        if res is res_a:
            return f"{_RED}{_BOLD}FAILS ({fails_a} checks){_RESET}"
        return f"{_RED}{_BOLD}FAILS ({fails_b} checks){_RESET}"

    lines.append(f"\n  OVERALL  {label_a[:18]:<18}: {res_a.overall}")
    lines.append(f"  OVERALL  {label_b[:18]:<18}: {res_b.overall}")

    if a_passes > b_passes:
        lines.append(f"\n  {_GREEN}{_BOLD}► {label_a} performs better ({a_passes}/7 vs {b_passes}/7){_RESET}")
    elif b_passes > a_passes:
        lines.append(f"\n  {_GREEN}{_BOLD}► {label_b} performs better ({b_passes}/7 vs {a_passes}/7){_RESET}")
    else:
        lines.append(f"\n  {_YELLOW}{_BOLD}► Both designs score {a_passes}/7 checks{_RESET}")

    lines.append(sep)
    return "\n".join(lines)
