from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# REMOVED: import session_memory (This was causing the crash)
from . import config  # type: ignore
import json
from pathlib import Path
from typing import Any, Dict, List

# --- NEW: AWS-Safe In-Memory Storage ---
# This replaces the file-based session_memory to prevent Read-Only errors
_RAM_MEMORY: Dict[str, List[Dict[str, str]]] = {}

def get_ram_history(session_id: str) -> List[Dict[str, str]]:
    """Retrieve history from RAM"""
    return _RAM_MEMORY.get(session_id, [])

def append_ram_message(session_id: str, role: str, content: str):
    """Save message to RAM"""
    if session_id not in _RAM_MEMORY:
        _RAM_MEMORY[session_id] = []
    _RAM_MEMORY[session_id].append({"role": role, "content": content})
# ----------------------------------------

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

def chat_with_history(
    session_id: str, 
    user_input: str, 
    history_limit: int = 20, 
    system_prompt: str | None = None,
) -> str:
    # UPDATED: Use RAM memory instead of file memory
    history = get_ram_history(session_id)

    # 1) Ensure global system prompt is present once per session
    global_sp = getattr(config, "GLOBAL_SYSTEM_PROMPT", "").strip()
    if global_sp and not _has_system_content(history, global_sp):
        append_ram_message(session_id, "system", global_sp)
        history = get_ram_history(session_id)

    # 2) Ensure template-specific system prompt is present
    if system_prompt:
        sp = system_prompt.strip()
        if sp and not _has_system_content(history, sp):
            append_ram_message(session_id, "system", sp)
            history = get_ram_history(session_id)

    # 3) Use chat history context
    recent = history[-history_limit:] if history_limit else history
    messages = [_to_lc_message(m) for m in recent]
    messages.append(HumanMessage(content=user_input))

    # --- DEBUG BLOCK START ---
    try:
        llm = ChatGoogleGenerativeAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
        resp = llm.invoke(messages)
        
        # Save success to RAM
        append_ram_message(session_id, "human", user_input)
        append_ram_message(session_id, "ai", resp.content)
        return resp.content

    except Exception as e:
        # If it fails, catch the error and return it as a chat message
        error_message = f"⚠️ **CRASH DETECTED:**\n\n{str(e)}"
        
        # Append error to history so it doesn't look like a total failure
        append_ram_message(session_id, "human", user_input)
        append_ram_message(session_id, "ai", error_message)
        return error_message
    # --- DEBUG BLOCK END ---

_PROMPTS_CACHE: Dict[str, Any] | None = None

def _load_prompts() -> Dict[str, Any]:
    global _PROMPTS_CACHE
    if _PROMPTS_CACHE is None:
        # Load prompts from backend/prompts.json
        # usage of open(..., 'r') is SAFE on AWS (Read-only is fine)
        path = Path(__file__).resolve().parent / "prompts.json"
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            _PROMPTS_CACHE = data.get("prompts", {})
        except FileNotFoundError:
            _PROMPTS_CACHE = {}
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
    raise KeyError("Static templates have been removed. Use generate_generic_content() instead.")

def generate_generic_content(
    session_id: str,
    content_type: str,
    extracted_info: Dict[str, Any] | None = None,
    extra_input: str | None = None,
    history_limit: int = 20,
) -> str:
    extracted_info = extracted_info or {}

    sys_lines = [
        f"You are a professional content writer that creates comprehensive {content_type.lower()} in README markdown format.",
        "Use clear headings, bullet points, and professional tone.",
        "Only include sections with meaningful content inferred from chat history and provided data.",
    ]
    system_prompt = "\n".join(sys_lines)

    info_parts: list[str] = []
    name = extracted_info.get("name")
    title = extracted_info.get("title")
    if name or title:
        info_parts.append(f"Name/Title: {name or ''} {('- ' + title) if title else ''}".strip())
    if extracted_info.get("contact"):
        info_parts.append("Contact info present")
    techs = extracted_info.get("technologies") or []
    if techs:
        info_parts.append("Technologies: " + ", ".join(map(str, techs[:20])))
    exp_years = (extracted_info.get("experience") or {}).get("years")
    if exp_years:
        info_parts.append(f"Experience: {exp_years} years")
    if extracted_info.get("education"):
        info_parts.append("Education data present")
    if extracted_info.get("projects"):
        info_parts.append("Projects data present")
    if extracted_info.get("achievements"):
        info_parts.append("Achievements data present")
    if extracted_info.get("certifications"):
        info_parts.append("Certifications data present")

    info_summary = ("- " + "\n- ".join(info_parts)) if info_parts else "- General professional information from chat"

    guidance = (
        f"Create a polished {content_type.lower()} using README markdown with relevant sections "
        f"(header, contact, summary, skills, experience, education, projects, achievements, certifications as applicable).\n"
        f"Incorporate the conversation context and the available data succinctly."
    )
    recent_note = f"\n\nAdditional input: {extra_input}" if extra_input else ""

    user_prompt = (
        f"Available data summary:\n{info_summary}\n\n"
        f"{guidance}{recent_note}"
    )

    return chat_with_history(
        session_id=session_id,
        user_input=user_prompt,
        history_limit=history_limit,
        system_prompt=system_prompt,
    )

