"""
export/csv_export.py
====================
Professional multi-section CSV reports for bearing design checks.
Structured for clarity in Excel: titled sections, labelled columns, grouped data.
"""

import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from checks.geometry import compute_geometry
from bearing_types.registry import PAD_BEARING, get_bearing_type
from engine import BearingResult
from models import BearingInput

REPORT_TITLE = "Freyssinet Elastomeric Bearing Design Check Report"
ORGANISATION = "Naidu Consulting — Digital Engineering"


def _blank_row() -> List[str]:
    return [""]


def _section_title(title: str) -> List[str]:
    return [title]


def _two_col_table(rows: List[Tuple[str, Any, str]]) -> List[List[str]]:
    """rows: (label, value, unit_or_notes)"""
    out = [["Parameter", "Value", "Unit / Notes"]]
    for label, value, unit in rows:
        if isinstance(value, float):
            display = f"{value:.6g}"
        elif isinstance(value, bool):
            display = "Yes" if value else "No"
        else:
            display = str(value)
        out.append([label, display, unit])
    return out


def _build_report_rows(
    inp: BearingInput,
    result: BearingResult,
    label: Optional[str] = None,
    bearing_type_code: str = "pad",
) -> List[List[str]]:
    """Build a full sectioned report as rows (ragged width allowed)."""
    bt = get_bearing_type(bearing_type_code) if bearing_type_code else PAD_BEARING
    geo = compute_geometry(inp, cover_strip=bt.cover_strip_mm)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    size = f"{inp.l} × {inp.b} × {inp.T} mm"

    rows: List[List[str]] = []

    # ── Cover ─────────────────────────────────────────────────────────────
    rows.append([REPORT_TITLE])
    rows.append([ORGANISATION])
    rows.append(["Generated", ts])
    if label:
        rows.append(["Bearing label", label])
    rows.append(["Bearing size", size])
    rows.append(["Bearing type", result.bearing_type or bearing_type_code])
    rows.append(["Overall result", result.overall])
    rows.append(_blank_row())

    # ── 1. Input parameters ───────────────────────────────────────────────
    rows.append(_section_title("1. INPUT PARAMETERS"))
    rows.extend(
        _two_col_table([
            ("Length l", inp.l, "mm"),
            ("Width b", inp.b, "mm"),
            ("Total height T", inp.T, "mm"),
            ("Plate thickness", inp.plate_thk, "mm"),
            ("Number of steel plates", inp.no_plates, "—"),
            ("Edge rubber thickness te", inp.te, "mm"),
            ("Internal rubber thickness ti", inp.ti, "mm"),
            ("Shear modulus G", inp.G, "N/mm²"),
            ("Maximum vertical load Vmax", inp.Vmax, "kN"),
            ("Dead load Vdl", inp.Vdl, "kN"),
            ("Live load Vll", inp.Vll, "kN"),
            ("Longitudinal shear Hs", inp.Hs, "kN"),
            ("Transverse shear Ht", inp.Ht, "kN"),
            ("Longitudinal movement", inp.long_mvmt, "mm"),
            ("Transverse movement", inp.trans_mvmt, "mm"),
            ("Rotation αb", inp.alpha_b, "radians"),
            ("Rotation αl", inp.alpha_l, "radians"),
        ])
    )
    rows.append(_blank_row())

    # ── 2. Derived geometry ─────────────────────────────────────────────────
    rows.append(_section_title("2. DERIVED GEOMETRY (spreadsheet)"))
    rows.extend(
        _two_col_table([
            ("Effective length le", geo.le, "mm  (l − 10)"),
            ("Effective width be", geo.be, "mm  (b − 10)"),
            ("Number of rubber layers", geo.no_layers, "no_plates − 1"),
            ("Total rubber thickness tq", geo.tq, "mm"),
            ("Sum of internal layers Σti", geo.sum_ti, "mm"),
            ("Plan area Ae", geo.Ae, "mm²"),
            ("Perimeter lp", geo.lp, "mm"),
            ("Shape factor S", geo.S, "—"),
            ("Shear δb (long.)", geo.delta_b, "mm"),
            ("Shear δl (trans.)", geo.delta_l, "mm"),
            ("Resultant shear δr", geo.delta_r, "mm"),
        ])
    )
    rows.append(_blank_row())

    # ── 3. Summary ──────────────────────────────────────────────────────────
    rows.append(_section_title("3. DESIGN CHECK SUMMARY"))
    rows.append(
        ["Check", "Name", "Status", "Key value", "Pass criterion", "Remarks"]
    )

    summary = [
        (
            "1",
            "Shear strain",
            result.check1,
            f"Eq = {result.check1.Eq:.4f}",
            f"Eq < {bt.eq_limit}",
        ),
        (
            "2",
            "Maximum design strain",
            result.check2,
            f"Et = {result.check2.Et:.4f}",
            f"Et < {bt.et_limit}",
        ),
        (
            "3",
            "Plate thickness",
            result.check3,
            f"tmin = {result.check3.tmin:.4f} mm",
            "tmin < plate thickness",
        ),
        (
            "4",
            "Stability",
            result.check4,
            f"V/A1 = {result.check4.intermediates['V/A1 (N/mm²)']:.4f} N/mm²",
            "V/A1 and Σti limits",
        ),
        (
            "5",
            "Vertical deflection",
            result.check5,
            f"▲Total = {result.check5.delta_total:.4f} mm",
            "▲Total < 0.15·ti",
        ),
        (
            "6",
            "Rotational limit",
            result.check6,
            f"▲ = {result.check6.delta_total:.4f} mm",
            "▲ > rot_limit",
        ),
        (
            "7",
            "Fixing of bearings",
            result.check7,
            "Sub-checks a & b",
            "H and V/A1 limits",
        ),
    ]

    for num, name, chk, key_val, criterion in summary:
        rows.append([num, name, chk.status, key_val, criterion, chk.message or ""])

    rows.append(_blank_row())
    rows.append(["OVERALL VERDICT", result.overall])
    rows.append(_blank_row())

    # ── 4. Detailed intermediates ───────────────────────────────────────────
    rows.append(_section_title("4. DETAILED INTERMEDIATE VALUES"))
    check_blocks = [
        ("Check 1 — Shear strain", result.check1),
        ("Check 2 — Maximum design strain", result.check2),
        ("Check 3 — Plate thickness", result.check3),
        ("Check 4 — Stability", result.check4),
        ("Check 5 — Vertical deflection", result.check5),
        ("Check 6 — Rotational limit", result.check6),
        ("Check 7 — Fixing of bearings", result.check7),
    ]

    for title, chk in check_blocks:
        rows.append(_blank_row())
        rows.append([title, f"Status: {chk.status}"])
        rows.append(["Intermediate", "Value"])
        for k, v in chk.intermediates.items():
            if isinstance(v, bool):
                val = "PASS" if v else "FAIL"
            elif isinstance(v, float):
                val = f"{v:.6f}"
            else:
                val = str(v)
            rows.append([k, val])
        if chk.message:
            rows.append(["Engineer note", chk.message])

    rows.append(_blank_row())
    rows.append(
        [
            "Disclaimer",
            "Generated by the Freyssinet Bearing Design Check Tool. "
            "Verify all results with a qualified structural engineer before use.",
        ]
    )

    return rows


