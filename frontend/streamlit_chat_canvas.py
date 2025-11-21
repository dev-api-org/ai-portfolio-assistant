import streamlit as st
from datetime import datetime
import json
import sys
import os
import pathlib
import re
from collections import OrderedDict

# --- FIXED: Page config MUST be the first Streamlit command ---
# This ensures that if imports fail later, st.error() can actually display the message.
st.set_page_config(
    page_title="DevFolio AI",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ---------------------------------------------------------------

# Constants for maintainability
MAX_ANALYSIS_MESSAGES = 20
PREVIEW_HEIGHT = 500
LOCATION_CONTEXT_WINDOW = 50
MAX_MESSAGES_HISTORY = 200

# Load Streamlit secrets into environment variables for LangChain compatibility
# This ensures GOOGLE_API_KEY is available when deployed to Streamlit Cloud
if hasattr(st, "secrets"):
    try:
        for key in st.secrets:
            if key not in os.environ:
                os.environ[key] = str(st.secrets[key])
    except (FileNotFoundError, Exception):
        # No secrets file found - this is OK for local development with .env
        pass

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Avoid duplicate path injection
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from frontend.components import file_upload
    from backend import chat_core
except ImportError as e:
    st.error(f"CRITICAL IMPORT ERROR: {e}")
    # We stop execution here so the rest of the app doesn't try to run with broken imports
    st.stop()

# Logo centered
col_logo = st.columns([3, 2, 3])
with col_logo[1]:
    try:
        logo_path = ROOT / "frontend" / "img" / "devfolio-logo.png"
        if logo_path.exists():
            st.image(str(logo_path), width=180)
        else:
            st.markdown("## 🚀 DevFolio AI")
    except Exception:
        st.markdown("## 🚀 DevFolio AI")

st.markdown("---")

# Custom CSS (keep minimal and stable selectors)
st.markdown("""
<style>
/* Light touch styling to avoid brittle selectors */
:root {
    --df-border-color: rgba(49,51,63,0.2);
}
/* Chat bubble padding */
[data-testid="stChatMessage"] {
    padding: 1rem;
    border-radius: 10px;
}
/* Text area theming */
textarea {
    background-color: transparent;
    color: inherit;
    border: 1px solid var(--df-border-color);
}
</style>
""", unsafe_allow_html=True)

# Load prompts from JSON files
def load_prompts():
    """Load prompts from JSON files with graceful fallback"""
    try:
        prompts_path = ROOT / "backend" / "prompts.json"
        system_prompts_path = ROOT / "backend" / "systemprompts.json"

        prompts = {}
        system_prompts = {}

        if prompts_path.exists():
            with open(prompts_path, 'r') as f:
                prompts = json.load(f)
        if system_prompts_path.exists():
            with open(system_prompts_path, 'r') as f:
                system_prompts = json.load(f)

        return prompts, system_prompts
    except Exception as e:
        st.error(f"Error loading prompts: {e}")
        return {}, {}

def extract_user_info_from_chat(messages):
    """Extract key information from chat history with safer, heuristic parsing"""
    extracted_info = {
        "name": "",
        "title": "",
        "contact": {},
        "technologies": [],
        "experience": {},
        "education": [],
        "projects": [],
        "skills": {},
        "achievements": [],
        "certifications": []
    }

    # Analyze recent messages for information
    recent_messages = messages[-MAX_ANALYSIS_MESSAGES:]

    full_text = " ".join([msg.get("content", "") for msg in recent_messages if msg.get("role") == "user"]) or ""
    full_text_lower = full_text.lower()

    # Extract name (prefer anchored phrases)
    name = ""
    anchored_patterns = [
        r"\bmy name is\s+([A-Z][a-zA-Z\-']+\s+[A-Z][a-zA-Z\-']+)\b",
        r"\bi am\s+([A-Z][a-zA-Z\-']+\s+[A-Z][a-zA-Z\-']+)\b",
        r"\bi'm\s+([A-Z][a-zA-Z\-']+\s+[A-Z][a-zA-Z\-']+)\b",
    ]
    for pat in anchored_patterns:
        m = re.search(pat, full_text)
        if m:
            candidate = m.group(1).strip()
            name = candidate
            break
    if not name:
        # Fallback:
