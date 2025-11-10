# Quick Start Guide

Get DevFolio AI running in 5 minutes.

## 🚀 Deploy to Streamlit Cloud (Fastest)

### 1. Get API Key (2 minutes)
1. Go to https://aistudio.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

### 2. Deploy (2 minutes)
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Fill in:
   - **Repository:** `dev-api-org/ai-portfolio-assistant`
   - **Branch:** `main`
   - **Main file:** `frontend/streamlit_chat_canvas.py`

### 3. Add Secrets (1 minute)
In the deployment form, expand "Secrets" and add:
```toml
GOOGLE_API_KEY = "paste_your_api_key_here"
```

### 4. Deploy!
Click "Deploy" and wait ~3 minutes. Done! 🎉

---

## 💻 Run Locally (5 minutes)

### Prerequisites
- Python 3.10+
- Git

### Steps

```bash
# 1. Clone
git clone https://github.com/dev-api-org/ai-portfolio-assistant.git
cd ai-portfolio-assistant

# 2. Create virtual environment
python -m venv .venv

# Windows:
.\.venv\Scripts\Activate

# Mac/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Run
streamlit run frontend/streamlit_chat_canvas.py
```

App opens at http://localhost:8501

---

## 🆘 Troubleshooting

### "ModuleNotFoundError: No module named 'backend'"
**Fix:** Ensure `backend/__init__.py` exists
```bash
touch backend/__init__.py  # Mac/Linux
New-Item backend/__init__.py  # Windows
```

### "API Key Error"
**Fix:** 
1. Check your API key at https://aistudio.google.com/app/apikey
2. Verify it's in `.env` (local) or Streamlit secrets (cloud)
3. No extra spaces or quotes

### "Import Error"
**Fix:** Reinstall dependencies
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📚 More Help

- **Full Setup:** See [README.md](README.md)
- **Deployment:** See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Checklist:** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- **Changes:** See [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)

---

**Ready?** Choose cloud or local above and get started! 🚀