def _write_rows(path_or_buf, rows: List[List[str]], is_path: bool) -> None:
    """Write ragged rows; pad each row to max width in section for Excel."""
    max_cols = max(len(r) for r in rows) if rows else 1
    padded = [r + [""] * (max_cols - len(r)) for r in rows]

    if is_path:
        with open(path_or_buf, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerows(padded)
    else:
        writer = csv.writer(path_or_buf)
        writer.writerows(padded)


def _flat_row_legacy(inp: BearingInput, result: BearingResult,
                     label: Optional[str] = None) -> dict:
    """Single-row flat export for batch comparison (unchanged keys)."""
    row: Dict[str, Any] = {}
    if label:
        row["bearing_label"] = label
    row["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    row.update({
        "l_mm": inp.l, "b_mm": inp.b, "T_mm": inp.T,
        "plate_thk_mm": inp.plate_thk, "no_plates": inp.no_plates,
        "te_mm": inp.te, "ti_mm": inp.ti, "G_N_mm2": inp.G,
        "Vmax_kN": inp.Vmax, "Vdl_kN": inp.Vdl, "Vll_kN": inp.Vll,
        "Hs_kN": inp.Hs, "Ht_kN": inp.Ht,
        "long_mvmt_mm": inp.long_mvmt, "trans_mvmt_mm": inp.trans_mvmt,
        "alpha_b_rad": inp.alpha_b, "alpha_l_rad": inp.alpha_l,
        "check1_status": result.check1.status,
        "check1_Eq": round(result.check1.Eq, 6),
        "check2_status": result.check2.status,
        "check2_Et": round(result.check2.Et, 6),
        "check3_status": result.check3.status,
        "check4_status": result.check4.status,
        "check5_status": result.check5.status,
        "check5_delta_total_mm": round(result.check5.delta_total, 6),
        "check6_status": result.check6.status,
        "check7_status": result.check7.status,
        "overall": result.overall,
    })
    return row


def export_csv_single(
    inp: BearingInput,
    result: BearingResult,
    output_path: str,
    bearing_type_code: str = "pad",
) -> str:
    """Write a professional sectioned CSV report."""
    rows = _build_report_rows(inp, result, bearing_type_code=bearing_type_code)
    _write_rows(output_path, rows, is_path=True)
    return output_path


def export_csv_batch(
    batch: List[Tuple[BearingInput, BearingResult, str]],
    output_path: str,
) -> str:
    """
    Batch export: one summary row per bearing (for comparison),
    plus optional full reports are not combined — use single export per bearing.
    """
    if not batch:
        raise ValueError("Batch is empty — nothing to export.")

    rows: List[List[str]] = [
        [REPORT_TITLE, "Batch summary"],
        [ORGANISATION],
        ["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        _blank_row(),
        _section_title("BATCH COMPARISON"),
        [
            "Label", "l (mm)", "b (mm)", "T (mm)", "Overall",
            "Chk1", "Eq", "Chk2", "Et", "Chk3", "Chk4", "Chk5", "▲Total",
            "Chk6", "Chk7",
        ],
    ]

    for inp, res, label in batch:
        rows.append([
            label,
            inp.l, inp.b, inp.T,
            res.overall,
            res.check1.status, round(res.check1.Eq, 4),
            res.check2.status, round(res.check2.Et, 4),
            res.check3.status, res.check4.status,
            res.check5.status, round(res.check5.delta_total, 4),
            res.check6.status, res.check7.status,
        ])

    _write_rows(output_path, rows, is_path=True)
    return output_path


def results_to_csv_string(
    inp: BearingInput,
    result: BearingResult,
    bearing_type_code: str = "pad",
) -> str:
    """Return sectioned CSV content for the API endpoint."""
    rows = _build_report_rows(inp, result, bearing_type_code=bearing_type_code)
    buf = io.StringIO()
    _write_rows(buf, rows, is_path=False)
    return buf.getvalue()
