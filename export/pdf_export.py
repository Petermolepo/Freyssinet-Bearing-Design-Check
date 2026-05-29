"""
export/pdf_export.py
====================
Professional PDF report with Naidu branding, logo, and structured sections.
"""

import os
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from bearing_types.registry import PAD_BEARING, get_bearing_type
from checks.geometry import compute_geometry
from engine import BearingResult
from models import BearingInput

NAIDU_GREEN = colors.HexColor("#8DC63F")
GREEN_DARK = colors.HexColor("#5A8F1E")
DARK = colors.HexColor("#1A1A1A")
MID = colors.HexColor("#666666")
LIGHT = colors.HexColor("#F4F6F0")
FAIL_RED = colors.HexColor("#C62828")
PASS_GREEN = colors.HexColor("#2E7D32")
WHITE = colors.white
BORDER = colors.HexColor("#D4E4BC")

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm

_LOGO_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "..", "web", "static", "img", "naidu-logo.jpg"),
    os.path.join(os.path.dirname(__file__), "..", "naidu_logo_listings-250x250.jpg"),
]


def _logo_path() -> Optional[str]:
    for p in _LOGO_CANDIDATES:
        if os.path.isfile(p):
            return os.path.abspath(p)
    return None


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=DARK,
            spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=9,
            textColor=MID,
            spaceAfter=2,
        ),
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=GREEN_DARK,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "small": ParagraphStyle(
            "small",
            fontName="Helvetica",
            fontSize=7.5,
            textColor=MID,
        ),
        "verdict_pass": ParagraphStyle(
            "verdict_pass",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=PASS_GREEN,
            alignment=TA_CENTER,
        ),
        "verdict_fail": ParagraphStyle(
            "verdict_fail",
            fontName="Helvetica-Bold",
            fontSize=13,
            textColor=FAIL_RED,
            alignment=TA_CENTER,
        ),
    }


def _table_style_header() -> list:
    return [
        ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]


def _letterhead(inp: BearingInput, result: BearingResult) -> list:
    """Top banner with logo and report metadata."""
    s = _styles()
    elements = []
    usable = PAGE_W - 2 * MARGIN
    logo_file = _logo_path()

    left_cells = []
    if logo_file:
        img = Image(logo_file, width=22 * mm, height=22 * mm)
        img.hAlign = "LEFT"
        left_cells.append(img)
    else:
        left_cells.append(
            Paragraph(
                '<font color="#8DC63F"><b>NAIDU</b></font>',
                ParagraphStyle("lg", fontName="Helvetica-Bold", fontSize=14),
            )
        )

    right_block = [
        Paragraph("Freyssinet Elastomeric Bearing Design Check", s["title"]),
        Paragraph("Naidu Consulting · Digital Engineering", s["subtitle"]),
        Paragraph(
            f"Bearing {inp.l} × {inp.b} × {inp.T} mm  ·  "
            f"{datetime.now().strftime('%d %B %Y, %H:%M')}",
            s["subtitle"],
        ),
    ]

    banner = Table(
        [[left_cells[0], right_block]],
        colWidths=[26 * mm, usable - 26 * mm],
    )
    banner.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(banner)
    elements.append(
        HRFlowable(width="100%", thickness=3, color=NAIDU_GREEN, spaceAfter=10)
    )
    return elements


def _kv_table(title: str, pairs: list[tuple[str, str]]) -> Table:
    data = [[title, ""]]
    data.append(["Parameter", "Value"])
    data.extend([[k, v] for k, v in pairs])
    col_w = [(PAGE_W - 2 * MARGIN) * 0.55, (PAGE_W - 2 * MARGIN) * 0.45]
    t = Table(data, colWidths=col_w)
    style = _table_style_header()
    style.insert(0, ("SPAN", (0, 0), (1, 0)))
    style.insert(1, ("BACKGROUND", (0, 0), (1, 0), NAIDU_GREEN))
    style.insert(2, ("TEXTCOLOR", (0, 0), (1, 0), WHITE))
    style.insert(3, ("FONTNAME", (0, 0), (1, 0), "Helvetica-Bold"))
    style.insert(4, ("FONTSIZE", (0, 0), (1, 0), 9))
    t.setStyle(TableStyle(style))
    return t


def _geometry_table(inp: BearingInput, bt) -> Table:
    g = compute_geometry(inp, cover_strip=bt.cover_strip_mm)
    pairs = [
        ("Effective length le (mm)", f"{g.le:.2f}"),
        ("Effective width be (mm)", f"{g.be:.2f}"),
        ("Rubber layers", str(g.no_layers)),
        ("Total rubber tq (mm)", f"{g.tq:.2f}"),
        ("Σti (mm)", f"{g.sum_ti:.2f}"),
        ("Plan area Ae (mm²)", f"{g.Ae:.2f}"),
        ("Shape factor S", f"{g.S:.4f}"),
        ("δb / δl / δr (mm)", f"{g.delta_b:.3f} / {g.delta_l:.3f} / {g.delta_r:.3f}"),
    ]
    return _kv_table("Derived geometry", pairs)


def _inputs_table(inp: BearingInput) -> Table:
    pairs = [
        ("Length l", f"{inp.l} mm"),
        ("Width b", f"{inp.b} mm"),
        ("Height T", f"{inp.T} mm"),
        ("Plate thickness", f"{inp.plate_thk} mm"),
        ("No. of plates", str(inp.no_plates)),
        ("te / ti", f"{inp.te} / {inp.ti} mm"),
        ("Shear modulus G", f"{inp.G} N/mm²"),
        ("Vmax / Vdl / Vll", f"{inp.Vmax} / {inp.Vdl} / {inp.Vll} kN"),
        ("Hs / Ht", f"{inp.Hs} / {inp.Ht} kN"),
        ("Movements (long / trans)", f"{inp.long_mvmt} / {inp.trans_mvmt} mm"),
        ("Rotations αb / αl", f"{inp.alpha_b} / {inp.alpha_l} rad"),
    ]
    return _kv_table("Input parameters", pairs)


