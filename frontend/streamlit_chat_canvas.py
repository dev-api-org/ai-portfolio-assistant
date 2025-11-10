import streamlit as st
from datetime import datetime
import json
import sys
import os
import pathlib
import re
from collections import OrderedDict

# Constants for maintainability
MAX_ANALYSIS_MESSAGES = 20
PREVIEW_HEIGHT = 500
LOCATION_CONTEXT_WINDOW = 50
MAX_MESSAGES_HISTORY = 200

# Load Streamlit secrets into environment variables for LangChain compatibility
# This ensures GOOGLE_API_KEY is available when deployed to Streamlit Cloud
if hasattr(st, "secrets"):
    for key in st.secrets:
        if key not in os.environ:
            os.environ[key] = str(st.secrets[key])

ROOT = pathlib.Path(__file__).resolve().parents[1]
# Avoid duplicate path injection
if str(ROOT) not in sys.path:
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
    logo_path = ROOT / "frontend" / "img" / "devfolio-logo.png"
    st.image(str(logo_path), width=180)

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
        # Fallback: capture first capitalized pair not containing common role words
        m = re.search(r"\b([A-Z][a-zA-Z\-']+\s+[A-Z][a-zA-Z\-']+)\b", full_text)
        if m:
            candidate = m.group(1)
            if not re.search(r"\b(Engineer|Developer|Manager|Senior|Lead|Principal)\b", candidate):
                name = candidate
    if name:
        extracted_info["name"] = name

    # Extract title/role with prioritization
    role_keywords = OrderedDict([
        ("level", ["principal", "staff", "lead", "senior", "jr", "junior"]),
        ("role", ["full stack", "full-stack", "fullstack", "frontend", "front-end", "front end", "backend", "back-end", "back end", "devops", "sre", "infrastructure", "data scientist", "data engineer", "data analyst"]),
        ("noun", ["developer", "engineer", "programmer", "coder"])])

    detected = {k: None for k in role_keywords}
    for k, words in role_keywords.items():
        for w in words:
            if re.search(rf"\b{re.escape(w)}\b", full_text_lower):
                detected[k] = w
                break
    title_parts = []
    if detected["level"]:
        title_parts.append(detected["level"].title().replace("Jr", "Junior"))
    if detected["role"]:
        role = detected["role"].title().replace("Full stack", "Full-Stack")
        title_parts.append(role)
    if detected["noun"]:
        title_parts.append(detected["noun"].title())
    if title_parts:
        extracted_info["title"] = " ".join(OrderedDict.fromkeys(title_parts))

    # Extract contact information
    email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", full_text)
    if email_match:
        extracted_info["contact"]["email"] = email_match.group(0)

    phone_match = re.search(r"\b(\+?\d{1,3}[\s-]?)?(\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4})\b", full_text)
    if phone_match:
        extracted_info["contact"]["phone"] = phone_match.group(0)

    # Extract location
    for indicator in ["based in", "located in", "from", "living in"]:
        idx = full_text_lower.find(indicator)
        if idx != -1:
            location_text = full_text[idx + len(indicator): idx + len(indicator) + LOCATION_CONTEXT_WINDOW]
            candidate = location_text.split('.')[0].split(',')[0].strip()
            if candidate and len(candidate.split()) <= 5:
                extracted_info["contact"]["location"] = candidate
                break

    # Extract technologies with categories using word boundaries
    tech_categories = {
        "frontend": ["react", "vue", "angular", "typescript", "javascript", "html", "css", "sass", "bootstrap", "tailwind"],
        "backend": ["node", "python", "java", "spring", "express", "django", "flask", "fastapi", "ruby", "php"],
        "database": ["mongodb", "postgresql", "mysql", "redis", "sql", "oracle", "dynamodb"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd"],
        "tools": ["git", "github", "gitlab", "jest", "webpack", "figma", "jira", "confluence"]
    }
    tech_flat = []
    for category, techs in tech_categories.items():
        extracted_info["skills"][category] = []
        for tech in techs:
            # ci/cd special-case word boundary
            pattern = r"\b" + re.escape(tech) + r"\b" if tech != "ci/cd" else r"\bci/?cd\b"
            if re.search(pattern, full_text_lower):
                label = tech.upper() if tech in {"aws", "gcp"} else tech.title()
                extracted_info["skills"][category].append(label)
                tech_flat.append(label)
    # Dedup while preserving order
    extracted_info["technologies"] = list(OrderedDict.fromkeys(tech_flat))

    # Extract experience years with constrained patterns
    years_match = re.search(r"\b(\d{1,2})\+?\s*(years?|yrs?)\b", full_text_lower)
    if years_match:
        extracted_info["experience"]["years"] = years_match.group(1)

    # Extract company names heuristically
    companies = []
    for indicator in ["worked at", "currently at", "at", "employed at", "with"]:
        for m in re.finditer(rf"\b{indicator}\b\s+([A-Za-z][A-Za-z&\-\s]{1,40})", full_text_lower):
            cand = m.group(1).strip().split('.')[0].split(',')[0]
            # Reject if too long or contains digits
            if 1 < len(cand.split()) <= 4 and not re.search(r"\d", cand):
                companies.append(cand.title())
    if companies:
        extracted_info["experience"]["companies"] = list(OrderedDict.fromkeys(companies))[:5]

    # Extract education (simple sentence-bound, trimmed)
    education_hits = []
    for indicator in ["university", "college", "bachelor", "master", "phd", "degree", "graduated"]:
        for m in re.finditer(rf"\b.{0,60}{indicator}.{{0,60}}", full_text_lower):
            snippet = full_text[m.start():m.end()]
            education_hits.append(snippet.strip().split('\n')[0])
    if education_hits:
        norm = list(OrderedDict.fromkeys([e.strip().capitalize() for e in education_hits]))
        extracted_info["education"] = norm[:3]

    # Extract projects/achievements/certs with basic thresholds
    def split_sentences(text: str):
        return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]

    sentences = split_sentences(full_text)

    for s in sentences:
        s_low = s.lower()
        if any(t in s_low for t in ["project", "built", "created", "developed", "implemented"]) and len(s) > 30:
            extracted_info["projects"].append(s)
        if any(t in s_low for t in ["achieved", "accomplished", "award", "recognition", "success", "led", "managed"]) and len(s) > 20:
            extracted_info["achievements"].append(s)
        if any(t in s_low for t in ["certified", "certification", "aws", "google cloud", "azure"]) and len(s) > 10:
            extracted_info["certifications"].append(s)

    # Clean up lists and cap sizes
    for key, cap in [("projects", 5), ("achievements", 5), ("certifications", 5)]:
        if extracted_info[key]:
            extracted_info[key] = list(OrderedDict.fromkeys(extracted_info[key]))[:cap]

    return extracted_info

