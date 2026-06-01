# checks/ — Design checks (the core maths)

This folder holds **all 7 Freyssinet design checks** plus shared geometry.

| File | What it does |
|------|----------------|
| `geometry.py` | Works out le, be, tq, δr, shape factor S, etc. from raw inputs |
| `check1_shear_strain.py` | Check 1 — shear strain Eq must be below limit |
| `check2_max_design_strain.py` | Check 2 — total strain Et from load + rotation |
| `check3_plate_thickness.py` | Check 3 — steel plates thick enough |
| `check4_stability.py` | Check 4 — bearing stable under vertical load |
| `check5_vertical_deflection.py` | Check 5 — total vertical sag within limit |
| `check6_rotational_limit.py` | Check 6 — deflection vs rotation allowance |
| `check7_fixing.py` | Check 7 — anchorage / fixing forces |

**Flow:** `engine.py` calls `compute_geometry()` first, then runs checks 1–7 in order. Check 2 needs Eq from Check 1; Check 3–7 use geometry and earlier results.
