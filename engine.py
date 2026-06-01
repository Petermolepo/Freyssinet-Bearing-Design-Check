"""
engine.py — Calculation orchestrator
====================================
Runs geometry once, then checks 1→7 in the correct order.
Returns one BearingResult with pass/fail per check and overall verdict.
This is the single entry point for “run the full design check”.
"""

from dataclasses import dataclass

from models import BearingInput
from checks.geometry import compute_geometry
from checks.check1_shear_strain import check1_shear_strain, Check1Result
from checks.check2_max_design_strain import check2_max_design_strain, Check2Result
from checks.check3_plate_thickness import check3_plate_thickness, Check3Result
from checks.check4_stability import check4_stability, Check4Result
from checks.check5_vertical_deflection import check5_vertical_deflection, Check5Result
from checks.check6_rotational_limit import check6_rotational_limit, Check6Result
from checks.check7_fixing import check7_fixing, Check7Result


@dataclass
class BearingResult:
    """Full outcome: seven check results plus BEARING PASSES / BEARING FAILS."""
    check1: Check1Result
    check2: Check2Result
    check3: Check3Result
    check4: Check4Result
    check5: Check5Result
    check6: Check6Result
    check7: Check7Result
    overall: str          # "BEARING PASSES" | "BEARING FAILS"
    bearing_type: str = "pad"


def run_checks(inp: BearingInput, bearing_type=None) -> BearingResult:
    """
    Run all 7 Freyssinet design checks.

    Parameters
    ----------
    inp          : BearingInput
    bearing_type : BearingType | None   Pass a BearingType to apply its
                                        constants. Defaults to PAD_BEARING.
    """
    # Import here to avoid circular at module level
    from bearing_types.registry import PAD_BEARING
    bt = bearing_type or PAD_BEARING

    g = compute_geometry(inp, cover_strip=bt.cover_strip_mm)

    # ── Check 1 ───────────────────────────────────────────────────────────
    c1 = check1_shear_strain(
        delta_r=g.delta_r, delta_b=g.delta_b, delta_l=g.delta_l,
        S=g.S, tq=g.tq, eq_limit=bt.eq_limit,
    )

    # ── Check 2 ───────────────────────────────────────────────────────────
    c2 = check2_max_design_strain(
        Ae=g.Ae, delta_b=g.delta_b, delta_l=g.delta_l,
        be=g.be, le=g.le,
        Vmax=inp.Vmax, Vdl=inp.Vdl, Vll=inp.Vll,
        G=inp.G, S=g.S,
        alpha_b=inp.alpha_b, alpha_l=inp.alpha_l,
        ti=inp.ti, sum_ti=g.sum_ti, Eq=c1.Eq,
        et_limit=bt.et_limit,
    )

    A1 = c2.intermediates["A1 (mm²)"]

    # ── Check 3 ───────────────────────────────────────────────────────────
    c3 = check3_plate_thickness(
        Vmax=inp.Vmax, A1=A1,
        t1=inp.te, t2=inp.ti,
        plate_thk=inp.plate_thk,
        sigma_s=bt.steel_yield,
    )

    # ── Check 4 ───────────────────────────────────────────────────────────
    c4 = check4_stability(
        Vmax=inp.Vmax, A1=A1,
        be=g.be, G=inp.G, S=g.S,
        sum_ti=g.sum_ti,
    )

    # ── Check 5 ───────────────────────────────────────────────────────────
    c5 = check5_vertical_deflection(
        Vmax=inp.Vmax, ti=inp.ti,
        Ae=g.Ae, G=inp.G, S=g.S,
        no_layers=g.no_layers,
        Eb=bt.bulk_modulus,
    )

    # ── Check 6 ───────────────────────────────────────────────────────────
    c6 = check6_rotational_limit(
        delta_total=c5.delta_total,
        be=g.be, le=g.le,
        alpha_b=inp.alpha_b, alpha_l=inp.alpha_l,
    )

    # ── Check 7 ───────────────────────────────────────────────────────────
    c7 = check7_fixing(
        l=inp.l, b=inp.b, G=inp.G,
        delta_r=g.delta_r, tq=g.tq,
        Vmax=inp.Vmax, Vdl=inp.Vdl,
        A1=A1,
    )

    all_pass = all(c.status == "OK" for c in [c1, c2, c3, c4, c5, c6, c7])
    overall  = "BEARING PASSES" if all_pass else "BEARING FAILS"

    return BearingResult(
        check1=c1, check2=c2, check3=c3, check4=c4,
        check5=c5, check6=c6, check7=c7,
        overall=overall, bearing_type=bt.code,
    )
