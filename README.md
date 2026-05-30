# Freyssinet Elastomeric Bearing Design Check Tool
### Naidu Consulting — Digital Engineering Technical Assessment

> **Candidate:** Peter Molepo | **Role:** Engineering Software Developer

---

## What it does

Converts the Freyssinet Excel spreadsheet into a fully working Python tool.

- Accepts all **17 bearing input parameters**
- Runs all **7 Freyssinet design checks** — formulas taken directly from the spreadsheet
- Shows every **intermediate value** so an engineer can verify the math
- Gives a clear **PASS / FAIL** per check and an overall **BEARING PASSES / BEARING FAILS**
- **Never crashes** on bad input — tells the user exactly what is wrong
- Reproduces the brief's **verification example exactly**
- Ships with a **web UI**, **PDF/CSV export**, **batch mode**, and **--compare mode**

---

## Quick start (3 commands)

```bash
git clone https://github.com/Petermolepo/frey-bridge-bearing-tool.git
cd frey-bridge-bearing-tool
pip install -r requirements.txt
```

---

## All commands — copy-paste reference

### Run the verification sample (most important)
```bash
python main.py --sample
```

### See ALL intermediate values for every check
```bash
python main.py --sample --verbose
```

### Output as JSON (for programmatic use)
```bash
python main.py --sample --json
```

### Run from your own JSON input file
```bash
python main.py --input sample_input.json
```

### Interactive mode — enter values one by one
```bash
python main.py --interactive
```

### Save a PDF report
```bash
python main.py --sample --export-pdf bearing_report.pdf
```

### Save a CSV report
```bash
python main.py --sample --export-csv bearing_report.csv
```

### Run multiple bearings from a CSV file (batch mode)
```bash
python main.py --batch batch_samples/sample_batch.csv
```

### Batch + export all results to CSV
```bash
python main.py --batch batch_samples/sample_batch.csv --export-csv all_results.csv
```

### Compare two bearing designs side by side
```bash
python main.py --compare sample_input.json bearing_b.json
```

### List all supported bearing types
```bash
python main.py --types
```

### Use a different bearing type
```bash
python main.py --input sample_input.json --type laminated
```

### Print the full formula reference sheet
```bash
python main.py --explain
```

### Start the web UI (opens at http://localhost:8000)
```bash
pip install -r requirements.txt
python main.py --web
```

**Windows (recommended):**
```powershell
.\scripts\setup.ps1      # once — creates .venv and installs deps
.\scripts\run-web.ps1      # starts backend + web UI
```

If port 8000 is busy: `python main.py --web --port 8001`

### Presentation deck (interview prep)
With the web UI running, open:

**http://localhost:8000/presentation**

Use **← →** arrow keys to navigate 12 slides. Slide 3 highlights *“explain your code”*; Slide 4 shows the core pipeline architecture.

### Run all tests (50 tests)
```bash
pytest tests/ -v
```

### Keyboard shortcut in the web UI
```
Ctrl + Enter (or Cmd + Enter on Mac)  →  Run All Checks
```

---

## Verification — expected results

| Check | Expected | Tool output |
|-------|----------|-------------|
| 1 – Shear Strain       | **FAIL**  Eq = 0.80     | FAIL  Eq = 0.8016  ✓ |
| 2 – Max Design Strain  | **FAIL**  Et = 5.43     | FAIL  Et = 5.4264  ✓ |
| 3 – Plate Thickness    | OK                      | OK                 ✓ |
| 4 – Stability          | OK                      | OK                 ✓ |
| 5 – Vertical Deflection| **FAIL**  ▲Total = 1.59 | FAIL  ▲ = 1.5888   ✓ |
| 6 – Rotational Limit   | OK                      | OK                 ✓ |
| 7 – Fixing of Bearings | OK                      | OK                 ✓ |
| **Overall**            | **BEARING FAILS**       | **BEARING FAILS**  ✓ |

---

## Project structure

