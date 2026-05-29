"""
tests/test_checks.py
====================
Full test suite: unit tests per check, integration test against
the official sample, and input validation tests.

Run with:  pytest tests/ -v
"""

import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from models import BearingInput
from validators import validate
from engine import run_checks
from checks.geometry import compute_geometry
from checks.check1_shear_strain import check1_shear_strain
from checks.check2_max_design_strain import check2_max_design_strain
from checks.check3_plate_thickness import check3_plate_thickness
from checks.check4_stability import check4_stability
from checks.check5_vertical_deflection import check5_vertical_deflection
from checks.check6_rotational_limit import check6_rotational_limit
from checks.check7_fixing import check7_fixing


# ══════════════════════════════════════════════════════════════════════════════
# SAMPLE INPUT (official verification case from the brief)
# ══════════════════════════════════════════════════════════════════════════════

SAMPLE = BearingInput(
    l=457, b=254, T=54,
    plate_thk=4.5, no_plates=4,
    te=10, ti=10,
    G=0.9,
    Vmax=1420, Vdl=384, Vll=1036,
    Hs=50, Ht=10,
    long_mvmt=10.6, trans_mvmt=4.19,
    alpha_b=0.0001, alpha_l=0,
)


# ══════════════════════════════════════════════════════════════════════════════
# INTEGRATION TEST – must reproduce brief's exact verification results
# ══════════════════════════════════════════════════════════════════════════════

class TestSampleVerification:
    """
    These tests are the ground truth. Every value is taken directly
    from the brief's Verification section. If any of these fail, the
    engine is wrong — do not change the assertions, fix the engine.
    """

    def test_overall_result_is_bearing_fails(self):
        result = run_checks(SAMPLE)
        assert result.overall == "BEARING FAILS"

    def test_check1_fails(self):
        result = run_checks(SAMPLE)
        assert result.check1.status == "FAIL"

    def test_check1_eq_approx_0_80(self):
        result = run_checks(SAMPLE)
        assert abs(result.check1.Eq - 0.80) < 0.01, \
            f"Expected Eq ≈ 0.80, got {result.check1.Eq:.4f}"

    def test_check2_fails(self):
        result = run_checks(SAMPLE)
        assert result.check2.status == "FAIL"

    def test_check2_et_approx_5_43(self):
        result = run_checks(SAMPLE)
        assert abs(result.check2.Et - 5.43) < 0.05, \
            f"Expected Et ≈ 5.43, got {result.check2.Et:.4f}"

    def test_check3_passes(self):
        result = run_checks(SAMPLE)
        assert result.check3.status == "OK"

    def test_check4_passes(self):
        result = run_checks(SAMPLE)
        assert result.check4.status == "OK"

    def test_check5_fails(self):
        result = run_checks(SAMPLE)
        assert result.check5.status == "FAIL"

    def test_check5_delta_total_approx_1_59(self):
        result = run_checks(SAMPLE)
        assert abs(result.check5.delta_total - 1.59) < 0.02, \
            f"Expected ▲Total ≈ 1.59, got {result.check5.delta_total:.4f}"

    def test_check6_passes(self):
        result = run_checks(SAMPLE)
        assert result.check6.status == "OK"

    def test_check7_passes(self):
        result = run_checks(SAMPLE)
        assert result.check7.status == "OK"

    def test_failing_checks_are_exactly_1_2_5(self):
        """Checks 1, 2, 5 must fail; all others must pass."""
        result = run_checks(SAMPLE)
        assert result.check1.status == "FAIL"
        assert result.check2.status == "FAIL"
        assert result.check3.status == "OK"
        assert result.check4.status == "OK"
        assert result.check5.status == "FAIL"
        assert result.check6.status == "OK"
        assert result.check7.status == "OK"


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – GEOMETRY
# ══════════════════════════════════════════════════════════════════════════════

