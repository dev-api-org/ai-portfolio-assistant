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

# Check for required environment variables
if not os.getenv("GOOGLE_API_KEY"):
    import streamlit as st
    st.error("❌ GOOGLE_API_KEY environment variable is not set!")
    st.info("Please set the GOOGLE_API_KEY in your environment variables.")
    st.stop()

# Import the current Streamlit UI. Executing this file with Streamlit will run the app.
# Usage: streamlit run app.py
try:
    import frontend.streamlit_chat_canvas  # noqa: F401
except Exception as e:
    import streamlit as st
    st.error(f"❌ Failed to load application: {e}")
    st.stop()
