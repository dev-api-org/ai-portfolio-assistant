from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
try:
    from . import session_memory as memory  # type: ignore
    from . import config  # type: ignore
except ImportError:  # when executed without package context
    import session_memory as memory  # type: ignore
    import config  # type: ignore
import json
from pathlib import Path
from typing import Any, Dict


def _to_lc_message(item: dict):
    role = item.get("role")
    content = item.get("content", "")
    if role == "human":
        return HumanMessage(content=content)
    if role == "ai":
        return AIMessage(content=content)
    if role == "system":
        return SystemMessage(content=content)
    return HumanMessage(content=content)


def _has_system_content(history: list[dict], content: str) -> bool:
    return any(m.get("role") == "system" and m.get("content", "") == content for m in history)


def chat_with_history(session_id: str, user_input: str, history_limit: int = 20, system_prompt: str | None = None) -> str:
    history = memory.get_history(session_id)

    # 1) Ensure global system prompt is present once per session
    global_sp = getattr(config, "GLOBAL_SYSTEM_PROMPT", "").strip()
    if global_sp and not _has_system_content(history, global_sp):
        memory.append_message(session_id, "system", global_sp)
        history = memory.get_history(session_id)

    # 2) Ensure template-specific system prompt is present (even if global exists)
    if system_prompt:
        sp = system_prompt.strip()
        if sp and not _has_system_content(history, sp):
            memory.append_message(session_id, "system", sp)
            history = memory.get_history(session_id)

    recent = history[-history_limit:] if history_limit else history
    messages = [_to_lc_message(m) for m in recent]
    messages.append(HumanMessage(content=user_input))

    llm = ChatGoogleGenerativeAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
    resp = llm.invoke(messages)

    memory.append_message(session_id, "human", user_input)
    memory.append_message(session_id, "ai", resp.content)

    return resp.content

_PROMPTS_CACHE: Dict[str, Any] | None = None

def _load_prompts() -> Dict[str, Any]:
    global _PROMPTS_CACHE
    if _PROMPTS_CACHE is None:
        path = Path(__file__).resolve().parent.parent / "prompts" / "prompts.json"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        _PROMPTS_CACHE = data.get("prompts", {})
    return _PROMPTS_CACHE

def _normalize_params(params: Dict[str, Any]) -> Dict[str, str]:
    norm: Dict[str, str] = {}
    for k, v in params.items():
        if isinstance(v, list):
            norm[k] = ", ".join(map(str, v))
        else:
            norm[k] = str(v)
    return norm

def render_template(template_key: str, params: Dict[str, Any]) -> tuple[str, str]:
    prompts = _load_prompts()
    if template_key not in prompts:
        raise KeyError(f"Unknown template '{template_key}'")
    t = prompts[template_key]
    required = list(t.get("parameters", {}).keys())
    missing = [p for p in required if p not in params]
    if missing:
        raise ValueError(f"Missing parameters for '{template_key}': {', '.join(missing)}")
    norm = _normalize_params(params)
    system_prompt = t["system_prompt"].format(**norm)
    user_prompt = t["user_prompt_template"].format(**norm)
    return system_prompt, user_prompt

def generate_from_template(session_id: str, template_key: str, params: Dict[str, Any], history_limit: int = 20) -> str:
    system_prompt, user_prompt = render_template(template_key, params)
    return chat_with_history(
        session_id=session_id,
        user_input=user_prompt,
        history_limit=history_limit,
        system_prompt=system_prompt,
    )
