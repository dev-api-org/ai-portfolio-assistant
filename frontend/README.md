# Frontend (Streamlit) — AI Portfolio Assistant

Quick scaffold for a Streamlit frontend used by the project.

How to run (Windows / PowerShell):

```powershell
# create a venv and activate it (PowerShell)
python -m venv .venv; .\.venv\Scripts\Activate.ps1
python -m pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

Files added:
- `streamlit_app.py` — main app and simple router
- `pages/upload.py` — upload page
- `utils.py` — small helpers
- `requirements.txt` — minimal dependencies

Next steps:
- Wire uploads to the backend API for indexing
- Add authentication (if needed)
- Add tests and CI checks
