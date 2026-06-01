# bearing_types/ — Different bearing products

Lets you pick **pad**, **laminated**, or **pot** bearing via `--type` or the web UI.

| File | What it does |
|------|----------------|
| `registry.py` | Defines `BearingType` (limits, steel grade, cover strip) and the lookup table |

**Default:** `pad` — fully verified against the Freyssinet spreadsheet.  
**Others:** stubs with different constants; same 7 checks until calibrated.
