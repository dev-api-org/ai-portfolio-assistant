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
if 'checklist' not in st.session_state:
    st.session_state.checklist = {}
if 'next_action' not in st.session_state:
    st.session_state.next_action = None

# Initialize checklist schema on first load based on current mode
if not st.session_state.checklist:
    st.session_state.checklist = get_checklist_schema(st.session_state.mode)

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
    """Extract key information from chat history to avoid repetitive questions"""
    extracted_info = {
        "skills": [],
        "experience": "",
        "role": "",
        "achievements": [],
        "technologies": [],
        "projects": [],
        "learning_topics": []
    }
    
    # Simple keyword-based extraction from recent messages
    recent_messages = messages[-10:]  # Only check last 10 messages
    
    for message in recent_messages:
        content = message["content"].lower()
        
        # Extract skills/technologies
        tech_keywords = ["python", "javascript", "java", "react", "node", "sql", "aws", "docker", "kubernetes", 
                        "typescript", "angular", "vue", "mongodb", "postgresql", "mysql", "git", "github", 
                        "azure", "gcp", "linux", "html", "css", "sass", "tailwind", "bootstrap"]
        for tech in tech_keywords:
            if tech in content:
                extracted_info["technologies"].append(tech)
        
        # Extract experience
        if "year" in content or "experience" in content:
            for word in content.split():
                if word.isdigit() and int(word) in range(1, 50):
                    extracted_info["experience"] = word
                    break
        
        # Extract role
        role_keywords = ["developer", "engineer", "designer", "manager", "analyst", "architect", 
                        "scientist", "researcher", "consultant", "specialist", "lead", "senior", "junior"]
        for role in role_keywords:
            if role in content:
                extracted_info["role"] = role
                break
                
        # Extract project mentions
        if "project" in content:
            # Simple extraction of project context
            words = content.split()
            for i, word in enumerate(words):
                if word == "project" and i + 1 < len(words):
                    next_word = words[i + 1]
                    if len(next_word) > 3:  # Basic filter
                        extracted_info["projects"].append(next_word)
        
        # Extract learning topics
        if "learn" in content or "study" in content or "course" in content:
            words = content.split()
            for i, word in enumerate(words):
                if word in ["learn", "learning", "studied", "course"] and i + 1 < len(words):
                    topic = words[i + 1]
                    if len(topic) > 3:
                        extracted_info["learning_topics"].append(topic)
    
    # Remove duplicates and clean up
    extracted_info["technologies"] = list(set(extracted_info["technologies"]))
    extracted_info["projects"] = list(set(extracted_info["projects"]))
    extracted_info["learning_topics"] = list(set(extracted_info["learning_topics"]))
    
    return extracted_info

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

def generate_content(user_input, current_canvas, mode, chat_history=None):
    """Generate content based on user input and mode using chat data"""
    
    # Extract info from chat history to avoid repetitive questions
    extracted_info = extract_user_info_from_chat(st.session_state.messages)
    st.session_state.user_data["extracted_info"] = extracted_info
    
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
        
        # Ensure the content is appended naturally to the canvas
        if current_canvas.strip():
            # Only add separator if there's existing content
            updated_canvas = current_canvas + f"\n\n---\n\n{generated_content}"
        else:
            updated_canvas = generated_content
            
        return generated_content, updated_canvas
        
    except Exception as e:
        # Natural fallback content generation
        fallback_content = create_natural_fallback(mode, context, extracted_info, user_input)
        
        if current_canvas.strip():
            updated_canvas = current_canvas + f"\n\n---\n\n{fallback_content}"
        else:
            updated_canvas = fallback_content
            
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
    st.write("• Content formats automatically as README")
    st.write("• No rigid templates - flow follows conversation")

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

        st.session_state.intent = classify_intent(prompt, st.session_state.mode)

        st.session_state.canvas_history.append(st.session_state.canvas_content)

        ai_response, updated_canvas = generate_content(
            prompt,
            st.session_state.canvas_content,
            st.session_state.mode
        )
        st.session_state.canvas_content = updated_canvas

        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
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
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Canvas"):
            st.session_state.canvas_content = get_default_content(st.session_state.mode)
            st.rerun()
    with col2:
        if st.button("Refresh Extraction"):
            extracted_info = extract_user_info_from_chat(st.session_state.messages)
            st.session_state.user_data["extracted_info"] = extracted_info
            st.rerun()

# Footer
st.markdown("---")
st.caption("© DevFolio AI — Create your professional story in README format.")