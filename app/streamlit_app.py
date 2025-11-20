import sys
import pathlib

# Ensure project root on sys.path so existing frontend/backend imports work
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import the current Streamlit UI. Executing this file with Streamlit will run the app.
# Usage: streamlit run app/streamlit_app.py
import frontend.streamlit_chat_canvas  # noqa: F401