def get_system_prompt(mode, extracted_info):
    """Get dynamic system prompt that adapts to available information"""
    
    base_prompt = f"""You are a professional content writer that creates comprehensive {mode.lower()} in README format.

Create a well-structured, professional document that incorporates all available information. Use appropriate markdown formatting with clear headings and sections.

Key guidelines:
- Structure the content logically based on what information is available
- Use consistent markdown formatting (headings, bullet points, etc.)
- Maintain a professional tone throughout
- Only include sections for which you have substantial information
- Make the document visually clean and easy to read

Available information to incorporate:"""

    # Add available information to the prompt
    info_parts = []
    
    if extracted_info["name"]:
        info_parts.append(f"Name: {extracted_info['name']}")
    if extracted_info["title"]:
        info_parts.append(f"Title/Role: {extracted_info['title']}")
    if extracted_info["contact"]:
        info_parts.append("Contact information available")
    if extracted_info["technologies"]:
        info_parts.append(f"Technologies: {', '.join(extracted_info['technologies'][:15])}")
    if extracted_info["experience"].get("years"):
        info_parts.append(f"Experience: {extracted_info['experience']['years']} years")
    if extracted_info["education"]:
        info_parts.append("Education history available")
    if extracted_info["projects"]:
        info_parts.append(f"Projects: {len(extracted_info['projects'])} mentioned")
    if extracted_info["achievements"]:
        info_parts.append("Achievements available")
    if extracted_info["certifications"]:
        info_parts.append("Certifications available")
    
    if info_parts:
        base_prompt += "\n- " + "\n- ".join(info_parts)
    else:
        base_prompt += "\n- General professional information from conversation"
    
    base_prompt += """

Structure the document with relevant sections such as:
- Name and title header
- Contact information
- Professional summary
- Technical skills (categorized)
- Professional experience
- Education
- Projects
- Achievements
- Certifications

But only include sections that have meaningful content available."""

    return base_prompt

