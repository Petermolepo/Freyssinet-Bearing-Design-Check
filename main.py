#!/usr/bin/env python3
"""
main.py – Freyssinet Elastomeric Bearing Design Check Tool
==========================================================

QUICK REFERENCE
───────────────
  python main.py --sample                          Verification sample (table)
  python main.py --sample --verbose                All intermediate values
  python main.py --sample --json                   JSON output
  python main.py --sample --export-pdf report.pdf  Save PDF report
  python main.py --sample --export-csv report.csv  Save CSV report
  python main.py --input bearing.json              Run from JSON file
  python main.py --interactive                     Prompt for each value
  python main.py --batch batch_samples/sample_batch.csv   Run multiple bearings
  python main.py --compare bearing_a.json bearing_b.json  Compare two designs
  python main.py --types                           List supported bearing types
  python main.py --explain                         Print formula reference
  python main.py --web                             Start local web UI (port 8000)

FLAGS (combinable)
  --type pad|laminated|pot    Bearing type (default: pad)
  --json                      Output as JSON
  --verbose                   Show all intermediate values
  --export-pdf <file>         Also save a PDF report
  --export-csv <file>         Also save a CSV report
"""

import argparse
import json
import sys
import os

from models import BearingInput
from validators import validate
from engine import run_checks
from outputs import format_table, format_full, format_json, format_explain
from compare import format_comparison
from batch import run_batch, format_batch_summary
from bearing_types.registry import get_bearing_type, list_bearing_types


# ── Sample input (official verification case) ───────────────────────────────
SAMPLE_INPUT = {
    "l": 457, "b": 254, "T": 54,
    "plate_thk": 4.5, "no_plates": 4,
    "te": 10, "ti": 10, "G": 0.9,
    "Vmax": 1420, "Vdl": 384, "Vll": 1036,
    "Hs": 50, "Ht": 10,
    "long_mvmt": 10.6, "trans_mvmt": 4.19,
    "alpha_b": 0.0001, "alpha_l": 0,
}

# ── Interactive prompts ──────────────────────────────────────────────────────
PROMPTS = [
    ("l",         "Bearing length l (mm)",                       float),
    ("b",         "Bearing width b (mm)",                        float),
    ("T",         "Total bearing height T (mm)",                 float),
    ("plate_thk", "Steel plate thickness (mm)",                  float),
    ("no_plates", "Number of steel plates",                      int),
    ("te",        "Edge rubber layer thickness te (mm)",         float),
    ("ti",        "Internal rubber layer thickness ti (mm)",     float),
    ("G",         "Shear modulus G (N/mm²)",                     float),
    ("Vmax",      "Maximum vertical load Vmax (kN)",             float),
    ("Vdl",       "Dead load Vdl (kN)",                         float),
    ("Vll",       "Live load Vll (kN)",                         float),
    ("Hs",        "Longitudinal horizontal shear Hs (kN)",       float),
    ("Ht",        "Transverse horizontal shear Ht (kN)",         float),
    ("long_mvmt", "Longitudinal movement (mm)",                  float),
    ("trans_mvmt","Transverse movement (mm)",                    float),
    ("alpha_b",   "Rotation alpha_b (radians)",                  float),
    ("alpha_l",   "Rotation alpha_l (radians)",                  float),
]


def _build_input(raw: dict) -> BearingInput:
    return BearingInput(
        l=float(raw["l"]), b=float(raw["b"]), T=float(raw["T"]),
        plate_thk=float(raw["plate_thk"]), no_plates=int(raw["no_plates"]),
        te=float(raw["te"]), ti=float(raw["ti"]),
        G=float(raw["G"]),
        Vmax=float(raw["Vmax"]), Vdl=float(raw["Vdl"]), Vll=float(raw["Vll"]),
        Hs=float(raw["Hs"]), Ht=float(raw["Ht"]),
        long_mvmt=float(raw["long_mvmt"]), trans_mvmt=float(raw["trans_mvmt"]),
        alpha_b=float(raw["alpha_b"]), alpha_l=float(raw["alpha_l"]),
    )


def _load_json(path: str) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}")
        sys.exit(1)


def _maybe_export(inp, result, args):
    """Handle optional --export-pdf and --export-csv flags."""
    if args.export_pdf:
        try:
            from export.pdf_export import export_pdf
            export_pdf(inp, result, args.export_pdf)
            print(f"\n  ✔  PDF saved → {args.export_pdf}")
        except Exception as e:
            print(f"\n  ✗  PDF export failed: {e}")

    if args.export_csv:
        try:
            from export.csv_export import export_csv_single
            export_csv_single(inp, result, args.export_csv)
            print(f"  ✔  CSV saved → {args.export_csv}")
        except Exception as e:
            print(f"  ✗  CSV export failed: {e}")


def _run_and_print(raw: dict, args, bt=None) -> int:
    errors = validate(raw)
    if errors:
        print("\n[INPUT ERRORS]")
        for e in errors:
            print(f"  • {e}")
        print()
        return 1

    inp    = _build_input(raw)
    result = run_checks(inp, bt)

    if args.json:
        print(format_json(result))
    elif args.verbose:
        print(format_full(result))
    else:
        print(format_table(result))

    _maybe_export(inp, result, args)
    return 0 if result.overall == "BEARING PASSES" else 1


def _interactive_mode(args, bt) -> int:
    print("\n  Freyssinet Bearing Design Check – Interactive Mode")
    print("  Enter each parameter value when prompted.\n")
    raw = {}
    for key, label, cast in PROMPTS:
        while True:
            try:
                val = input(f"  {label}: ").strip()
                raw[key] = cast(val)
                break
            except ValueError:
                print(f"    ✗  Expected a {'whole number' if cast is int else 'number'}. Try again.")
    print()
    return _run_and_print(raw, args, bt)


