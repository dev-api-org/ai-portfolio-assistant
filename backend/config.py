import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables from .env file (for local development)
load_dotenv()

# --- SIMPLIFIED CONFIG LOADER ---
# We rely purely on os.getenv().
# 1. On AWS: Keys are loaded from the Environment Properties you set in the console.
# 2. On Local: python-dotenv loads them from your .env file.
# We removed 'import streamlit' to prevent the "secrets.toml not found" crash.

def _get_config(key: str, default: str = "") -> str:
    return os.getenv(key, default)

# Model configuration
MODEL_NAME = _get_config("MODEL_NAME", "gemini-2.0-flash-exp")
TEMPERATURE = float(_get_config("MODEL_TEMPERATURE", "0.7"))

# Global system prompt for the assistant
DEFAULT_GLOBAL_SYSTEM_PROMPT = (
    "You are DevFolio AI. Help users analyze, improve, and generate portfolio content "
    "(bios, project descriptions, skills summaries, SEO text) with actionable, concise guidance. "
    "Always ask for missing details, keep answers structured, and tailor advice to the target role and audience."
)

def _load_global_system_prompt_from_file() -> str:
    try:
        # Align with actual file location
        path = Path(__file__).resolve().parent / "systemprompts.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Expect either {"system_prompt": "..."} or {"prompts": {"global": "..."}}
            sp = str(data.get("system_prompt") or data.get("global") or "").strip()
            if sp:
                return sp
    except Exception:
        pass
    return ""

_file_sp = _load_global_system_prompt_from_file()
GLOBAL_SYSTEM_PROMPT = (
    _file_sp
    or _get_config("GLOBAL_SYSTEM_PROMPT", DEFAULT_GLOBAL_SYSTEM_PROMPT).strip()
)
