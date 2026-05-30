"""
web/app.py
==========
FastAPI backend for the Freyssinet Bearing Design Check Tool.

Endpoints:
  GET  /                      → Web UI (index.html)
  GET  /static/*              → CSS, JS assets
  POST /api/check             → Run all 7 checks (JSON)
  POST /api/check/pdf         → PDF report
  POST /api/check/csv         → CSV export
  GET  /api/types             → Bearing types
  GET  /api/health            → Health check
"""

import sys
import os
import io
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from models import BearingInput
from validators import validate
from engine import run_checks
from checks.geometry import compute_geometry
from bearing_types.registry import get_bearing_type, list_bearing_types

app = FastAPI(
    title="Freyssinet Bearing Design Check Tool",
    description="Runs all 7 Freyssinet design checks for elastomeric bridge bearings.",
    version="1.0.0",
)

_STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_PRESENTATION_HTML = os.path.join(_PROJECT_ROOT, "presentation", "index.html")
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


class BearingRequest(BaseModel):
    l: float = Field(..., gt=0, description="Bearing length (mm)")
    b: float = Field(..., gt=0, description="Bearing width (mm)")
    T: float = Field(..., gt=0, description="Total bearing height (mm)")
    plate_thk: float = Field(..., gt=0, description="Steel plate thickness (mm)")
    no_plates: int = Field(..., ge=2, description="Number of steel plates")
    te: float = Field(..., gt=0, description="Edge rubber layer thickness (mm)")
    ti: float = Field(..., gt=0, description="Internal rubber layer thickness (mm)")
    G: float = Field(..., gt=0, description="Shear modulus (N/mm²)")
    Vmax: float = Field(..., gt=0, description="Maximum vertical load (kN)")
    Vdl: float = Field(..., ge=0, description="Dead load (kN)")
    Vll: float = Field(..., ge=0, description="Live load (kN)")
    Hs: float = Field(..., ge=0, description="Longitudinal shear force (kN)")
    Ht: float = Field(..., ge=0, description="Transverse shear force (kN)")
    long_mvmt: float = Field(..., ge=0, description="Longitudinal movement (mm)")
    trans_mvmt: float = Field(..., ge=0, description="Transverse movement (mm)")
    alpha_b: float = Field(..., ge=0, description="Rotation alpha_b (radians)")
    alpha_l: float = Field(..., ge=0, description="Rotation alpha_l (radians)")
    bearing_type: str = Field("pad", description="Bearing type: pad | laminated | pot")


def _req_payload(req: BearingRequest) -> dict:
    if hasattr(req, "model_dump"):
        return req.model_dump()
    return req.dict()


def _build(req: BearingRequest) -> BearingInput:
    data = _req_payload(req)
    data.pop("bearing_type", None)
    return BearingInput(**data)


def _geometry_dict(inp: BearingInput, bt) -> dict:
    g = compute_geometry(inp, cover_strip=bt.cover_strip_mm)
    return {
        "le": g.le,
        "be": g.be,
        "no_layers": g.no_layers,
        "tq": g.tq,
        "sum_ti": g.sum_ti,
        "Ae": g.Ae,
        "lp": g.lp,
        "S": g.S,
        "delta_bH": g.delta_bH,
        "delta_lH": g.delta_lH,
        "delta_b": g.delta_b,
        "delta_l": g.delta_l,
        "delta_r": g.delta_r,
    }


def _thresholds_dict(bt) -> dict:
    return {
        "check1_shear_strain": f"Eq < {bt.eq_limit} (spreadsheet); brief summary: Eq ≤ 1.0",
        "check2_max_design_strain": f"Et < {bt.et_limit} (spreadsheet); brief summary: Et ≤ 7.0",
        "check3_plate_thickness": "tmin < plate thickness (and plate > 2 mm)",
        "check4_stability": "V/A1 < limit and Σti < be/4",
        "check5_vertical_deflection": "▲Total < 0.15·ti",
        "check6_rotational_limit": "▲Total > (be·αb + le·αl)/3",
        "check7_fixing_of_bearings": "H < 0.1(V+2A1) and Vdl/A1 > 2 N/mm²",
    }


def _result_to_dict(result, geometry: dict, thresholds: dict) -> dict:
    def chk(c):
        d = {
            "status": c.status,
            "intermediates": c.intermediates,
            "message": c.message,
        }
        for attr in ("Eq", "Et", "tmin", "delta_total", "rot_limit"):
            if hasattr(c, attr):
                d[attr] = getattr(c, attr)
        return d

    return {
        "check1_shear_strain": chk(result.check1),
        "check2_max_design_strain": chk(result.check2),
        "check3_plate_thickness": chk(result.check3),
        "check4_stability": chk(result.check4),
        "check5_vertical_deflection": chk(result.check5),
        "check6_rotational_limit": chk(result.check6),
        "check7_fixing_of_bearings": chk(result.check7),
        "overall": result.overall,
        "bearing_type": result.bearing_type,
        "geometry": geometry,
        "thresholds": thresholds,
        "reference": {
            "source": "NC-DE-ESD_Test_ElastomericBearingDesign.xlsx (Freyssinet manual)",
            "note": "Pass/fail logic follows the spreadsheet formulas, which match the verification sample.",
        },
    }


def _run_validated(req: BearingRequest):
    raw = {k: str(v) for k, v in _req_payload(req).items() if k != "bearing_type"}
    errors = validate(raw)
    if errors:
        raise HTTPException(status_code=422, detail={"validation_errors": errors})
    try:
        bt = get_bearing_type(req.bearing_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    inp = _build(req)
    result = run_checks(inp, bt)
    return inp, result, bt


@app.get("/api/health")
def health():
    return {"status": "ok", "tool": "Freyssinet Bearing Design Check v1.0"}


@app.get("/api/types")
def bearing_types():
    return {"types": list_bearing_types()}


@app.post("/api/check")
def check_bearing(req: BearingRequest):
    inp, result, bt = _run_validated(req)
    geo = _geometry_dict(inp, bt)
    return _result_to_dict(result, geo, _thresholds_dict(bt))


@app.post("/api/check/pdf")
def check_bearing_pdf(req: BearingRequest):
    inp, result, bt = _run_validated(req)
    from export.pdf_export import export_pdf

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp_path = tmp.name
    export_pdf(inp, result, tmp_path, bearing_type_code=bt.code)
    filename = f"bearing_{inp.l}x{inp.b}x{inp.T}.pdf"
    return FileResponse(
        tmp_path, media_type="application/pdf", filename=filename
    )


@app.post("/api/check/csv")
def check_bearing_csv(req: BearingRequest):
    inp, result, bt = _run_validated(req)
    from export.csv_export import results_to_csv_string

    csv_content = results_to_csv_string(inp, result, bearing_type_code=bt.code)
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=bearing_{inp.l}x{inp.b}.csv"
        },
    )


@app.get("/", response_class=HTMLResponse)
def root():
    index = os.path.join(_STATIC_DIR, "index.html")
    with open(index, encoding="utf-8") as f:
        return f.read()


@app.get("/presentation", response_class=HTMLResponse)
def presentation():
    """Assessment presentation deck (open in browser for interview prep)."""
    if not os.path.isfile(_PRESENTATION_HTML):
        raise HTTPException(
            status_code=404,
            detail=f"Presentation not found at {_PRESENTATION_HTML}",
        )
    with open(_PRESENTATION_HTML, encoding="utf-8") as f:
        return f.read()
