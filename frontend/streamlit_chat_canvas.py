import streamlit as st
from datetime import datetime
import json
import sys
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from frontend.components import file_upload
from backend import chat_core
# Prefer using the LLM service when available, with safe fallback
try:
    from backend import llm_service as llm  # type: ignore
except Exception:
    llm = None  # type: ignore


def safe_generate(session_id: str, content_type: str, extracted_info: dict, extra_input: str | None = None, history_limit: int = 25) -> str:
    """Use llm_service if available, else fall back to chat_core generic generator."""
    if llm is not None:
        try:
            if hasattr(llm, "generate_generic_content"):
                return llm.generate_generic_content(
                    session_id=session_id,
                    content_type=content_type,
                    extracted_info=extracted_info,
                    extra_input=extra_input,
                    history_limit=history_limit,
                )
            if hasattr(llm, "generate"):
                return llm.generate(
                    session_id=session_id,
                    content_type=content_type,
                    extracted_info=extracted_info,
                    extra_input=extra_input,
                    history_limit=history_limit,
                )
        except Exception:
            pass
    return chat_core.generate_generic_content(
        session_id=session_id,
        content_type=content_type,
        extracted_info=extracted_info,
        extra_input=extra_input,
        history_limit=history_limit,
    )

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
/* Match the textarea (live preview) to app background theme */
.stTextArea textarea {
    background-color: transparent; /* inherit background */
    color: inherit;
    border: 1px solid rgba(49,51,63,0.2);
}
/* Optional: tweak container to blend in better */
[data-testid="stTextArea"] > div > div > textarea {
    background-color: transparent !important;
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

def extract_user_info_from_chat(messages):
    """Extract key information from chat history with flexible parsing"""
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
    recent_messages = messages[-20:]  # Check last 20 messages
    
    full_text = " ".join([msg["content"] for msg in recent_messages if msg["role"] == "user"])
    full_text_lower = full_text.lower()
    
    # Extract name and title
    name_patterns = [
        r"([A-Z][a-z]+ [A-Z][a-z]+)",  # First Last
        r"my name is ([A-Z][a-z]+ [A-Z][a-z]+)",  # My name is John Doe
        r"i'm ([A-Z][a-z]+ [A-Z][a-z]+)",  # I'm John Doe
        r"i am ([A-Z][a-z]+ [A-Z][a-z]+)"  # I am John Doe
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, full_text)
        if match:
            extracted_info["name"] = match.group(1)
            break
    
    # Extract title/role
    title_keywords = {
        "senior": ["senior", "lead", "principal", "staff"],
        "developer": ["developer", "engineer", "programmer", "coder"],
        "fullstack": ["full stack", "fullstack", "full-stack"],
        "frontend": ["frontend", "front-end", "front end"],
        "backend": ["backend", "back-end", "back end"],
        "devops": ["devops", "sre", "infrastructure"],
        "data": ["data scientist", "data engineer", "data analyst"]
    }
    
    title_parts = []
    for category, keywords in title_keywords.items():
        for keyword in keywords:
            if keyword in full_text_lower:
                title_parts.append(keyword.title())
                break
    
    if title_parts:
        extracted_info["title"] = " ".join(title_parts)
    
    # Extract contact information
    email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', full_text)
    if email_match:
        extracted_info["contact"]["email"] = email_match.group(0)
    
    phone_match = re.search(r'(\+?(\d{1,3})?[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})', full_text)
    if phone_match:
        extracted_info["contact"]["phone"] = phone_match.group(0)
    
    # Extract location
    location_indicators = ["based in", "located in", "from", "living in"]
    for indicator in location_indicators:
        if indicator in full_text_lower:
            # Extract next few words after location indicator
            idx = full_text_lower.find(indicator)
            if idx != -1:
                location_text = full_text[idx + len(indicator):idx + len(indicator) + 50]
                # Simple extraction - could be enhanced with location database
                extracted_info["contact"]["location"] = location_text.split('.')[0].split(',')[0].strip()
                break
    
    # Extract technologies with categories
    tech_categories = {
        "frontend": ["react", "vue", "angular", "typescript", "javascript", "html", "css", "sass", "bootstrap", "tailwind"],
        "backend": ["node", "python", "java", "spring", "express", "django", "flask", "fastapi", "ruby", "php"],
        "database": ["mongodb", "postgresql", "mysql", "redis", "sql", "oracle", "dynamodb"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd"],
        "tools": ["git", "github", "gitlab", "jest", "webpack", "figma", "jira", "confluence"]
    }
    
    for category, techs in tech_categories.items():
        extracted_info["skills"][category] = []
        for tech in techs:
            if tech in full_text_lower:
                extracted_info["skills"][category].append(tech.title())
                extracted_info["technologies"].append(tech.title())
    
    # Remove duplicate technologies
    extracted_info["technologies"] = list(set(extracted_info["technologies"]))
    
    # Extract experience information
    experience_patterns = [
        r"(\d+)\+?\s*years?",  # 5+ years, 5 years
        r"(\d+)\+?\s*yr",      # 5+ yr, 5 yr
        r"experience.*?(\d+)",  # experience of 5
        r"(\d+).*?experience"   # 5 years experience
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, full_text_lower)
        if match:
            extracted_info["experience"]["years"] = match.group(1)
            break
    
    # Extract company names and positions
    company_indicators = [" at ", " from ", " with ", " working at ", " employed at "]
    for indicator in company_indicators:
        if indicator in full_text_lower:
            parts = full_text_lower.split(indicator)
            if len(parts) > 1:
                # Extract potential company name
                company_text = parts[1].split('.')[0].split(',')[0].strip()
                if len(company_text) > 2 and len(company_text.split()) <= 4:
                    if "companies" not in extracted_info["experience"]:
                        extracted_info["experience"]["companies"] = []
                    extracted_info["experience"]["companies"].append(company_text.title())
    
    # Extract education
    education_indicators = ["university", "college", "bachelor", "master", "phd", "degree", "graduated"]
    for indicator in education_indicators:
        if indicator in full_text_lower:
            idx = full_text_lower.find(indicator)
            if idx != -1:
                edu_text = full_text[idx:idx + 100].split('.')[0]
                extracted_info["education"].append(edu_text.strip())
    
    # Extract projects
    project_indicators = ["project", "built", "created", "developed", "implemented"]
    for indicator in project_indicators:
        if indicator in full_text_lower:
            # Extract sentences containing project indicators
            sentences = re.split(r'[.!?]+', full_text)
            for sentence in sentences:
                if indicator in sentence.lower() and len(sentence.strip()) > 20:
                    extracted_info["projects"].append(sentence.strip())
    
    # Extract achievements
    achievement_indicators = ["achieved", "accomplished", "award", "recognition", "success", "led", "managed"]
    for indicator in achievement_indicators:
        if indicator in full_text_lower:
            sentences = re.split(r'[.!?]+', full_text)
            for sentence in sentences:
                if indicator in sentence.lower() and len(sentence.strip()) > 15:
                    extracted_info["achievements"].append(sentence.strip())
    
    # Extract certifications
    cert_indicators = ["certified", "certification", "aws", "google cloud", "azure"]
    for indicator in cert_indicators:
        if indicator in full_text_lower:
            sentences = re.split(r'[.!?]+', full_text)
            for sentence in sentences:
                if indicator in sentence.lower():
                    extracted_info["certifications"].append(sentence.strip())
    
    # Clean up lists
    extracted_info["education"] = list(set(extracted_info["education"]))[:3]
    extracted_info["projects"] = list(set(extracted_info["projects"]))[:5]
    extracted_info["achievements"] = list(set(extracted_info["achievements"]))[:5]
    extracted_info["certifications"] = list(set(extracted_info["certifications"]))[:5]
    
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

def generate_content(user_input, mode, chat_history=None):
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
            new_content = safe_generate(
                session_id="ui_main",
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
    st.text_area(
        "Your Professional README",
        value=st.session_state.current_content,
        height=500,
        key="content_preview",
        label_visibility="collapsed"
    )
    # Auto-updates occur with each chat message and on mode switch; only keep Clear All
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_content = f"# {st.session_state.mode}\n\nChat to generate your {st.session_state.mode.lower()} in README format."
        st.session_state.user_data["extracted_info"] = {}
        st.rerun()

# Right Column - Chat Interface
with col_right:
    st.markdown("### 💬 Chat with AI")
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Share your professional experience or paste your resume..."):
        timestamp = datetime.now().strftime("%H:%M")
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        # Update extracted info
        extracted_info = extract_user_info_from_chat(st.session_state.messages)
        st.session_state.user_data["extracted_info"] = extracted_info
        old_content = st.session_state.current_content
        # Generate new content for current mode without clearing history
        try:
            new_content = safe_generate(
                session_id="ui_main",
                content_type=st.session_state.mode,
                extracted_info=extracted_info,
                extra_input=prompt,
                history_limit=25,
            )
            # Decide acknowledgement based on actual change
            if new_content and new_content.strip() and new_content.strip() != old_content.strip():
                st.session_state.current_content = new_content
                ai_response = "Updated your content. What else would you like to include or refine?"
            else:
                ai_response = "No changes detected. Try adding more specific details (skills, roles, metrics)."
        except Exception as e:
            st.error(f"Error updating content: {e}")
            ai_response = "I encountered an error while updating. Your message was saved, but the content did not change."
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": timestamp
        })
        st.rerun()

# Footer
st.markdown("---")
st.caption("© DevFolio AI — Comprehensive professional profile generation.")