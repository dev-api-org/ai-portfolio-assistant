
import streamlit as st
from datetime import datetime
import json
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontend.components import file_upload
from backend import chat_core

# Page configuration
st.set_page_config(
    page_title="DevFolio AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Logo centered
col_logo = st.columns([3, 2, 3])
with col_logo[1]:
    st.image("frontend/img/devfolio-logo.png", width=180)

st.markdown("---")

# Custom CSS
st.markdown("""
<style>
.stChatMessage {
    padding: 1rem;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Load prompts from JSON files
def load_prompts():
    """Load prompts from JSON files"""
    try:
        prompts_path = ROOT / "backend" / "prompts.json"
        system_prompts_path = ROOT / "backend" / "systemprompts.json"
        
        with open(prompts_path, 'r') as f:
            prompts = json.load(f)
        
        with open(system_prompts_path, 'r') as f:
            system_prompts = json.load(f)
        
        return prompts, system_prompts

    except Exception as e:
        st.error(f"Error loading prompts: {e}")
        return {}, {}

# Load prompts
PROMPTS, SYSTEM_PROMPTS = load_prompts()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'canvas_content' not in st.session_state:
    st.session_state.canvas_content = ""
if 'mode' not in st.session_state:
    st.session_state.mode = "Personal Bio"
if 'canvas_history' not in st.session_state:
    st.session_state.canvas_history = []
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "key_skills": "",
        "achievements": "",
        "current_role": "",
        "years_exp": "",
        "extracted_info": {}
    }

# Intent/checklist scaffolding for progressive workflow
if 'intent' not in st.session_state:
    st.session_state.intent = None
if 'next_action' not in st.session_state:
    st.session_state.next_action = None
if 'checklist' not in st.session_state:
    st.session_state.checklist = {}

# Pending canvas patch state (feat-002a)
if 'pending_canvas_patch' not in st.session_state:
    st.session_state.pending_canvas_patch = None  # Will hold: {"new_content": str, "reasoning": str, "checklist_snapshot": dict}
if 'apply_needed' not in st.session_state:
    st.session_state.apply_needed = False  # Flag to show if a patch is awaiting approval

def get_default_content(mode):
    """Get default content based on mode"""
    defaults = {
        "Personal Bio": """# Professional Profile

## About Me
Brief introduction about your professional background and passions.

## Skills
- Primary skills
- Technologies you work with
- Domain expertise

## Experience
Key career highlights and experience overview.
""",
        "Project Summaries": """# Project Name

## Overview
Brief description of the project and its purpose.

## Technologies Used
- Main technologies and tools

## Key Features
- Main functionality
- Technical challenges solved
""",
        "Learning Reflections": """# Learning Journey: [Topic]

## What I Learned
Key takeaways and new skills acquired.

## Application
How this learning applies to my work and projects.
"""
    }
    return defaults.get(mode, "")

def get_checklist_schema(mode: str):
    """Return the checklist schema for a given mode with empty slots."""
    mode_l = mode.lower()
    if "personal" in mode_l:
        return {
            "role_title": None,
            "years_experience": None,
            "top_skills": [],
            "achievements": [],
            "industries": [],
            "tone": None,
        }
    if "project" in mode_l:
        return {
            "project_name": None,
            "objective": None,
            "role_responsibilities": None,
            "tech_stack": [],
            "features_challenges": [],
            "outcomes_metrics": [],
        }
    # Learning reflections
    return {
        "topic": None,
        "motivation": None,
        "learned_points": [],
        "application_examples": [],
        "next_steps": [],
    }

# Initialize checklist schema on first load based on current mode (must run after function is defined)
if not st.session_state.checklist:
    st.session_state.checklist = get_checklist_schema(st.session_state.mode)

def get_system_prompt(mode, context):
    """Get system prompt based on mode and context"""
    prompt_key = f"{mode.lower().replace(' ', '_')}_generation"
    
    if prompt_key in SYSTEM_PROMPTS:
        base_prompt = SYSTEM_PROMPTS[prompt_key]
    else:
        base_prompt = SYSTEM_PROMPTS.get("default_generation", 
            "You are a helpful AI assistant that creates professional README-style documentation. Format all content using clean markdown with clear sections and bullet points.")
    
    # Enhance with README formatting guidance
    readme_guidance = """
    
Format all content as clean, professional README-style markdown. Use:
- Clear headings with ## and ###
- Bullet points for lists
- Bold text for emphasis where appropriate
- Code blocks for technical content if needed
- Clean, readable structure

Avoid forced templates - let the content flow naturally based on the conversation.
"""
    
    if context:
        enhanced_prompt = f"{base_prompt}{readme_guidance}\n\nUser Context: {context}"
    else:
        enhanced_prompt = f"{base_prompt}{readme_guidance}"
    
    return enhanced_prompt

def get_generation_prompt(mode, user_input, context, extracted_info):
    """Get the appropriate generation prompt based on mode"""
    prompt_key = f"{mode.lower().replace(' ', '_')}_generation"
    
    if prompt_key in PROMPTS:
        template = PROMPTS[prompt_key]
    else:
        # Natural, flexible prompts for README-style content
        template = PROMPTS.get("default_generation", 
            "Create README-style content based on: {user_input}")
    
    # Format the template with available information
    try:
        formatted_prompt = template.format(
            user_input=user_input,
            context=context,
            technologies=", ".join(extracted_info.get("technologies", [])),
            experience=extracted_info.get("experience", ""),
            role=extracted_info.get("role", ""),
            skills=", ".join(extracted_info.get("skills", []))
        )
    except KeyError:
        # If formatting fails, use a simple version
        formatted_prompt = f"Create README-style {mode} content. User input: {user_input}"
    
    return formatted_prompt

def extract_user_info_from_chat(messages):
    """Enhanced extraction: parse compound roles, focus areas, and contextual information"""
    import re
    
    extracted_info = {
        "skills": [],
        "experience": "",
        "experience_years": None,
        "role": "",
        "full_role": "",
        "seniority": "",
        "focus_areas": [],
        "achievements": [],
        "technologies": [],
        "projects": [],
        "learning_topics": [],
        "current_work": ""
    }
    
    # Combine all user messages for better context
    all_user_content = " ".join([m["content"] for m in messages if m["role"] == "user"])
    content_lower = all_user_content.lower()
    
    # Extract years of experience with multiple patterns
    exp_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'experience.*?(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s+in',
        r'worked\s+for\s+(\d+)\+?\s*years?'
    ]
    for pattern in exp_patterns:
        match = re.search(pattern, content_lower)
        if match:
            years = match.group(1)
            extracted_info["experience"] = f"{years} years"
            extracted_info["experience_years"] = int(years)
            break
    
    # Extract compound role titles (e.g., "software engineer", "data scientist")
    role_patterns = [
        r'(?:i\s+am\s+a\s+|i\'m\s+a\s+|as\s+a\s+|work\s+as\s+(?:a\s+)?)((?:senior|junior|lead|principal|staff)?\s*(?:software|data|machine\s+learning|ml|ai|frontend|backend|full[\s-]?stack|devops|cloud)?\s*(?:engineer|developer|scientist|analyst|architect|designer|programmer))',
        r'(?:position|role|job|title).*?((?:senior|junior|lead)?\s*(?:software|data|ml|ai|frontend|backend|full[\s-]?stack)?\s*(?:engineer|developer|scientist|analyst|architect))'
    ]
    for pattern in role_patterns:
        match = re.search(pattern, content_lower)
        if match:
            full_role = match.group(1).strip()
            extracted_info["full_role"] = full_role.title()
            # Extract seniority
            for level in ["senior", "junior", "lead", "principal", "staff"]:
                if level in full_role:
                    extracted_info["seniority"] = level.title()
                    break
            # Extract base role
            for role in ["engineer", "developer", "scientist", "analyst", "architect", "designer"]:
                if role in full_role:
                    extracted_info["role"] = role.title()
                    break
            break
    
    # Extract focus areas
    focus_keywords = {
        "automation": ["automation", "automate", "automated", "scripting"],
        "web development": ["web development", "web dev", "web applications", "frontend", "backend"],
        "data analysis": ["data analysis", "data analytics", "analyzing data"],
        "machine learning": ["machine learning", "ml", "deep learning", "ai"],
        "devops": ["devops", "ci/cd", "deployment", "infrastructure"],
        "cloud": ["cloud", "aws", "azure", "gcp"],
        "testing": ["testing", "qa", "quality assurance", "test automation"],
        "api development": ["api", "rest", "restful", "microservices"],
    }
    for area, keywords in focus_keywords.items():
        for keyword in keywords:
            if keyword in content_lower:
                extracted_info["focus_areas"].append(area)
                break
    
    # Extract technologies (expanded)
    tech_keywords = {
        "Python": ["python", "py", "django", "flask", "fastapi"],
        "JavaScript": ["javascript", "js", "node", "nodejs", "react", "vue", "angular"],
        "Java": ["java", "spring"],
        "SQL": ["sql", "mysql", "postgresql", "postgres"],
        "Docker": ["docker", "containers"],
        "Kubernetes": ["kubernetes", "k8s"],
        "AWS": ["aws", "amazon web services"],
        "Git": ["git", "github", "gitlab"],
        "TypeScript": ["typescript", "ts"],
    }
    for tech, keywords in tech_keywords.items():
        for keyword in keywords:
            if keyword in content_lower:
                extracted_info["technologies"].append(tech)
                break
    
    # Extract current work
    current_patterns = [
        r'(?:currently|now|working on|focused on|building)\s+([^.!?]+)',
        r'(?:i\s+)?(?:work|focus|specialize)\s+(?:on|in)\s+([^.!?]+)'
    ]
    for pattern in current_patterns:
        match = re.search(pattern, content_lower)
        if match:
            extracted_info["current_work"] = match.group(1).strip()[:100]
            break
    
    # Remove duplicates
    extracted_info["technologies"] = list(set(extracted_info["technologies"]))
    extracted_info["focus_areas"] = list(set(extracted_info["focus_areas"]))
    
    return extracted_info

def populate_checklist_from_extraction(extracted_info: dict, mode: str):
    """Fill checklist slots from extracted info without overriding explicit user-provided slots."""
    cl = st.session_state.checklist or {}
    mode_l = mode.lower()

    def set_if_empty(key, value):
        if key in cl and (cl[key] is None or cl[key] == []):
            cl[key] = value

    if "personal" in mode_l:
        if extracted_info.get("role"):
            set_if_empty("role_title", extracted_info["role"])
        if extracted_info.get("experience"):
            set_if_empty("years_experience", extracted_info["experience"])
        if extracted_info.get("technologies"):
            existing = set(cl.get("top_skills", []))
            merged = list(existing.union(set(extracted_info["technologies"])))
            cl["top_skills"] = merged
    elif "project" in mode_l:
        if extracted_info.get("technologies"):
            existing = set(cl.get("tech_stack", []))
            merged = list(existing.union(set(extracted_info["technologies"])))
            cl["tech_stack"] = merged
    else:  # learning
        if extracted_info.get("learning_topics"):
            existing = set(cl.get("learned_points", []))
            merged = list(existing.union(set(extracted_info["learning_topics"])))
            cl["learned_points"] = merged

    st.session_state.checklist = cl

def _canonicalize_title(title: str) -> str:
    """Normalize section title for comparison."""
    return title.strip().lower()

def _summarize_canvas_changes(old_md: str, new_md: str) -> str:
    """Return a short human message describing which sections changed."""
    old_secs, old_lines = _parse_markdown_sections(old_md)
    new_secs, new_lines = _parse_markdown_sections(new_md)
    changed = []
    added = []
    removed = []

    def body(lines, s):
        return "\n".join(lines[s['start']+1:s['end']]).strip()

    # Map by canonical title
    old_map = { _canonicalize_title(s['title']) : s for s in old_secs if s['level']>=2 }
    new_map = { _canonicalize_title(s['title']) : s for s in new_secs if s['level']>=2 }

    for key, ns in new_map.items():
        if key not in old_map:
            added.append(ns['title'])
        else:
            if body(old_lines, old_map[key]) != body(new_lines, ns):
                changed.append(ns['title'])
    for key, os in old_map.items():
        if key not in new_map:
            removed.append(os['title'])

    parts = []
    if changed:
        parts.append("Updated: " + ", ".join(changed))
    if added:
        parts.append("Added: " + ", ".join(added))
    if removed:
        parts.append("Removed: " + ", ".join(removed))
    return "; ".join(parts) if parts else "No material changes detected."

def detect_section_target(message: str, mode: str):
    """Detect if user is targeting a specific section (feat-005)."""
    ml = message.lower()
    # Common section names
    section_keywords = {
        "skills": ["skill", "skills", "technologies", "tech stack"],
        "experience": ["experience", "work history", "employment"],
        "projects": ["project", "projects", "work"],
        "about": ["about", "bio", "introduction", "profile"],
        "learning": ["learning", "education", "courses", "studies"]
    }
    
    for section, keywords in section_keywords.items():
        for kw in keywords:
            if kw in ml and ("section" in ml or "update" in ml or "add" in ml or "change" in ml):
                return section
    return None

def classify_intent(message, mode):
    message_l = message.lower().strip()
    action_keywords = [
        "add", "update", "modify", "include", "remove", "change", "insert", "replace"
    ]
    section_keywords = [
        "skill", "skills", "project", "projects", "learning", "bio", "experience", "about"
    ]
    tech_indicators = [
        "python", "javascript", "java", "react", "node", "sql", "aws", "docker", "kubernetes",
        "typescript", "angular", "vue", "mongodb", "postgresql", "mysql", "git", "github",
        "azure", "gcp", "linux", "html", "css", "sass", "tailwind", "bootstrap"
    ]

    is_request_change = any(k in message_l for k in action_keywords) and any(s in message_l for s in section_keywords)
    has_commas = "," in message_l
    has_number = any(tok.isdigit() for tok in message_l.split())
    mentions_tech = any(t in message_l for t in tech_indicators)

    if is_request_change:
        return "request-change"
    if has_commas or has_number or mentions_tech:
        return "provide-info"
    return "discuss"

def format_checklist_status(checklist: dict, mode: str) -> str:
    """Format checklist as readable status (feat-003)."""
    if not checklist:
        return "_No information gathered yet._"
    
    mode_l = mode.lower()
    lines = ["**Information Gathered:**"]
    
    if "personal" in mode_l:
        if checklist.get("role_title"):
            lines.append(f"- Role: {checklist['role_title']}")
        if checklist.get("years_experience"):
            lines.append(f"- Experience: {checklist['years_experience']} years")
        if checklist.get("top_skills"):
            lines.append(f"- Skills: {', '.join(checklist['top_skills'][:5])}")
        if checklist.get("tone"):
            lines.append(f"- Tone: {checklist['tone']}")
    elif "project" in mode_l:
        if checklist.get("project_name"):
            lines.append(f"- Project: {checklist['project_name']}")
        if checklist.get("tech_stack"):
            lines.append(f"- Tech Stack: {', '.join(checklist['tech_stack'][:5])}")
        if checklist.get("role_responsibilities"):
            lines.append(f"- Role: {checklist['role_responsibilities']}")
    else:  # learning
        if checklist.get("topic"):
            lines.append(f"- Topic: {checklist['topic']}")
        if checklist.get("learned_points"):
            lines.append(f"- Key Points: {', '.join(checklist['learned_points'][:3])}")
    
    return "\n".join(lines) if len(lines) > 1 else "_No information gathered yet._"

def generate_conversational_response(extracted_info: dict, sections_updated: list) -> str:
    """Generate natural, conversational response about what was updated"""
    parts = []
    
    # Greeting based on what was extracted
    if extracted_info.get("full_role"):
        parts.append(f"Great! I see you're a {extracted_info['full_role']}")
        
        if extracted_info.get("experience"):
            parts.append(f"with {extracted_info['experience']}")
        
        if extracted_info.get("focus_areas"):
            focus = extracted_info['focus_areas'][0]
            parts.append(f"specializing in {focus}")
    
    response = " ".join(parts) + "." if parts else "Got it!"
    
    # Mention what was updated
    if sections_updated:
        section_names = ", ".join(sections_updated)
        response += f"\n\nI've updated your **{section_names}** section{'s' if len(sections_updated) > 1 else ''} with this information."
    
    # Mention technologies if any
    if extracted_info.get("technologies"):
        tech_list = ", ".join(extracted_info["technologies"][:3])
        more = f" and {len(extracted_info['technologies']) - 3} more" if len(extracted_info["technologies"]) > 3 else ""
        response += f" Your tech stack now includes {tech_list}{more}."
    
    return response

def format_plan_message(intent: str, mode: str, checklist: dict) -> str:
    """Format assistant response with plan + checklist + confirm (feat-003)."""
    mode_l = mode.lower()
    
    # Plan section
    if intent == "provide-info":
        plan = "📋 **Plan:** Gathering information to enhance your canvas."
    elif intent == "request-change":
        plan = "✏️ **Plan:** Preparing a canvas update based on your request."
    else:
        plan = "💬 **Plan:** Discussing your input (no canvas changes)."
    
    # Checklist section
    checklist_status = format_checklist_status(checklist, mode)
    
    # Confirm/Next steps
    if intent == "provide-info":
        confirm = "\n\n_Updating canvas automatically as we gather information..._"
    elif intent == "request-change":
        confirm = "\n\n_Review the proposed changes. Use Apply/Undo controls when ready._"
    else:
        confirm = "\n\n_Let me know if you'd like to make any changes!_"
    
    return f"{plan}\n\n{checklist_status}{confirm}"

def update_checklist_from_message(message: str, mode: str):
    """Parse a provide-info style message and update checklist (basic heuristics)."""
    cl = st.session_state.checklist or {}
    msg = message.strip()
    msg_l = msg.lower()
    tokens = [t.strip() for t in msg.split(",") if t.strip()]

    def merge_list(key, values):
        existing = set(cl.get(key, []))
        merged = list(existing.union(set(values)))
        cl[key] = merged

    # years experience numeric detection
    years = None
    for w in msg_l.replace("years", "").split():
        if w.isdigit():
            years = w
            break

    mode_l = mode.lower()
    if "personal" in mode_l:
        if "role" in msg_l or "title" in msg_l:
            cl["role_title"] = msg
        if years:
            cl["years_experience"] = years
        if tokens:
            merge_list("top_skills", [t.lower() for t in tokens])
    elif "project" in mode_l:
        if "project" in msg_l and ":" in msg:
            cl["project_name"] = msg.split(":", 1)[1].strip() or msg
        if tokens:
            merge_list("tech_stack", [t.lower() for t in tokens])
    else:  # learning
        if "topic" in msg_l and ":" in msg:
            cl["topic"] = msg.split(":", 1)[1].strip()
        if tokens:
            merge_list("learned_points", [t.lower() for t in tokens])

    st.session_state.checklist = cl

def create_multi_section_content(extracted_info: dict, mode: str) -> str:
    """Generate comprehensive content for multiple sections based on extracted info"""
    sections = []
    
    # About Me section
    if extracted_info.get("full_role") or extracted_info.get("role"):
        about_parts = []
        role = extracted_info.get("full_role") or extracted_info.get("role", "Professional")
        about_parts.append(f"{role}")
        
        if extracted_info.get("seniority"):
            about_parts[0] = f"{extracted_info['seniority']} {about_parts[0]}"
        
        if extracted_info.get("experience"):
            about_parts.append(f"with {extracted_info['experience']}")
        
        if extracted_info.get("focus_areas"):
            focus = ", ".join(extracted_info["focus_areas"][:2])
            about_parts.append(f"specializing in {focus}")
        
        about_text = " ".join(about_parts) + "."
        
        if extracted_info.get("current_work"):
            about_text += f"\n\nCurrently focused on {extracted_info['current_work']}."
        
        sections.append(f"## About Me\n{about_text}")
    
    # Skills section
    if extracted_info.get("technologies"):
        skills_text = "## Skills\n"
        for tech in extracted_info["technologies"]:
            skills_text += f"- {tech}\n"
        
        if extracted_info.get("focus_areas"):
            skills_text += f"\n**Focus Areas:** {', '.join(extracted_info['focus_areas'])}\n"
        
        sections.append(skills_text.strip())
    
    # Experience section
    if extracted_info.get("experience") or extracted_info.get("full_role"):
        exp_text = "## Experience\n"
        
        if extracted_info.get("experience") and extracted_info.get("full_role"):
            exp_text += f"{extracted_info['experience']} as a {extracted_info['full_role']}"
        elif extracted_info.get("full_role"):
            exp_text += f"Professional experience as a {extracted_info['full_role']}"
        elif extracted_info.get("experience"):
            exp_text += f"{extracted_info['experience']} of professional experience"
        
        if extracted_info.get("focus_areas"):
            exp_text += f", focusing on {' and '.join(extracted_info['focus_areas'][:2])}"
        
        exp_text += "."
        sections.append(exp_text)
    
    # Current Focus section (if relevant)
    if extracted_info.get("current_work") or extracted_info.get("focus_areas"):
        focus_text = "## Current Focus\n"
        
        if extracted_info.get("current_work"):
            focus_text += f"{extracted_info['current_work'].capitalize()}.\n\n"
        
        if extracted_info.get("focus_areas"):
            focus_text += f"Areas of expertise: {', '.join(extracted_info['focus_areas'])}"
        
        sections.append(focus_text.strip())
    
    return "\n\n".join(sections)

def generate_section_content(section_name: str, user_input: str, mode: str, extracted_info: dict) -> str:
    """Generate content for a specific section only (feat-005)."""
    # Create focused prompt for the section
    section_templates = {
        "skills": f"""## Skills
- {', '.join(extracted_info.get('technologies', ['Add your skills here']))}
""",
        "experience": f"""## Experience
{extracted_info.get('experience', '0')} years of experience in {extracted_info.get('role', 'technology')}.
""",
        "projects": f"""## Projects
### Recent Project
Brief description of your project work.
""",
        "about": f"""## About Me
Professional {extracted_info.get('role', 'developer')} with expertise in various technologies.
""",
        "learning": f"""## Learning Journey
Continuous learning and skill development.
"""
    }
    
    # Return focused section content
    template = section_templates.get(section_name, f"## {section_name.title()}\nContent for {section_name}.")
    return template

def generate_content(user_input, current_canvas, mode, chat_history=None):
    """Generate content based on user input and mode using chat data"""
    
    # Extract info from chat history to avoid repetitive questions
    extracted_info = extract_user_info_from_chat(st.session_state.messages)
    st.session_state.user_data["extracted_info"] = extracted_info
    # keep checklist in sync with extracted info
    populate_checklist_from_extraction(extracted_info, mode)
    
    # Prepare context from extracted information
    context_parts = []
    
    if extracted_info["technologies"]:
        context_parts.append(f"Technologies: {', '.join(extracted_info['technologies'])}")
    if extracted_info["experience"]:
        context_parts.append(f"Years of experience: {extracted_info['experience']}")
    if extracted_info["role"]:
        context_parts.append(f"Role: {extracted_info['role']}")
    if extracted_info["projects"]:
        context_parts.append(f"Projects mentioned: {', '.join(extracted_info['projects'][:3])}")
    if extracted_info["learning_topics"]:
        context_parts.append(f"Learning topics: {', '.join(extracted_info['learning_topics'][:3])}")
    
    context = ". ".join(context_parts) if context_parts else "General professional background"
    
    # Get system prompt and generation prompt
    system_prompt = get_system_prompt(mode, context)
    generation_prompt = get_generation_prompt(mode, user_input, context, extracted_info)
    
    try:
        # Use chat_core with the enhanced prompts for README-style content
        params = {
            "content_type": mode.lower().replace(' ', '_'),
            "user_context": context,
            "system_prompt": system_prompt,
            "generation_prompt": generation_prompt,
            "format": "readme_markdown"
        }
        
        generated_content = chat_core.generate_from_template(
            session_id=f"ui_{mode.lower().replace(' ', '_')}",
            template_key="content_generation",
            params=params,
            history_limit=15,
        )
        
        # If generation fails or returns minimal content, provide a natural fallback
        if not generated_content or len(generated_content.strip()) < 20:
            generated_content = create_natural_fallback(mode, context, extracted_info, user_input)
        
        # Merge generated content into existing canvas in-place by matching sections
        updated_canvas = _merge_sections_inplace(current_canvas, generated_content)
            
        return generated_content, updated_canvas
        
    except Exception as e:
        # Natural fallback content generation
        fallback_content = create_natural_fallback(mode, context, extracted_info, user_input)
        # Merge fallback into canvas in-place
        updated_canvas = _merge_sections_inplace(current_canvas, fallback_content)
            
        return fallback_content, updated_canvas

def create_natural_fallback(mode, context, extracted_info, user_input):
    """Create natural README-style fallback content"""
    
    if mode == "Personal Bio":
        return f"""# Professional Profile

## About Me
Based on our conversation about {user_input.lower()}, here's a professional overview.

## Technical Skills
{format_technologies(extracted_info['technologies'])}

## Experience
{extracted_info['experience'] + ' years of experience' if extracted_info['experience'] else 'Professional experience'} in {extracted_info['role'] or 'technical field'}

## Current Focus
Continuing to develop skills and work on challenging projects.
"""
    
    elif mode == "Project Summaries":
        return f"""# Project Work

## Overview
Summary of project experience and technical work.

## Technologies Used
{format_technologies(extracted_info['technologies'])}

## Project Highlights
- Developed solutions using modern technologies
- Collaborated on team projects and deliverables
- Applied {extracted_info['role'] or 'technical'} expertise to solve problems

## Key Achievements
Successful project delivery and technical implementation.
"""
    
    else:  # Learning Reflections
        return f"""# Learning Journey

## Skills Development
Progress in mastering {', '.join(extracted_info['technologies'][:3]) if extracted_info['technologies'] else 'new technologies'}

## Recent Learning
{user_input}

## Application
Applying new knowledge to professional work and projects.

## Next Steps
Continuing to expand technical expertise and practical skills.
"""

def format_technologies(tech_list):
    """Format technologies list for README display"""
    if not tech_list:
        return "- Various programming languages and tools\n- Software development methodologies\n- Technical problem-solving"
    
    # Group technologies if there are many
    if len(tech_list) > 8:
        half = len(tech_list) // 2
        first_half = tech_list[:half]
        second_half = tech_list[half:]
        
        tech_display = ""
        for tech in first_half:
            tech_display += f"- {tech.title()}\n"
        tech_display += "\n## Additional Tools\n"
        for tech in second_half:
            tech_display += f"- {tech.title()}\n"
        return tech_display
    else:
        return "\n".join([f"- {tech.title()}" for tech in tech_list])

def _parse_markdown_sections(md: str):
    """Return list of sections with (level, title, start_idx, end_idx). end_idx is exclusive."""
    lines = md.splitlines()
    sections = []
    current = None
    for i, line in enumerate(lines):
        if line.strip().startswith('#'):
            # heading level
            hashes = len(line) - len(line.lstrip('#'))
            title = line.strip('# ').strip()
            if current is not None:
                current['end'] = i
                sections.append(current)
            current = {'level': hashes, 'title': title, 'start': i, 'end': len(lines)}
    if current is not None:
        sections.append(current)
    return sections, lines

def _find_section_index(sections, title: str):
    t_norm = title.strip().lower()
    for idx, sec in enumerate(sections):
        if sec['title'].strip().lower() == t_norm:
            return idx
    return -1

def _section_body_is_empty(lines, sec):
    body = lines[sec['start']+1:sec['end']]
    return all(not ln.strip() for ln in body)

def _add_section(md: str, title: str, template_body: str = ""):
    sections, lines = _parse_markdown_sections(md)
    if _find_section_index(sections, title) != -1:
        return md  # already exists
    # Insert at the end with a blank line separator
    new_block = []
    if lines and lines[-1].strip() != "":
        new_block.append("")
    new_block.append(f"## {title}")
    new_block.append("")
    if template_body.strip():
        new_block.extend(template_body.splitlines())
        if new_block[-1] != "":
            new_block.append("")
    return "\n".join(lines + new_block)

def _remove_section(md: str, title: str):
    sections, lines = _parse_markdown_sections(md)
    idx = _find_section_index(sections, title)
    if idx == -1:
        return md  # nothing to remove
    sec = sections[idx]
    # Remove the block and surrounding extra blank lines
    new_lines = lines[:sec['start']] + lines[sec['end']:]
    # Clean up consecutive blank lines
    cleaned = []
    prev_blank = False
    for ln in new_lines:
        is_blank = not ln.strip()
        if is_blank and prev_blank:
            continue
        cleaned.append(ln)
        prev_blank = is_blank
    return "\n".join(cleaned).strip() + "\n"

def _parse_section_command(message: str):
    """Detect add/remove section intents. Returns (action, title) or (None, None)."""
    m = message.strip()
    ml = m.lower()
    # Patterns: "add section X", "remove section X", "add X section", "remove X section"
    tokens = ml.replace(":", "").split()
    if not tokens:
        return None, None
    def title_from(parts):
        return " ".join([p for p in parts if p])
    if tokens[0] in ("add", "create"):
        if "section" in tokens:
            idx = tokens.index("section")
            title = title_from(m.split()[idx+1:])
            return ("add", title.strip()) if title.strip() else (None, None)
        if tokens[-1] == "section" and len(tokens) > 1:
            title = title_from(m.split()[1:-1])
            return ("add", title.strip()) if title.strip() else (None, None)
    if tokens[0] in ("remove", "delete"):
        if "section" in tokens:
            idx = tokens.index("section")
            title = title_from(m.split()[idx+1:])
            return ("remove", title.strip()) if title.strip() else (None, None)
        if tokens[-1] == "section" and len(tokens) > 1:
            title = title_from(m.split()[1:-1])
            return ("remove", title.strip()) if title.strip() else (None, None)
    return None, None

def _list_empty_sections(md: str):
    sections, lines = _parse_markdown_sections(md)
    empties = []
    for sec in sections:
        if _section_body_is_empty(lines, sec):
            empties.append(sec['title'])
    return empties

def _merge_sections_inplace(current_md: str, generated_md: str) -> str:
    """Merge generated sections into current markdown in place.
    - If a generated H2+ section exists in current, replace that entire section (heading + body).
    - If it doesn't exist, append that section to the end.
    - If no sections matched at all, replace entire canvas with generated_md (to avoid duplicate appends).
    """
    cur_secs, cur_lines = _parse_markdown_sections(current_md)
    gen_secs, gen_lines = _parse_markdown_sections(generated_md)

    # If no current sections, just return generated
    if not cur_secs:
        return generated_md

    # Work on a mutable copy
    cur_md_updated = "\n".join(cur_lines)
    matched = 0

    for gs in gen_secs:
        # Only merge H2+ sections (skip H1 titles)
        if gs['level'] < 2:
            continue
        title = gs['title']
        # Try direct match first
        cur_secs_now, cur_lines_now = _parse_markdown_sections(cur_md_updated)
        idx = _find_section_index(cur_secs_now, title)

        if idx != -1:
            # Replace existing section with generated section block
            cs = cur_secs_now[idx]
            g_block = gen_lines[gs['start']:gs['end']]
            new_lines = cur_lines_now[:cs['start']] + g_block + cur_lines_now[cs['end']:]
            cur_md_updated = "\n".join(new_lines)
            matched += 1
        else:
            # Append as a new section to the end
            g_body = "\n".join(gen_lines[gs['start']+1:gs['end']]).strip()
            cur_md_updated = _add_section(cur_md_updated, title, g_body)

    if matched == 0 and generated_md.strip():
        # No matching sections found; replace entire document to avoid duplication
        return generated_md

    return cur_md_updated

# Sidebar
with st.sidebar:
    st.markdown("### DevFolio AI Assistant")
    st.markdown("Select mode for generating professional content:")
    
    modes = ["Personal Bio", "Project Summaries", "Learning Reflections"]
    selected_mode = st.radio("Content Mode", modes)
    
    if selected_mode != st.session_state.mode:
        st.session_state.mode = selected_mode
        st.session_state.messages = []
        st.session_state.canvas_content = get_default_content(selected_mode)
        st.session_state.checklist = get_checklist_schema(selected_mode)
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Extracted Information")
    if st.session_state.user_data["extracted_info"]:
        info = st.session_state.user_data["extracted_info"]
        if info["technologies"]:
            st.write("**Technologies:**", ", ".join(info["technologies"]))
        if info["role"]:
            st.write("**Role:**", info["role"])
        if info["experience"]:
            st.write("**Experience:**", info["experience"], "years")
        if info["projects"]:
            st.write("**Projects:**", ", ".join(info["projects"][:3]))
        if info["learning_topics"]:
            st.write("**Learning:**", ", ".join(info["learning_topics"][:3]))
    
    st.markdown("---")
    st.markdown("### Quick Tips")
    st.write("• Chat naturally about your experience")
    st.write("• Content updates automatically as you chat")
    st.write("• One statement can update multiple sections")
    st.write("• Use Undo to revert unwanted changes")
    st.write("• Extraction improves as you share more")

# Layout
col_left, col_right = st.columns([1, 1])

# Chat Section
with col_left:
    st.markdown("### Chat With AI")
    
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Ask DevFolio AI..."):
        timestamp = datetime.now().strftime("%H:%M")

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })

        # Extract info from the message
        extracted_info = extract_user_info_from_chat(st.session_state.messages)
        st.session_state.user_data["extracted_info"] = extracted_info
        
        st.session_state.intent = classify_intent(prompt, st.session_state.mode)
        
        # AUTO-APPLY ALL CHANGES - No approval flow
        if st.session_state.intent in ("provide-info", "request-change"):
            before_md = st.session_state.canvas_content
            st.session_state.canvas_history.append(before_md)
            
            # Generate multi-section content if we have rich info
            if extracted_info.get("full_role") or extracted_info.get("role"):
                # Use multi-section generator for comprehensive updates
                multi_section_content = create_multi_section_content(extracted_info, st.session_state.mode)
                updated_canvas = _merge_sections_inplace(before_md, multi_section_content)
                
                # Track which sections were updated
                old_secs, _ = _parse_markdown_sections(before_md)
                new_secs, _ = _parse_markdown_sections(updated_canvas)
                sections_updated = [s['title'] for s in new_secs if s['level'] >= 2]
                
                # Generate conversational response
                response = generate_conversational_response(extracted_info, sections_updated)
            else:
                # Fallback to regular generation
                _gen_text, updated_canvas = generate_content(
                    prompt,
                    before_md,
                    st.session_state.mode
                )
                response = "I've updated your canvas with that information!"
            
            # Apply changes immediately
            st.session_state.canvas_content = updated_canvas
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": timestamp
            })
            st.rerun()
        else:
            # Discuss/neutral intent: friendly acknowledgment
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Got it! Let me know if you'd like me to update your canvas with any specific information.",
                "timestamp": timestamp
            })
            st.rerun()

# Canvas Section
with col_right:
    st.markdown("### Content Canvas")
    
    st.caption("Your content automatically formats as clean README-style markdown")

    canvas_content = st.text_area(
        "Edit your content",
        value=st.session_state.canvas_content,
        height=400,
        label_visibility="collapsed"
    )

    if canvas_content != st.session_state.canvas_content:
        st.session_state.canvas_history.append(st.session_state.canvas_content)
        st.session_state.canvas_content = canvas_content

    with st.expander("Live Preview"):
        st.markdown(st.session_state.canvas_content)
    
    # Quick actions
    st.markdown("### Quick Actions")
    
    # Undo Last Change control
    col1, col2 = st.columns(2)
    with col1:
        if st.button("↩️ Undo Last Change", disabled=len(st.session_state.canvas_history) == 0):
            if st.session_state.canvas_history:
                st.session_state.canvas_content = st.session_state.canvas_history.pop()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "↩️ Reverted to previous canvas state.",
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                st.rerun()
    with col2:
        if st.button("🔄 Refresh Extraction"):
            extracted_info = extract_user_info_from_chat(st.session_state.messages)
            st.session_state.user_data["extracted_info"] = extracted_info
            st.rerun()
    
    # Additional actions (feat-006: Refresh Canvas)
    col3, col4 = st.columns(2)
    with col3:
        if st.button("📝 Refresh Canvas", help="Regenerate canvas based on current chat context"):
            extracted_info = extract_user_info_from_chat(st.session_state.messages)
            st.session_state.user_data["extracted_info"] = extracted_info
            # Regenerate canvas
            _gen_text, updated_canvas = generate_content(
                "Refresh canvas with current information",
                st.session_state.canvas_content,
                st.session_state.mode
            )
            st.session_state.canvas_history.append(st.session_state.canvas_content)
            st.session_state.canvas_content = updated_canvas
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🔄 **Canvas refreshed** with latest information from our conversation!",
                "timestamp": datetime.now().strftime("%H:%M")
            })
            st.rerun()
    with col4:
        if st.button("🗑️ Clear Canvas", help="Reset canvas to default template"):
            st.session_state.canvas_content = get_default_content(st.session_state.mode)
            st.rerun()

# Footer
st.markdown("---")
st.caption(" DevFolio AI — Create your professional story in README format.")