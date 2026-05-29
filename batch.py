"""
batch.py
========
Run design checks on multiple bearings defined in a CSV file.

CSV format: one row per bearing, column headers = input parameter names.
An optional 'label' column provides a name for each bearing.
Results are printed as a summary table and optionally exported.
"""

import csv
import sys
from typing import List, Tuple

from models import BearingInput
from validators import validate
from engine import run_checks, BearingResult

_USE_COLOUR = sys.stdout.isatty()
_GREEN  = "\033[92m" if _USE_COLOUR else ""
_RED    = "\033[91m" if _USE_COLOUR else ""
_BOLD   = "\033[1m"  if _USE_COLOUR else ""
_RESET  = "\033[0m"  if _USE_COLOUR else ""

REQUIRED_COLS = [
    "l","b","T","plate_thk","no_plates","te","ti","G",
    "Vmax","Vdl","Vll","Hs","Ht","long_mvmt","trans_mvmt","alpha_b","alpha_l",
]


def load_batch_csv(path: str) -> List[Tuple[str, dict]]:
    """
    Read a batch CSV file.
    Returns list of (label, raw_dict) tuples.
    Raises ValueError with a clear message on bad format.
    """
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV file '{path}' appears to be empty.")

        # Check required columns (ignore _comment etc.)
        headers = [h.strip() for h in reader.fieldnames if not h.startswith("_")]
        missing = [c for c in REQUIRED_COLS if c not in headers]
        if missing:
            raise ValueError(
                f"CSV file missing required columns: {missing}\n"
                f"  Found columns: {headers}"
            )

        rows = []
        for i, row in enumerate(reader, start=2):   # row 1 = header
            label = row.get("label", f"Bearing_{i-1}").strip()
            raw = {k: row[k].strip() for k in REQUIRED_COLS}
            rows.append((label, raw))

    if not rows:
        raise ValueError(f"CSV file '{path}' contains no data rows.")

    return rows


def run_batch(path: str, bearing_type=None) -> List[Tuple[str, BearingInput, BearingResult, List[str]]]:
    """
    Load and run all bearings in a CSV file.

    Returns list of (label, BearingInput, BearingResult, errors) tuples.
    errors is an empty list on success, populated on validation failure.
    """
    rows = load_batch_csv(path)
    results = []

    for label, raw in rows:
        errors = validate(raw)
        if errors:
            results.append((label, None, None, errors))
            continue

        inp = BearingInput(
            l=float(raw["l"]), b=float(raw["b"]), T=float(raw["T"]),
            plate_thk=float(raw["plate_thk"]), no_plates=int(raw["no_plates"]),
            te=float(raw["te"]), ti=float(raw["ti"]),
            G=float(raw["G"]),
            Vmax=float(raw["Vmax"]), Vdl=float(raw["Vdl"]), Vll=float(raw["Vll"]),
            Hs=float(raw["Hs"]), Ht=float(raw["Ht"]),
            long_mvmt=float(raw["long_mvmt"]), trans_mvmt=float(raw["trans_mvmt"]),
            alpha_b=float(raw["alpha_b"]), alpha_l=float(raw["alpha_l"]),
        )
        result = run_checks(inp, bearing_type)
        results.append((label, inp, result, []))

    return results


def format_batch_summary(
    results: List[Tuple[str, BearingInput, BearingResult, List[str]]]
) -> str:
    """Print a compact summary table of all batch results."""
    sep = "─" * 86
    lines = [sep]
    lines.append(f"  {'#':<4} {'LABEL':<20} {'C1':<5} {'C2':<5} {'C3':<5} {'C4':<5} {'C5':<5} {'C6':<5} {'C7':<5} {'OVERALL'}")
    lines.append(sep)

    passes = 0
    fails  = 0
    errors = 0

    for i, (label, inp, result, errs) in enumerate(results, start=1):
        if errs:
            lines.append(f"  {i:<4} {label:<20} {'INPUT ERROR – ' + errs[0][:40]}")
            errors += 1
            continue

        checks = [result.check1, result.check2, result.check3, result.check4,
                  result.check5, result.check6, result.check7]

        def fmt(c):
            if c.status == "OK":
                return f"{_GREEN}OK {_RESET}"
            return f"{_RED}FAIL{_RESET}"

        verdict = (f"{_GREEN}{_BOLD}PASSES{_RESET}"
                   if result.overall == "BEARING PASSES"
                   else f"{_RED}{_BOLD}FAILS {_RESET}")

        lines.append(
            f"  {i:<4} {label:<20} "
            + "  ".join(fmt(c) for c in checks)
            + f"  {verdict}"
        )

        if result.overall == "BEARING PASSES":
            passes += 1
        else:
            fails += 1

    lines.append(sep)
    total = len(results)
    lines.append(
        f"\n  Total: {total}  |  "
        f"{_GREEN}Passes: {passes}{_RESET}  |  "
        f"{_RED}Fails: {fails}{_RESET}  |  "
        f"Input errors: {errors}\n"
    )
    lines.append(sep)
    return "\n".join(lines)
