#!/usr/bin/env python3
"""
CI verification script — asserts sample input matches Naidu brief / spreadsheet.
Exits 0 on success, 1 on any assertion failure.
"""

import json
import subprocess
import sys


def _load_sample_json():
    out = subprocess.check_output(
        [sys.executable, "main.py", "--sample", "--json"],
        text=True,
    )
    return json.loads(out)


def main() -> int:
    d = _load_sample_json()

    assert d["overall"] == "BEARING FAILS", f"overall={d['overall']!r}"

    c1 = d["check1_shear_strain"]
    assert c1["status"] == "FAIL", f"check1 status={c1['status']}"
    assert abs(c1["Eq"] - 0.80) < 0.02, f"Eq={c1['Eq']}"

    c2 = d["check2_max_design_strain"]
    assert c2["status"] == "FAIL"
    assert abs(c2["Et"] - 5.43) < 0.05, f"Et={c2['Et']}"

    for key in (
        "check3_plate_thickness",
        "check4_stability",
        "check6_rotational_limit",
        "check7_fixing_of_bearings",
    ):
        assert d[key]["status"] == "OK", f"{key}={d[key]['status']}"

    c5 = d["check5_vertical_deflection"]
    assert c5["status"] == "FAIL"
    assert abs(c5["delta_total"] - 1.59) < 0.02, f"delta_total={c5['delta_total']}"

    print("Verification sample: all assertions passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