class TestGeometry:

    def test_le_be_reduced_by_10(self):
        g = compute_geometry(SAMPLE)
        assert g.le == SAMPLE.l - 10
        assert g.be == SAMPLE.b - 10

    def test_no_layers_is_plates_minus_1(self):
        g = compute_geometry(SAMPLE)
        assert g.no_layers == SAMPLE.no_plates - 1

    def test_tq_total_rubber(self):
        g = compute_geometry(SAMPLE)
        expected = SAMPLE.T - (SAMPLE.no_plates * SAMPLE.plate_thk)
        assert abs(g.tq - expected) < 1e-9

    def test_Ae_is_le_times_be(self):
        g = compute_geometry(SAMPLE)
        assert abs(g.Ae - g.le * g.be) < 1e-9

    def test_S_shape_factor(self):
        g = compute_geometry(SAMPLE)
        lp = 2 * (g.le + g.be)
        expected_S = (g.le * g.be) / (lp * SAMPLE.te)
        assert abs(g.S - expected_S) < 1e-6

    def test_delta_r_is_pythagoras(self):
        g = compute_geometry(SAMPLE)
        expected = math.sqrt(g.delta_b ** 2 + g.delta_l ** 2)
        assert abs(g.delta_r - expected) < 1e-9


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – CHECK 1: Shear Strain
# ══════════════════════════════════════════════════════════════════════════════

class TestCheck1:

    def test_passes_when_eq_below_0_7(self):
        # delta_r = 21, tq = 36 → Eq = 0.583 < 0.7 → OK
        r = check1_shear_strain(delta_r=21.0, delta_b=20.0, delta_l=5.0,
                                 S=7.9, tq=36.0)
        assert r.status == "OK"

    def test_fails_when_eq_above_0_7(self):
        # delta_r = 30, tq = 36 → Eq = 0.833 > 0.7 → FAIL
        r = check1_shear_strain(delta_r=30.0, delta_b=28.0, delta_l=10.0,
                                 S=7.9, tq=36.0)
        assert r.status == "FAIL"

    def test_eq_formula(self):
        r = check1_shear_strain(delta_r=25.2, delta_b=24.0, delta_l=8.0,
                                 S=7.0, tq=36.0)
        assert abs(r.Eq - 25.2 / 36.0) < 1e-9

    def test_boundary_exactly_0_7_fails(self):
        # Eq = 0.7 exactly — spreadsheet uses strict < 0.7, so 0.7 → FAIL
        r = check1_shear_strain(delta_r=0.7 * 36.0, delta_b=0.0,
                                 delta_l=0.0, S=7.0, tq=36.0)
        assert r.status == "FAIL"


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – CHECK 2: Maximum Design Strain
# ══════════════════════════════════════════════════════════════════════════════

class TestCheck2:

    def _sample_args(self, **overrides):
        g = compute_geometry(SAMPLE)
        base = dict(
            Ae=g.Ae, delta_b=g.delta_b, delta_l=g.delta_l,
            be=g.be, le=g.le,
            Vmax=SAMPLE.Vmax, Vdl=SAMPLE.Vdl, Vll=SAMPLE.Vll,
            G=SAMPLE.G, S=g.S,
            alpha_b=SAMPLE.alpha_b, alpha_l=SAMPLE.alpha_l,
            ti=SAMPLE.ti, sum_ti=g.sum_ti, Eq=0.8016,
        )
        base.update(overrides)
        return base

    def test_sample_et_approx_5_43(self):
        r = check2_max_design_strain(**self._sample_args())
        assert abs(r.Et - 5.43) < 0.05

    def test_passes_with_lower_load(self):
        r = check2_max_design_strain(**self._sample_args(Vmax=500, Vll=200, Vdl=300))
        assert r.status == "OK"

    def test_k_formula(self):
        r = check2_max_design_strain(**self._sample_args())
        expected_k = (1.5 * SAMPLE.Vll + 1.0 * SAMPLE.Vdl) / SAMPLE.Vmax
        assert abs(r.intermediates["k"] - expected_k) < 1e-4


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – CHECK 3: Plate Thickness
# ══════════════════════════════════════════════════════════════════════════════

