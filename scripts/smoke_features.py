#!/usr/bin/env python3
"""
CI Stage 4 smoke tests — CLI features and exports.
"""

import json
import os
import subprocess
import sys
import tempfile


def run(cmd, *, check=True, capture=False):
    return subprocess.run(
        cmd,
        check=check,
        capture_output=capture,
        text=True,
    )


def main() -> int:
    py = sys.executable

    # JSON output
    out = run([py, "main.py", "--sample", "--json"], capture=True).stdout
    json.loads(out)

    run([py, "main.py", "--input", "sample_input.json"])
    run([py, "main.py", "--explain"])
    run([py, "main.py", "--types"])
    run([py, "main.py", "--batch", "batch_samples/sample_batch.csv"])

    with tempfile.TemporaryDirectory() as td:
        pdf = os.path.join(td, "test_report.pdf")
        csv = os.path.join(td, "test_report.csv")
        run([py, "main.py", "--sample", "--export-pdf", pdf])
        run([py, "main.py", "--sample", "--export-csv", csv])
        assert os.path.isfile(pdf), "PDF not created"
        assert os.path.isfile(csv), "CSV not created"

    bad = os.path.join(tempfile.gettempdir(), "bearing_bad_input.json")
    with open(bad, "w", encoding="utf-8") as f:
        f.write('{"l": -1}')
    r = run([py, "main.py", "--input", bad], check=False)
    if r.returncode == 0:
        print("ERROR: bad input should exit non-zero", file=sys.stderr)
        return 1

    print("Feature smoke tests: all passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
