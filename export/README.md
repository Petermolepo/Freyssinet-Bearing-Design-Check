# export/ — Reports for clients and records

Turns calculation results into downloadable files.

| File | What it does |
|------|----------------|
| `pdf_export.py` | Branded PDF (Naidu letterhead, summary + detail tables) |
| `csv_export.py` | Sectioned CSV for Excel (inputs, geometry, all checks) |

Used by CLI (`--export-pdf`, `--export-csv`) and web API (`/api/check/pdf`, `/api/check/csv`).
