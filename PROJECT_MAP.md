# Project map (for presentations)

Quick guide to every part of the codebase.

## Root files (start here)

| File | Role |
|------|------|
| `main.py` | CLI entry — sample, JSON, batch, compare, web |
| `models.py` | `BearingInput` — all 15 engineer inputs |
| `validators.py` | Checks inputs before any maths |
| `engine.py` | Runs geometry + checks 1–7 → `BearingResult` |
| `outputs.py` | Prints table / JSON / formula sheet |
| `batch.py` | Many bearings from one CSV |
| `compare.py` | Two JSON designs side by side |

## Folders

| Folder | Purpose | README |
|--------|---------|--------|
| `checks/` | All 7 design checks + geometry | `checks/README.md` |
| `bearing_types/` | pad / laminated / pot constants | `bearing_types/README.md` |
| `export/` | PDF and CSV reports | `export/README.md` |
| `web/` | Browser UI + FastAPI API | `web/README.md` |
| `tests/` | Automated verification | `tests/README.md` |
| `scripts/` | CI helpers | `scripts/README.md` |
| `batch_samples/` | Example CSV | `batch_samples/README.md` |
| `presentation/` | Demo slide deck HTML | `presentation/README.md` |

## Data flow (say this in your demo)

```
User input → validate() → BearingInput → run_checks() → BearingResult → outputs / PDF / web
```

## Verification sample (proof it works)

```bash
python main.py --sample
```

Expected: **BEARING FAILS** — Check 1, 2, 5 fail; 3, 4, 6, 7 pass.