def generate_content(user_input, mode, chat_history):
    """Generate comprehensive README-style content"""
    
    # Extract info from chat history
    extracted_info = extract_user_info_from_chat(st.session_state.messages)
    st.session_state.user_data["extracted_info"] = extracted_info
    
    # Get system prompt
    system_prompt = get_system_prompt(mode, extracted_info)
    
    # Create generation prompt
    generation_prompt = f"""Based on the entire conversation history, create a comprehensive {mode.lower()} in professional README format.

Recent input: {user_input}

Create a complete, well-structured document that incorporates all available information. Use proper markdown formatting with clear sections and professional presentation.

Focus on creating a polished, comprehensive document that showcases the professional profile effectively."""

    try:
        params = {
            "content_type": mode.lower().replace(' ', '_'),
            "system_prompt": system_prompt,
            "generation_prompt": generation_prompt,
            "format": "professional_readme",
            "extracted_info": extracted_info
        }
        
        generated_content = chat_core.generate_from_template(
            session_id=f"ui_{mode.lower().replace(' ', '_')}",
            template_key="content_generation",
            params=params,
            history_limit=25,
        )
        
        # Validate and return content
        if generated_content and len(generated_content.strip()) > 100:
            return generated_content
        else:
            return create_comprehensive_fallback(mode, extracted_info)
        
    except Exception as e:
        return create_comprehensive_fallback(mode, extracted_info)

def create_comprehensive_fallback(mode, extracted_info):
    """Create comprehensive fallback content"""
    
    content_parts = []
    
    # Header with name and title
    if extracted_info["name"] and extracted_info["title"]:
        content_parts.append(f"# {extracted_info['name']} - {extracted_info['title']}")
    elif extracted_info["name"]:
        content_parts.append(f"# {extracted_info['name']}")
    elif extracted_info["title"]:
        content_parts.append(f"# Professional Profile - {extracted_info['title']}")
    else:
        content_parts.append("# Professional Profile")
    
    content_parts.append("")
    
    # Contact section
    if extracted_info["contact"]:
        content_parts.append("## Contact")
        for key, value in extracted_info["contact"].items():
            if value:
                content_parts.append(f"- **{key.title()}**: {value}")
        content_parts.append("")
    
    # Summary section
    content_parts.append("## Professional Summary")
    summary = f"Experienced professional"
    if extracted_info["experience"].get("years"):
        summary += f" with {extracted_info['experience']['years']} years of experience"
    if extracted_info["technologies"]:
        summary += f" specializing in {', '.join(extracted_info['technologies'][:5])}"
    summary += ". Proven track record of delivering successful projects and solutions."
    content_parts.append(summary)
    content_parts.append("")
    
    # Technical Skills
    if extracted_info["skills"]:
        content_parts.append("## Technical Skills")
        for category, skills in extracted_info["skills"].items():
            if skills:
                content_parts.append(f"- **{category.title()}**: {', '.join(skills)}")
        content_parts.append("")
    elif extracted_info["technologies"]:
        content_parts.append("## Technical Skills")
        content_parts.append("- " + "\n- ".join(extracted_info["technologies"][:15]))
        content_parts.append("")
    
    # Professional Experience
    if extracted_info["experience"].get("companies") or extracted_info["experience"].get("years"):
        content_parts.append("## Professional Experience")
        if extracted_info["experience"].get("companies"):
            for company in extracted_info["experience"]["companies"][:3]:
                content_parts.append(f"### {extracted_info['title'] or 'Professional'} | {company}")
                content_parts.append("- Contributed to various projects and initiatives")
                content_parts.append("- Collaborated with team members on development tasks")
                content_parts.append("- Applied technical skills to solve business problems")
                content_parts.append("")
        else:
            content_parts.append(f"{extracted_info['experience'].get('years', 'Several')} years of professional experience in relevant roles.")
            content_parts.append("")
    
    # Education
    if extracted_info["education"]:
        content_parts.append("## Education")
        for edu in extracted_info["education"][:3]:
            content_parts.append(f"- {edu}")
        content_parts.append("")
    
    # Projects
    if extracted_info["projects"]:
        content_parts.append("## Projects")
        for i, project in enumerate(extracted_info["projects"][:4], 1):
            content_parts.append(f"### Project {i}")
            content_parts.append(f"{project}")
            content_parts.append("")
    
    # Achievements
    if extracted_info["achievements"]:
        content_parts.append("## Achievements")
        for achievement in extracted_info["achievements"][:5]:
            content_parts.append(f"- {achievement}")
        content_parts.append("")
    
    # Certifications
    if extracted_info["certifications"]:
        content_parts.append("## Certifications")
        for cert in extracted_info["certifications"][:5]:
            content_parts.append(f"- {cert}")
        content_parts.append("")
    
    return "\n".join(content_parts)

# Load prompts
# Static prompts are not required for the generic generator but keep loading for compatibility
PROMPTS, SYSTEM_PROMPTS = load_prompts()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'current_content' not in st.session_state:
    st.session_state.current_content = "# Your Professional Profile\n\nStart chatting to generate your comprehensive README-style content."
if 'mode' not in st.session_state:
    st.session_state.mode = "Personal Bio"
if 'user_data' not in st.session_state:
    st.session_state.user_data = {"extracted_info": {}}

