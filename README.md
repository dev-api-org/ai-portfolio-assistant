# DevFolio AI - Portfolio Assistant

AI-powered tool for generating professional bios, project summaries, and learning reflections using Google's Gemini AI.

## 🚀 Features

- **Interactive Chat Interface**: Natural conversation with AI to build your portfolio content
- **Multiple Content Types**: Generate bios, project descriptions, skills summaries, and more
- **Context-Aware**: Maintains conversation history for coherent, personalized responses
- **Modern UI**: Clean, responsive interface built with Streamlit

## 📋 Prerequisites

- Python 3.10 or higher
- Google AI API Key ([Get one here](https://aistudio.google.com/app/apikey))
- Git (optional)

## 🛠️ Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/dev-api-org/ai-portfolio-assistant.git
cd ai-portfolio-assistant
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
# Upgrade pip (recommended)
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Google API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 5. Run the Application

```bash
streamlit run frontend/streamlit_chat_canvas.py
```

The app will open in your browser at `http://localhost:8501`

## ☁️ Streamlit Cloud Deployment

### Step 1: Prepare Your Repository

Ensure these files are in your repository:
- ✅ `requirements.txt` (unified dependencies)
- ✅ `backend/__init__.py` (makes backend a Python package)
- ✅ `.streamlit/config.toml` (Streamlit configuration)
- ✅ `.env.example` (template for local development)
- ✅ `.streamlit/secrets.toml.example` (template for cloud secrets)

### Step 2: Deploy to Streamlit Cloud

1. **Sign in** to [Streamlit Cloud](https://share.streamlit.io/)
2. **Click "New app"**
3. **Configure your app:**
   - Repository: `dev-api-org/ai-portfolio-assistant`
   - Branch: `main`
   - Main file path: `frontend/streamlit_chat_canvas.py`
4. **Click "Advanced settings"**
5. **Set Python version:** `3.10` or higher

### Step 3: Configure Secrets

In Streamlit Cloud, go to **App Settings > Secrets** and add:

```toml
GOOGLE_API_KEY = "your_google_api_key_here"
MODEL_NAME = "gemini-2.0-flash-exp"
MODEL_TEMPERATURE = "0.7"
```

### Step 4: Deploy

Click **"Deploy"** and wait for the build to complete.

## 🔒 Security Best Practices

### ⚠️ NEVER commit sensitive data:
- ❌ `.env` file with real API keys
- ❌ `.streamlit/secrets.toml` with real secrets
- ✅ Use `.env.example` and `.streamlit/secrets.toml.example` as templates

### Environment Variables

The app uses the following environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | ✅ Yes | - | Your Google AI API key |
| `MODEL_NAME` | No | `gemini-2.0-flash-exp` | Gemini model to use |
| `MODEL_TEMPERATURE` | No | `0.7` | Model creativity (0.0-1.0) |
| `GLOBAL_SYSTEM_PROMPT` | No | From config | Custom system prompt |

## 📁 Project Structure

```
ai-portfolio-assistant/
├── backend/
│   ├── __init__.py          # Makes backend a package
│   ├── chat_core.py         # Core chat logic
│   ├── config.py            # Configuration management
│   ├── session_memory.py    # Session state management
│   ├── prompts.json         # Prompt templates
│   └── systemprompts.json   # System prompts
├── frontend/
│   ├── components/          # Reusable UI components
│   ├── img/                 # Images and assets
│   ├── pages/               # Additional pages
│   ├── streamlit_chat_canvas.py  # Main app
│   └── utils.py             # Utility functions
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml.example # Secrets template
├── requirements.txt         # Python dependencies
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## 🧪 Testing

To test the backend independently:

```bash
python backend/llm_service.py
```

This runs a terminal-based chat to verify your API connection.

## 🐛 Troubleshooting

### ModuleNotFoundError: No module named 'backend'

**Solution:** Ensure `backend/__init__.py` exists (should be an empty file).

### API Key Errors

**Solution:** 
1. Verify your API key at [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Check that `GOOGLE_API_KEY` is set in `.env` (local) or Streamlit secrets (cloud)
3. Ensure no extra spaces or quotes in the key

### Streamlit Cloud Build Fails

**Solution:**
1. Check that `requirements.txt` is in the repository root
2. Verify all imports use proper package structure (`from backend import ...`)
3. Review build logs in Streamlit Cloud dashboard

## 📝 Notes

- The app maintains conversation history per session
- Session data is stored in memory (resets on restart)
- For production, consider adding persistent storage
- Rate limits apply based on your Google AI API tier

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

This project is for educational and portfolio purposes.