def _batch_mode(args, bt) -> int:
    try:
        results = run_batch(args.batch, bt)
    except (ValueError, FileNotFoundError) as e:
        print(f"BATCH ERROR: {e}")
        return 1

    print(format_batch_summary(results))

    if args.export_csv:
        try:
            from export.csv_export import export_csv_batch
            valid = [(inp, res, lbl) for lbl, inp, res, errs in results if not errs]
            if valid:
                export_csv_batch(valid, args.export_csv)
                print(f"  ✔  Batch CSV saved → {args.export_csv}")
        except Exception as e:
            print(f"  ✗  CSV export failed: {e}")

    any_fail = any(
        (not errs and res.overall != "BEARING PASSES")
        for _, inp, res, errs in results
    )
    return 1 if any_fail else 0


def _compare_mode(args, bt) -> int:
    raw_a = _load_json(args.compare[0])
    raw_b = _load_json(args.compare[1])

    errs_a = validate(raw_a)
    errs_b = validate(raw_b)

    if errs_a:
        print(f"[INPUT ERRORS in {args.compare[0]}]")
        for e in errs_a:
            print(f"  • {e}")
        return 1
    if errs_b:
        print(f"[INPUT ERRORS in {args.compare[1]}]")
        for e in errs_b:
            print(f"  • {e}")
        return 1

    inp_a = _build_input(raw_a)
    inp_b = _build_input(raw_b)
    res_a = run_checks(inp_a, bt)
    res_b = run_checks(inp_b, bt)

    label_a = os.path.splitext(os.path.basename(args.compare[0]))[0]
    label_b = os.path.splitext(os.path.basename(args.compare[1]))[0]

    print(format_comparison(inp_a, res_a, label_a, inp_b, res_b, label_b))
    return 0


def _start_web(args) -> int:
    try:
        import uvicorn
        from web.app import app
    except ImportError:
        print("ERROR: Web UI requires fastapi and uvicorn.")
        print("  Run:  pip install -r requirements.txt")
        return 1

    port = getattr(args, "port", 8000)
    print("\n  Starting Freyssinet Bearing Design Check Web UI…")
    print(f"  Open your browser at:  http://localhost:{port}\n")
    try:
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
    except OSError as e:
        if getattr(e, "winerror", None) == 10048 or "address already in use" in str(e).lower():
            print(f"ERROR: Port {port} is already in use.")
            print(f"  Stop the other process or run:  python main.py --web --port {port + 1}")
        else:
            print(f"ERROR: Could not start server: {e}")
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Freyssinet Elastomeric Bearing Design Check Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # ── Mode (mutually exclusive) ─────────────────────────────────────────
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sample",      action="store_true",
                      help="Run with the verification sample input")
    mode.add_argument("--input",       metavar="FILE",
                      help="JSON file containing bearing input parameters")
    mode.add_argument("--interactive", action="store_true",
                      help="Prompt for each input value interactively")
    mode.add_argument("--batch",       metavar="CSV_FILE",
                      help="Run multiple bearings from a CSV file")
    mode.add_argument("--compare",     metavar="FILE", nargs=2,
                      help="Compare two bearing JSON files side by side")
    mode.add_argument("--explain",     action="store_true",
                      help="Print formula reference sheet and exit")
    mode.add_argument("--types",       action="store_true",
                      help="List all supported bearing types")
    mode.add_argument("--web",         action="store_true",
                      help="Start the web UI on http://localhost:8000")

    # ── Options ───────────────────────────────────────────────────────────
    parser.add_argument("--port",       type=int, default=8000,
                        help="Web server port (with --web, default: 8000)")
    parser.add_argument("--type",       default="pad",
                        help="Bearing type: pad | laminated | pot  (default: pad)")
    parser.add_argument("--json",       action="store_true",
                        help="Output results as JSON")
    parser.add_argument("--verbose",    action="store_true",
                        help="Show all intermediate values per check")
    parser.add_argument("--export-pdf", metavar="FILE",
                        help="Save a PDF report to FILE")
    parser.add_argument("--export-csv", metavar="FILE",
                        help="Save a CSV report to FILE")

    args = parser.parse_args()

    # ── Bearing type ──────────────────────────────────────────────────────
    try:
        bt = get_bearing_type(args.type)
        if bt.code != "pad":
            print(f"\n  [Bearing type: {bt.name}]")
            if bt.notes:
                print(f"  Note: {bt.notes}\n")
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1

    # ── Dispatch ──────────────────────────────────────────────────────────
    if args.explain:
        print(format_explain())
        return 0

    if args.types:
        print("\n  Supported bearing types:\n")
        for t in list_bearing_types():
            print(f"  --type {t['code']:<12}  {t['name']}")
            print(f"  {'':14}  {t['description']}")
            if t['notes']:
                print(f"  {'':14}  ⚠  {t['notes']}")
            print()
        return 0

    if args.web:
        return _start_web(args)

    if args.sample:
        print("\n  [Running with verification sample input]\n")
        return _run_and_print(SAMPLE_INPUT, args, bt)

    if args.input:
        raw = _load_json(args.input)
        return _run_and_print(raw, args, bt)

    if args.interactive:
        return _interactive_mode(args, bt)

    if args.batch:
        return _batch_mode(args, bt)

    if args.compare:
        return _compare_mode(args, bt)


if __name__ == "__main__":
    sys.exit(main())
