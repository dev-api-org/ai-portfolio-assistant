from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatGoogleGenerativeAI
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
# Removed PDF imports and PDFManager. Rely solely on chat history.

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

    # 3) Use only chat history context; PDF context removed
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
        # Load prompts from backend/prompts.json to align with frontend usage
        path = Path(__file__).resolve().parent / "prompts.json"
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

# Deprecated: removed reliance on static templates. Use generic content generation.
def render_template(template_key: str, params: Dict[str, Any]) -> tuple[str, str]:
    raise KeyError("Static templates have been removed. Use generate_generic_content() instead.")

# Generic content generator that builds prompts dynamically from extracted info

def generate_generic_content(
    session_id: str,
    content_type: str,
    extracted_info: Dict[str, Any] | None = None,
    extra_input: str | None = None,
    history_limit: int = 20,
) -> str:
    extracted_info = extracted_info or {}

    # Build a dynamic system prompt
    sys_lines = [
        f"You are a professional content writer that creates comprehensive {content_type.lower()} in README markdown format.",
        "Use clear headings, bullet points, and professional tone.",
        "Only include sections with meaningful content inferred from chat history and provided data.",
    ]
    system_prompt = "\n".join(sys_lines)

    # Summarize available info succinctly for the model
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

    # User prompt with guidance and any extra user input
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

    # Invoke with chat history
    return chat_with_history(
        session_id=session_id,
        user_input=user_prompt,
        history_limit=history_limit,
        system_prompt=system_prompt,
    )


def _infer_target_section(user_input, mode):
    """Infer which section the user wants to update based on their input"""
    input_lower = user_input.lower()
    
    # Common section keywords for different modes
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
    
    # Get the section mapping for current mode
    mode_sections = section_keywords.get(mode, {})
    
    # Check which section has the most keyword matches
    best_section = None
    best_score = 0
    
    for section, keywords in mode_sections.items():
        score = sum(1 for keyword in keywords if keyword in input_lower)
        if score > best_score:
            best_score = score
            best_section = section
    
    # If no clear match, use some fallback logic
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
        else:  # Learning Reflections
            if any(word in input_lower for word in ["skill", "learned", "knowledge"]):
                best_section = "Skills Learned"
            else:
                best_section = "Learning Objectives"
    
    # Convert to proper title case
    if best_section:
        if best_section == "about":
            return "About Me"
        elif best_section == "skills":
            return "Skills & Technologies"
        elif best_section == "experience":
            return "Experience"
        elif best_section == "education":
            return "Education"
        elif best_section == "contact":
            return "Contact Information"
        elif best_section == "overview":
            return "Overview"
        elif best_section == "technologies":
            return "Technologies Used"
        elif best_section == "features":
            return "Key Features"
        elif best_section == "challenges":
            return "Challenges & Solutions"
        elif best_section == "results":
            return "Results & Impact"
        elif best_section == "objectives":
            return "Learning Objectives"
        elif best_section == "application":
            return "Practical Applications"
        elif best_section == "future":
            return "Future Learning Goals"
    
    return best_section

def _extract_section_block(content, target_section):
    """Extract a specific section block from generated content"""
    if not content or not target_section:
        return ""
    
    lines = content.split('\n')
    section_lines = []
    in_target_section = False
    current_level = 0
    
    for line in lines:
        # Check if this is a heading
        if line.startswith('#'):
            # Count heading level
            heading_level = len(line) - len(line.lstrip('#'))
            heading_text = line.lstrip('#').strip()
            
            # If we're in a section and encounter same or higher level heading, we're done
            if in_target_section and heading_level <= current_level:
                break
            
            # Check if this is our target section
            if (heading_text.lower() == target_section.lower() or 
                target_section.lower() in heading_text.lower() or
                heading_text.lower() in target_section.lower()):
                in_target_section = True
                current_level = heading_level
                section_lines.append(line)
                continue
        
        # If we're in the target section, collect the line
        if in_target_section:
            # Skip empty lines at the beginning of the section
            if not line.strip() and not section_lines:
                continue
            section_lines.append(line)
    
    # Clean up the extracted section
    if section_lines:
        # Remove trailing empty lines
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()
        
        # Ensure we have proper section structure
        result = '\n'.join(section_lines).strip()
        
        # If the result is too minimal, enhance it
        if len(result.split('\n')) <= 2:
            return _enhance_minimal_section(result, target_section)
        
        return result
    
    return ""

def _enhance_minimal_section(section_content, target_section):
    """Enhance a minimal section with appropriate content"""
    if not section_content.strip():
        # Create basic section structure
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