# Sidebar
with st.sidebar:
    st.markdown("### DevFolio AI Assistant")
    st.markdown("Select content type:")
    
    modes = ["Personal Bio", "Project Summaries", "Learning Reflections"]
    selected_mode = st.radio("Content Mode", modes, key="mode_selector")

    # Do not reset chat history on mode switch; only regenerate content
    if selected_mode != st.session_state.mode:
        old_content = st.session_state.current_content
        st.session_state.mode = selected_mode
        # Regenerate content based on existing messages and extracted info
        extracted_info = extract_user_info_from_chat(st.session_state.messages)
        st.session_state.user_data["extracted_info"] = extracted_info
        try:
            new_content = chat_core.generate_generic_content(
                session_id=f"ui_{selected_mode.lower().replace(' ', '_')}",
                content_type=selected_mode,
                extracted_info=extracted_info,
                history_limit=25,
            )
            if new_content and new_content.strip() and new_content.strip() != old_content.strip():
                st.session_state.current_content = new_content
            else:
                # Keep old content; show subtle notice
                st.info("Switched mode. Current content unchanged — provide more details to tailor it.")
        except Exception as e:
            st.error(f"Failed to regenerate content on mode switch: {e}")
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Extracted Information")
    
    info = st.session_state.user_data.get("extracted_info", {})
    if info.get("name"):
        st.write("**Name:**", info["name"])
    if info.get("title"):
        st.write("**Title:**", info["title"])
    if info.get("technologies"):
        st.write("**Technologies:**", ", ".join(info["technologies"][:8]))
    if info.get("experience", {}).get("years"):
        st.write("**Experience:**", info["experience"]["years"], "years")
    if info.get("contact"):
        st.write("**Contact Info:**", "Available")
    
    st.markdown("---")
    st.markdown("### How to Use")
    st.write("• Share your professional background naturally")
    st.write("• Include details about experience, skills, projects")
    st.write("• Content updates automatically in README format")

# Layout - Two columns (Preview on the left as requested)
col_left, col_right = st.columns([1, 1])

# Left Column - Content Preview
with col_left:
    st.markdown("### 📄 Professional Content Preview")
    st.caption("Live README markdown preview — auto-updates from chat")
    # Display-only markdown to avoid confusing editability
    st.markdown(st.session_state.current_content)
    # Auto-updates occur with each chat message and on mode switch; only keep Clear All
    if st.button("🗑️ Clear All", use_container_width=True):
        # Cap history, then clear
        st.session_state.messages = []
        st.session_state.current_content = f"# {st.session_state.mode}\n\nChat to generate your {st.session_state.mode.lower()} in README format."
        st.session_state.user_data["extracted_info"] = {}
        st.rerun()

# Right Column - Chat Interface
with col_right:
    st.markdown("### 💬 Chat with AI")
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.messages[-MAX_MESSAGES_HISTORY:]:
            with st.chat_message(message.get("role", "assistant")):
                # Do not allow unsafe HTML in user/LLM message rendering
                st.markdown(message.get("content", ""))

    # Chat input
    if prompt := st.chat_input("Share your professional experience or paste your resume..."):
        ts_user = datetime.now().isoformat(timespec="seconds")
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": ts_user
        })
        # Keep only last MAX_MESSAGES_HISTORY messages
        if len(st.session_state.messages) > MAX_MESSAGES_HISTORY:
            st.session_state.messages = st.session_state.messages[-MAX_MESSAGES_HISTORY:]
        # Update extracted info
        extracted_info = extract_user_info_from_chat(st.session_state.messages)
        st.session_state.user_data["extracted_info"] = extracted_info
        old_content = st.session_state.current_content
        # Generate new content for current mode without clearing history
        try:
            new_content = chat_core.generate_generic_content(
                session_id=f"ui_{st.session_state.mode.lower().replace(' ', '_')}",
                content_type=st.session_state.mode,
                extracted_info=extracted_info,
                extra_input=prompt,
                history_limit=25,
            )
            # Decide acknowledgement based on actual change with minimal semantic check
            if new_content and new_content.strip() and new_content.strip() != old_content.strip() and len(new_content.strip()) > 50:
                st.session_state.current_content = new_content
                ai_response = "Updated your content. What else would you like to include or refine?"
            else:
                ai_response = "No significant changes detected. Try adding more specific details (skills, roles, metrics)."
        except Exception as e:
            st.error(f"Error updating content: {e}")
            ai_response = "I encountered an error while updating. Your message was saved, but the content did not change."
        ts_ai = datetime.now().isoformat(timespec="seconds")
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": ts_ai
        })
        st.rerun()

# Footer
st.markdown("---")
st.caption("© DevFolio AI — Comprehensive professional profile generation.")