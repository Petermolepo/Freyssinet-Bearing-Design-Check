#!/usr/bin/env python3
"""
CI Stage 4 — CLI features and exports (in-process where possible).
"""

import json
import os
import sys
import tempfile

# Project root on path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from batch import run_batch
from bearing_types.registry import list_bearing_types
from engine import run_checks
from export.csv_export import export_csv_single
from export.pdf_export import export_pdf
from main import SAMPLE_INPUT, _build_input
from models import BearingInput
from outputs import format_explain, format_json
from validators import validate


def _sample_input() -> BearingInput:
    return _build_input(SAMPLE_INPUT)


def main() -> int:
    inp = _sample_input()
    result = run_checks(inp)

    # JSON output
    payload = json.loads(format_json(result))
    assert payload["overall"] == "BEARING FAILS"
    assert "Eq" in payload["check1_shear_strain"]

    # Explain / types
    assert "CHECK 1" in format_explain()
    assert len(list_bearing_types()) >= 1

    # Batch
    batch = run_batch(os.path.join(_ROOT, "batch_samples", "sample_batch.csv"))
    assert len(batch) >= 1

    # Exports
    with tempfile.TemporaryDirectory() as td:
        pdf = os.path.join(td, "test_report.pdf")
        csv = os.path.join(td, "test_report.csv")
        export_pdf(inp, result, pdf)
        export_csv_single(inp, result, csv)
        assert os.path.isfile(pdf), "PDF not created"
        assert os.path.isfile(csv), "CSV not created"

    # Bad input must fail validation (no crash)
    errors = validate({"l": "-1"})
    assert errors, "invalid input should produce validation errors"

    # CLI exit code: calculation success => exit 0 even when bearing fails
    import subprocess

    proc = subprocess.run(
        [sys.executable, "main.py", "--sample"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        print("ERROR: main.py --sample should exit 0", file=sys.stderr)
        print(proc.stderr or proc.stdout, file=sys.stderr)
        return 1

    print("Feature smoke tests: all passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
