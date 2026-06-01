"""
geometry.py — Shared derived values (run before Check 1)
=========================================================
Computes effective size (le, be), rubber thickness tq, movements δb/δl/δr,
plan area Ae, and shape factor S. Every check uses these numbers.
cover_strip: mm trimmed from each side of l and b (default 5, pad bearing).
"""

import math
from dataclasses import dataclass


@dataclass
class Geometry:
    """All intermediate geometry from the spreadsheet (one object, easy to pass)."""
    le: float
    be: float
    no_layers: int
    tq: float
    sum_ti: float
    Ae: float
    lp: float
    S: float
    delta_bH: float
    delta_lH: float
    delta_b: float
    delta_l: float
    delta_r: float


def compute_geometry(inp, cover_strip: float = 5.0) -> Geometry:
    """Build Geometry from BearingInput. Called once at the start of run_checks()."""
    le = inp.l - 2 * cover_strip
    be = inp.b - 2 * cover_strip
    no_layers = inp.no_plates - 1
    tq = inp.T - (inp.no_plates * inp.plate_thk)
    sum_ti = inp.ti * no_layers
    Ae = le * be
    lp = 2 * (le + be)
    S = Ae / (lp * inp.te)

    delta_bH = inp.Hs * 1000 * tq / (inp.l * inp.b * inp.G)
    delta_lH = inp.Ht * 1000 * tq / (inp.l * inp.b * inp.G)
    delta_b  = inp.long_mvmt + delta_bH
    delta_l  = inp.trans_mvmt + delta_lH
    delta_r  = math.sqrt(delta_b ** 2 + delta_l ** 2)

    return Geometry(
        le=le, be=be,
        no_layers=no_layers, tq=tq, sum_ti=sum_ti,
        Ae=Ae, lp=lp, S=S,
        delta_bH=delta_bH, delta_lH=delta_lH,
        delta_b=delta_b, delta_l=delta_l, delta_r=delta_r,
    )
