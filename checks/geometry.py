"""
Pre-computed geometry values derived from raw inputs.
Accepts cover_strip parameter so bearing types can override the default 5 mm.
"""

import math
from dataclasses import dataclass


@dataclass
class Geometry:
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