class TestCheck3:

    def test_sample_passes(self):
        g = compute_geometry(SAMPLE)
        A1 = g.Ae * (1 - g.delta_b / g.be - g.delta_l / g.le)
        r = check3_plate_thickness(Vmax=SAMPLE.Vmax, A1=A1,
                                    t1=SAMPLE.te, t2=SAMPLE.ti,
                                    plate_thk=SAMPLE.plate_thk)
        assert r.status == "OK"

    def test_fails_when_plate_too_thin(self):
        # Force tmin > plate_thk by using a very thin plate
        r = check3_plate_thickness(Vmax=5000, A1=10000,
                                    t1=20, t2=20, plate_thk=1.0)
        assert r.status == "FAIL"

    def test_tmin_formula(self):
        g = compute_geometry(SAMPLE)
        A1 = g.Ae * (1 - g.delta_b / g.be - g.delta_l / g.le)
        r = check3_plate_thickness(Vmax=SAMPLE.Vmax, A1=A1,
                                    t1=SAMPLE.te, t2=SAMPLE.ti,
                                    plate_thk=SAMPLE.plate_thk)
        expected = (1.3 * SAMPLE.Vmax * 1000 * (SAMPLE.te + SAMPLE.ti)) / (A1 * 290)
        assert abs(r.tmin - expected) < 1e-6


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – CHECK 4: Stability
# ══════════════════════════════════════════════════════════════════════════════

class TestCheck4:

    def test_sample_passes(self):
        g = compute_geometry(SAMPLE)
        A1 = g.Ae * (1 - g.delta_b / g.be - g.delta_l / g.le)
        r = check4_stability(Vmax=SAMPLE.Vmax, A1=A1,
                              be=g.be, G=SAMPLE.G, S=g.S,
                              sum_ti=g.sum_ti)
        assert r.status == "OK"

    def test_fails_when_sum_ti_too_large(self):
        g = compute_geometry(SAMPLE)
        A1 = g.Ae * (1 - g.delta_b / g.be - g.delta_l / g.le)
        # sum_ti > be/4 forces geometry failure
        r = check4_stability(Vmax=SAMPLE.Vmax, A1=A1,
                              be=g.be, G=SAMPLE.G, S=g.S,
                              sum_ti=g.be)   # way too large
        assert r.status == "FAIL"


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – CHECK 5: Vertical Deflection
# ══════════════════════════════════════════════════════════════════════════════

class TestCheck5:

    def test_sample_fails(self):
        g = compute_geometry(SAMPLE)
        r = check5_vertical_deflection(Vmax=SAMPLE.Vmax, ti=SAMPLE.ti,
                                        Ae=g.Ae, G=SAMPLE.G, S=g.S,
                                        no_layers=g.no_layers)
        assert r.status == "FAIL"
        assert abs(r.delta_total - 1.59) < 0.02

    def test_passes_with_small_load(self):
        g = compute_geometry(SAMPLE)
        r = check5_vertical_deflection(Vmax=100, ti=SAMPLE.ti,
                                        Ae=g.Ae, G=SAMPLE.G, S=g.S,
                                        no_layers=g.no_layers)
        assert r.status == "OK"

    def test_limit_is_0_15_ti(self):
        g = compute_geometry(SAMPLE)
        r = check5_vertical_deflection(Vmax=SAMPLE.Vmax, ti=SAMPLE.ti,
                                        Ae=g.Ae, G=SAMPLE.G, S=g.S,
                                        no_layers=g.no_layers)
        assert abs(r.intermediates["0.15·ti (mm)"] - 0.15 * SAMPLE.ti) < 1e-9


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – CHECK 6: Rotational Limit
# ══════════════════════════════════════════════════════════════════════════════

class TestCheck6:

    def test_sample_passes(self):
        g = compute_geometry(SAMPLE)
        r = check6_rotational_limit(delta_total=1.5888, be=g.be, le=g.le,
                                     alpha_b=SAMPLE.alpha_b, alpha_l=SAMPLE.alpha_l)
        assert r.status == "OK"

    def test_fails_when_delta_tiny(self):
        # Very small delta_total → below rot_limit
        g = compute_geometry(SAMPLE)
        r = check6_rotational_limit(delta_total=0.001, be=g.be, le=g.le,
                                     alpha_b=0.01, alpha_l=0.01)
        assert r.status == "FAIL"