# Helper functions below are pure logic (no file I/O), so they are safe.
def _infer_target_section(user_input, mode):
    input_lower = user_input.lower()
    section_keywords = {
        "Personal Bio": {
            "about": ["about", "introduction", "intro", "overview", "summary", "bio"],
            "skills": ["skill", "technology", "tech", "programming", "coding", "framework", "language"],
            "experience": ["experience", "work", "career", "background", "history", "professional"],
            "education": ["education", "degree", "school", "university", "college"],
            "contact": ["contact", "email", "phone", "linkedin", "github", "portfolio"]
        },
        "Project Summaries": {
            "overview": ["overview", "description", "summary", "about", "what is"],
            "technologies": ["technology", "tech", "stack", "tools", "framework", "language"],
            "features": ["feature", "functionality", "what it does", "capabilities"],
            "challenges": ["challenge", "problem", "difficulty", "issue", "solution"],
            "results": ["result", "impact", "outcome", "achievement", "success"]
        },
        "Learning Reflections": {
            "objectives": ["objective", "goal", "purpose", "aim", "why"],
            "skills": ["skill", "learned", "acquired", "knowledge", "understanding"],
            "application": ["apply", "use", "practice", "implement", "real world"],
            "challenges": ["challenge", "difficulty", "struggle", "problem"],
            "future": ["future", "next", "continue", "improve", "develop"]
        }
    }
    
    mode_sections = section_keywords.get(mode, {})
    best_section = None
    best_score = 0
    
    for section, keywords in mode_sections.items():
        score = sum(1 for keyword in keywords if keyword in input_lower)
        if score > best_score:
            best_score = score
            best_section = section
    
    if not best_section:
        if mode == "Personal Bio":
            if any(word in input_lower for word in ["skill", "tech", "programming"]):
                best_section = "Skills"
            elif any(word in input_lower for word in ["work", "job", "experience"]):
                best_section = "Experience"
            else:
                best_section = "About Me"
        elif mode == "Project Summaries":
            if any(word in input_lower for word in ["tech", "stack", "tool"]):
                best_section = "Technologies Used"
            else:
                best_section = "Overview"
        else: 
            if any(word in input_lower for word in ["skill", "learned", "knowledge"]):
                best_section = "Skills Learned"
            else:
                best_section = "Learning Objectives"
    
    if best_section:
        if best_section == "about": return "About Me"
        elif best_section == "skills": return "Skills & Technologies"
        elif best_section == "experience": return "Experience"
        elif best_section == "education": return "Education"
        elif best_section == "contact": return "Contact Information"
        elif best_section == "overview": return "Overview"
        elif best_section == "technologies": return "Technologies Used"
        elif best_section == "features": return "Key Features"
        elif best_section == "challenges": return "Challenges & Solutions"
        elif best_section == "results": return "Results & Impact"
        elif best_section == "objectives": return "Learning Objectives"
        elif best_section == "application": return "Practical Applications"
        elif best_section == "future": return "Future Learning Goals"
    
    return best_section

def _extract_section_block(content, target_section):
    if not content or not target_section:
        return ""
    lines = content.split('\n')
    section_lines = []
    in_target_section = False
    current_level = 0
    for line in lines:
        if line.startswith('#'):
            heading_level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('#').strip()
            if in_target_section and heading_level <= current_level:
                break
            if (heading_text.lower() == target_section.lower() or 
                target_section.lower() in heading_text.lower() or
                heading_text.lower() in target_section.lower()):
                in_target_section = True
                current_level = heading_level
                section_lines.append(line)
                continue
        if in_target_section:
            if not line.strip() and not section_lines:
                continue
            section_lines.append(line)
    
    if section_lines:
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()
        result = '\n'.join(section_lines).strip()
        if len(result.split('\n')) <= 2:
            return _enhance_minimal_section(result, target_section)
        return result
    return ""

def _enhance_minimal_section(section_content, target_section):
    if not section_content.strip():
        if target_section.lower() in ["skills", "skills & technologies"]:
            return f"## {target_section}\n\n- Technical skills based on conversation\n- Relevant technologies and tools\n- Professional competencies"
        elif target_section.lower() in ["about me", "overview"]:
            return f"## {target_section}\n\nProfessional background and key strengths based on our discussion."
        elif target_section.lower() in ["technologies used", "tech stack"]:
            return f"## {target_section}\n\n- Primary technologies mentioned\n- Development tools and frameworks\n- Technical environment"
        elif target_section.lower() in ["experience", "work experience"]:
            return f"## {target_section}\n\nCareer history and professional achievements discussed."
        else:
            return f"## {target_section}\n\nContent related to {target_section.lower()} based on our conversation."
    return section_content
