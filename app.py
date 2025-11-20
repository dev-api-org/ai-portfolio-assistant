import sys
import pathlib
import os

# Ensure project root on sys.path so existing frontend/backend imports work
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load environment variables from .env if available (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not available, that's OK

# Import the current Streamlit UI. Executing this file with Streamlit will run the app.
# Usage: streamlit run app.py
import frontend.streamlit_chat_canvas  # noqa: F401