def _results_table(result: BearingResult, bt) -> Table:
    checks = [
        ("1", "Shear strain", result.check1, f"Eq = {result.check1.Eq:.4f}", f"Eq < {bt.eq_limit}"),
        ("2", "Max design strain", result.check2, f"Et = {result.check2.Et:.4f}", f"Et < {bt.et_limit}"),
        ("3", "Plate thickness", result.check3, f"tmin = {result.check3.tmin:.4f} mm", "tmin < plate"),
        ("4", "Stability", result.check4,
         f"V/A1 = {result.check4.intermediates['V/A1 (N/mm²)']:.3f}",
         "Stress & geometry"),
        ("5", "Vertical deflection", result.check5,
         f"▲ = {result.check5.delta_total:.4f} mm", "▲ < 0.15·ti"),
        ("6", "Rotational limit", result.check6,
         f"▲ = {result.check6.delta_total:.4f} mm", "▲ > limit"),
        ("7", "Fixing of bearings", result.check7, "Sub-checks a & b", "H & V/A1"),
    ]

    data = [["#", "Check", "Key value", "Criterion", "Result"]]
    for num, name, chk, kv, crit in checks:
        data.append([num, name, kv, crit, chk.status])

    col_w = [10 * mm, 42 * mm, 42 * mm, 38 * mm, 18 * mm]
    t = Table(data, colWidths=col_w)
    style = _table_style_header()
    style.append(("ALIGN", (0, 1), (0, -1), "CENTER"))
    style.append(("ALIGN", (-1, 1), (-1, -1), "CENTER"))

    for i, (_, _, chk, _, _) in enumerate(checks, start=1):
        col = PASS_GREEN if chk.status == "OK" else FAIL_RED
        style.append(("TEXTCOLOR", (-1, i), (-1, i), col))
        style.append(("FONTNAME", (-1, i), (-1, i), "Helvetica-Bold"))

    t.setStyle(TableStyle(style))
    return t


def _intermediates_block(title: str, chk) -> list:
    s = _styles()
    out = [Paragraph(title, s["section"])]
    data = [["Intermediate", "Value"]]
    for k, v in chk.intermediates.items():
        if isinstance(v, bool):
            val = "✓" if v else "✗"
        elif isinstance(v, float):
            val = f"{v:.6f}"
        else:
            val = str(v)
        data.append([k, val])

    col_w = [(PAGE_W - 2 * MARGIN) * 0.6, (PAGE_W - 2 * MARGIN) * 0.4]
    t = Table(data, colWidths=col_w)
    t.setStyle(TableStyle(_table_style_header()))
    out.append(t)
    if chk.message:
        out.append(Spacer(1, 2 * mm))
        out.append(
            Paragraph(
                f"<i>{chk.message}</i>",
                ParagraphStyle("note", fontName="Helvetica-Oblique", fontSize=8, textColor=MID),
            )
        )
    out.append(Spacer(1, 4 * mm))
    return out


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(MID)
    canvas.drawString(
        MARGIN,
        12 * mm,
        "Naidu Consulting · Freyssinet Bearing Design Check · Verify with a qualified engineer",
    )
    canvas.drawRightString(PAGE_W - MARGIN, 12 * mm, f"Page {doc.page}")
    canvas.restoreState()


def export_pdf(
    inp: BearingInput,
    result: BearingResult,
    output_path: str,
    bearing_type_code: str = "pad",
) -> str:
    """Generate a branded PDF report."""
    bt = get_bearing_type(bearing_type_code) if bearing_type_code else PAD_BEARING
    s = _styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=22 * mm,
    )

    story = []
    story.extend(_letterhead(inp, result))

    # Verdict first (executive summary)
    is_pass = result.overall == "BEARING PASSES"
    verdict_style = s["verdict_pass"] if is_pass else s["verdict_fail"]
    verdict_bg = colors.HexColor("#E8F5E9") if is_pass else colors.HexColor("#FFEBEE")
    verdict_border = PASS_GREEN if is_pass else FAIL_RED

    verdict_tbl = Table(
        [[Paragraph(f"●  {result.overall}", verdict_style)]],
        colWidths=[PAGE_W - 2 * MARGIN],
    )
    verdict_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), verdict_bg),
                ("BOX", (0, 0), (-1, -1), 1.5, verdict_border),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(verdict_tbl)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("Design check summary", s["section"]))
    story.append(_results_table(result, bt))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Input & geometry", s["section"]))
    story.append(_inputs_table(inp))
    story.append(Spacer(1, 4 * mm))
    story.append(_geometry_table(inp, bt))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("Detailed intermediate values", s["section"]))
    story.append(Spacer(1, 2 * mm))

    details = [
        ("Check 1 — Shear strain", result.check1),
        ("Check 2 — Maximum design strain", result.check2),
        ("Check 3 — Plate thickness", result.check3),
        ("Check 4 — Stability", result.check4),
        ("Check 5 — Vertical deflection", result.check5),
        ("Check 6 — Rotational limit", result.check6),
        ("Check 7 — Fixing of bearings", result.check7),
    ]
    for i, (name, chk) in enumerate(details):
        if i == 4:
            story.append(PageBreak())
        story.extend(_intermediates_block(name, chk))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
    story.append(
        Paragraph(
            "This report was generated by the Freyssinet Bearing Design Check Tool. "
            "Calculations follow the provided Freyssinet spreadsheet. "
            "Results must be verified by a qualified structural engineer.",
            s["small"],
        )
    )

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return output_path