# ══════════════════════════════════════════════════════════════════════════════
# UNIT TESTS – CHECK 7: Fixing of Bearings
# ══════════════════════════════════════════════════════════════════════════════

class TestCheck7:

    def test_sample_passes(self):
        g = compute_geometry(SAMPLE)
        A1 = g.Ae * (1 - g.delta_b / g.be - g.delta_l / g.le)
        r = check7_fixing(l=SAMPLE.l, b=SAMPLE.b, G=SAMPLE.G,
                           delta_r=g.delta_r, tq=g.tq,
                           Vmax=SAMPLE.Vmax, Vdl=SAMPLE.Vdl, A1=A1)
        assert r.status == "OK"

    def test_sub_b_fails_when_vdl_tiny(self):
        g = compute_geometry(SAMPLE)
        A1 = g.Ae * (1 - g.delta_b / g.be - g.delta_l / g.le)
        # Vdl*1000/A1 must be > 2; if Vdl is tiny it fails
        r = check7_fixing(l=SAMPLE.l, b=SAMPLE.b, G=SAMPLE.G,
                           delta_r=g.delta_r, tq=g.tq,
                           Vmax=SAMPLE.Vmax, Vdl=0.001, A1=A1)
        assert r.status == "FAIL"


# ══════════════════════════════════════════════════════════════════════════════
# INPUT VALIDATION TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestValidation:

    def _valid(self):
        return dict(
            l=457, b=254, T=54, plate_thk=4.5, no_plates=4,
            te=10, ti=10, G=0.9,
            Vmax=1420, Vdl=384, Vll=1036,
            Hs=50, Ht=10,
            long_mvmt=10.6, trans_mvmt=4.19,
            alpha_b=0.0001, alpha_l=0,
        )

    def test_valid_input_no_errors(self):
        assert validate(self._valid()) == []

    def test_missing_field_returns_error(self):
        d = self._valid()
        del d["Vmax"]
        errors = validate(d)
        assert any("Vmax" in e for e in errors)

    def test_negative_l_returns_error(self):
        d = self._valid()
        d["l"] = -10
        errors = validate(d)
        assert any("'l'" in e for e in errors)

    def test_zero_G_returns_error(self):
        d = self._valid()
        d["G"] = 0
        errors = validate(d)
        assert any("'G'" in e for e in errors)

    def test_non_numeric_value_returns_error(self):
        d = self._valid()
        d["Vmax"] = "not_a_number"
        errors = validate(d)
        assert any("TYPE ERROR" in e for e in errors)

    def test_no_plates_less_than_2_returns_error(self):
        d = self._valid()
        d["no_plates"] = 1
        errors = validate(d)
        assert any("no_plates" in e for e in errors)

    def test_vdl_exceeds_vmax_returns_error(self):
        d = self._valid()
        d["Vdl"] = 9999
        errors = validate(d)
        assert any("Vdl" in e and "Vmax" in e for e in errors)

    def test_zero_T_returns_error(self):
        d = self._valid()
        d["T"] = 0
        errors = validate(d)
        assert any("'T'" in e for e in errors)

    def test_tq_negative_returns_error(self):
        # T too small vs no_plates * plate_thk
        d = self._valid()
        d["T"] = 1   # way too small
        errors = validate(d)
        assert any("tq" in e for e in errors)

    def test_negative_movement_returns_error(self):
        d = self._valid()
        d["long_mvmt"] = -5
        errors = validate(d)
        assert any("long_mvmt" in e for e in errors)

    def test_string_no_plates_returns_error(self):
        d = self._valid()
        d["no_plates"] = "four"
        errors = validate(d)
        assert any("no_plates" in e for e in errors)

    def test_all_zero_alphas_accepted(self):
        d = self._valid()
        d["alpha_b"] = 0
        d["alpha_l"] = 0
        assert validate(d) == []

    def test_zero_horizontal_forces_accepted(self):
        d = self._valid()
        d["Hs"] = 0
        d["Ht"] = 0
        assert validate(d) == []
