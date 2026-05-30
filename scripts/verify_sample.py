#!/usr/bin/env python3
"""
CI verification script — asserts sample input matches Naidu brief / spreadsheet.
Exits 0 on success, 1 on any assertion failure.
"""

import json
import subprocess
import sys

# Authoritative values from NC-DE-ESD_Test_ElastomericBearingDesign.xlsx (sample row)
EXPECTED = {
    "overall": "BEARING FAILS",
    "check1": {"status": "FAIL", "Eq": 0.801621277084429},
    "check2": {"status": "FAIL", "Et": 5.426411654240332},
    "check5": {"status": "FAIL", "delta_total": 1.5888364140976308},
    "checks_ok": (
        "check3_plate_thickness",
        "check4_stability",
        "check6_rotational_limit",
        "check7_fixing_of_bearings",
    ),
}


def _run_cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "main.py", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def _load_sample_json() -> dict:
    proc = _run_cli(["--sample", "--json"])
    if proc.returncode != 0:
        print("ERROR: main.py --sample --json failed", file=sys.stderr)
        print(proc.stderr or proc.stdout, file=sys.stderr)
        sys.exit(1)
    return json.loads(proc.stdout)


def main() -> int:
    # Optional human-readable output (must exit 0 — calculation success, not pass/fail)
    verbose = _run_cli(["--sample", "--verbose"])
    if verbose.returncode != 0:
        print(
            "ERROR: main.py --sample --verbose exited",
            verbose.returncode,
            file=sys.stderr,
        )
        print(verbose.stderr or verbose.stdout, file=sys.stderr)
        return 1
    print(verbose.stdout)

    d = _load_sample_json()

    assert d["overall"] == EXPECTED["overall"], f"overall={d['overall']!r}"

    c1 = d["check1_shear_strain"]
    assert c1["status"] == EXPECTED["check1"]["status"]
    assert abs(c1["Eq"] - EXPECTED["check1"]["Eq"]) < 0.001, (
        f"Eq={c1['Eq']} expected ~{EXPECTED['check1']['Eq']}"
    )

    c2 = d["check2_max_design_strain"]
    assert c2["status"] == EXPECTED["check2"]["status"]
    assert abs(c2["Et"] - EXPECTED["check2"]["Et"]) < 0.01, (
        f"Et={c2['Et']} expected ~{EXPECTED['check2']['Et']}"
    )

    for key in EXPECTED["checks_ok"]:
        assert d[key]["status"] == "OK", f"{key}={d[key]['status']}"

    c5 = d["check5_vertical_deflection"]
    assert c5["status"] == EXPECTED["check5"]["status"]
    assert abs(c5["delta_total"] - EXPECTED["check5"]["delta_total"]) < 0.01, (
        f"delta_total={c5['delta_total']} expected ~{EXPECTED['check5']['delta_total']}"
    )

    print("Verification sample: all assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
