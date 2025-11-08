import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables
load_dotenv()

# Model configuration
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.0-flash")
TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", "0.7"))

# Global system prompt for the assistant (applied once per session before any template-specific prompts)
DEFAULT_GLOBAL_SYSTEM_PROMPT = (
    "You are DevFolio AI. Help users analyze, improve, and generate portfolio content "
    "(bios, project descriptions, skills summaries, SEO text) with actionable, concise guidance. "
    "Always ask for missing details, keep answers structured, and tailor advice to the target role and audience."
)

def _load_global_system_prompt_from_file() -> str:
    try:
        # Align with actual file location and name used by the frontend
        path = Path(__file__).resolve().parent / "systemprompts.json"
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Expect either {"system_prompt": "..."} or {"prompts": {"global": "..."}}
            sp = str(data.get("system_prompt") or data.get("global") or "").strip()
            if sp:
                return sp
    except Exception:
        # Silently fall back to env/default if file is unreadable
        pass
    return ""

_file_sp = _load_global_system_prompt_from_file()
GLOBAL_SYSTEM_PROMPT = (
    _file_sp
    or os.getenv("GLOBAL_SYSTEM_PROMPT", DEFAULT_GLOBAL_SYSTEM_PROMPT).strip()
)
