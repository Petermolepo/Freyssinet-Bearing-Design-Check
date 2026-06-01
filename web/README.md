# web/ — Browser UI and REST API

| Path | What it does |
|------|----------------|
| `app.py` | FastAPI server — runs checks, serves UI, PDF/CSV download |
| `static/index.html` | Main form page |
| `static/js/app.js` | Form logic, calls `/api/check`, shows results |
| `static/css/styles.css` | Naidu green branding and layout |

**Start:** `python main.py --web` then open http://localhost:8000  
**Presentation deck:** http://localhost:8000/presentation