```
frey-bridge-bearing-tool/
│
├── main.py                   ← CLI entry point — all flags live here
├── engine.py                 ← Runs all 7 checks, returns BearingResult
├── models.py                 ← BearingInput dataclass (17 parameters)
├── validators.py             ← Input validation (type, range, logic)
├── outputs.py                ← Table / verbose / JSON formatters
├── compare.py                ← Side-by-side bearing comparison
├── batch.py                  ← Batch CSV runner
│
├── checks/                   ← One file per check — pure functions
│   ├── geometry.py           ← Derived geometry (le, be, S, δr, …)
│   ├── check1_shear_strain.py
│   ├── check2_max_design_strain.py
│   ├── check3_plate_thickness.py
│   ├── check4_stability.py
│   ├── check5_vertical_deflection.py
│   ├── check6_rotational_limit.py
│   └── check7_fixing.py
│
├── bearing_types/
│   └── registry.py           ← PAD / LAMINATED / POT bearing type registry
│
├── export/
│   ├── pdf_export.py         ← Full PDF report (reportlab)
│   └── csv_export.py         ← Single + batch CSV export
│
├── web/
│   ├── app.py                ← FastAPI backend (REST API)
│   └── static/
│       ├── index.html        ← Web UI shell
│       ├── css/styles.css    ← Naidu brand styling
│       └── js/app.js         ← Form, API, results rendering
├── scripts/
│   ├── setup.ps1             ← Create .venv + install deps (Windows)
│   └── run-web.ps1           ← Start web UI
│
├── tests/
│   └── test_checks.py        ← 50 pytest tests
│
├── batch_samples/
│   └── sample_batch.csv      ← Sample batch input file
│
├── sample_input.json          ← Official verification input
├── requirements.txt
└── .github/workflows/ci.yml  ← 4-stage CI pipeline
```

---

## Input format (JSON)

All 17 fields required. See `sample_input.json` for a complete example.

| Field         | Description                           | Unit    |
|---------------|---------------------------------------|---------|
| `l`           | Bearing length                        | mm      |
| `b`           | Bearing width                         | mm      |
| `T`           | Total bearing height                  | mm      |
| `plate_thk`   | Reinforcing steel plate thickness     | mm      |
| `no_plates`   | Number of steel plates                | —       |
| `te`          | Edge rubber layer thickness           | mm      |
| `ti`          | Internal rubber layer thickness       | mm      |
| `G`           | Shear modulus of rubber               | N/mm²   |
| `Vmax`        | Maximum vertical load                 | kN      |
| `Vdl`         | Dead load vertical force              | kN      |
| `Vll`         | Live load vertical force              | kN      |
| `Hs`          | Longitudinal horizontal shear force   | kN      |
| `Ht`          | Transverse horizontal shear force     | kN      |
| `long_mvmt`   | Longitudinal bearing movement         | mm      |
| `trans_mvmt`  | Transverse bearing movement           | mm      |
| `alpha_b`     | Rotation about transverse axis        | radians |
| `alpha_l`     | Rotation about longitudinal axis      | radians |

---

## Brief vs spreadsheet pass criteria

The **Naidu candidate brief** summarises pass limits (e.g. Eq ≤ 1.0, Et ≤ 7.0). The **provided Excel file** (`NC-DE-ESD_Test_ElastomericBearingDesign.xlsx`) uses stricter Freyssinet formulas (`Eq < 0.7`, `Et < 5`). This tool follows the **spreadsheet** so the verification sample matches exactly. The web UI shows both where they differ.

| Check | Brief (summary) | Spreadsheet (this tool) | Sample result |
|-------|-----------------|-------------------------|---------------|
| 1 | Eq ≤ 1.0 | Eq < 0.7 | FAIL (Eq ≈ 0.80) |
| 2 | Et ≤ 7.0 | Et < 5.0 | FAIL (Et ≈ 5.43) |
| 5 | ▲Total ≤ 0.15·ti | same | FAIL (▲ ≈ 1.59 mm) |

## Assumptions

1. **Effective dimensions**: `le = l − 10 mm`, `be = b − 10 mm` (5 mm cover strip each side). Confirmed by the verification numbers.
2. **Check 1 threshold**: Spreadsheet `Eq < 0.7` (see table above). Sample: Eq = 0.80 → FAIL ✓
3. **Check 2 threshold**: Spreadsheet `Et < 5` (see table above). Sample: Et = 5.43 → FAIL ✓
4. **Bulk modulus Eb**: Hardcoded at `2000 N/mm²` as found in the spreadsheet.
5. **Steel yield stress σs**: Hardcoded at `290 N/mm²` as found in the spreadsheet.
6. **Check 6 direction**: `delta_total > rot_limit → OK`. The deflection capacity must exceed the rotation demand.
7. **te and ti**: Treated as independent inputs. For the sample, both are 10 mm.

---

## With more time

- Calibrate LAMINATED_BEARING and POT_BEARING type thresholds against their respective design manuals
- Add a `--watch` mode that reloads when input JSON changes
- Support more bearing types (spherical, guided, free)
- Add unit conversion helper (import in kN or N, mm or m)
- Deploy web UI to a public URL with Docker

---

*Built by Peter Molepo — Naidu Consulting Technical Assessment, 2026*
