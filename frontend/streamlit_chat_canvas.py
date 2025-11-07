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

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'canvas_content' not in st.session_state:
    st.session_state.canvas_content = ""
if 'mode' not in st.session_state:
    st.session_state.mode = "Personal Bio"
if 'canvas_history' not in st.session_state:
    st.session_state.canvas_history = []

def get_default_content(mode):
    defaults = {
        "Personal Bio": """# Your Professional Bio
## About Me
[Add your introduction here]
## Skills & Expertise
- Skill 1
- Skill 2
- Skill 3
""",
        "Project Summaries": """# Project Title
## Overview
[Brief project description]
""",
        "Learning Reflections": """# Learning Reflection
## Topic
[What did you learn?]
"""
    }
    return defaults.get(mode, "")

def generate_content(user_input, current_canvas, mode, key_skills="", achievements="", current_role="", years_exp="", chat_history=chat_core.chat_with_history("terminal", "user_input")):
    """Generate content based on user input and mode"""
    if mode == "Personal Bio":
        key_points_list = []
        if key_skills:
            key_points_list.append(f"Key skills: {', '.join([s for s in key_skills.splitlines() if s.strip()])}")
        if achievements:
            key_points_list.append(f"Achievements: {', '.join([a for a in achievements.splitlines() if a.strip()])}")
        if current_role:
            key_points_list.append(f"Current role: {current_role}")
        if years_exp:
            key_points_list.append(f"Experience: {years_exp} years")
        if chat_history:
            key_points_list.append(f"Additional context from chat: {chat_history}")
        
        params = {
            "content_type": "bio",
            "platform": "personal website",
            "key_points": [],
            "tone": "professional",
        }
        generated_content = chat_core.generate_from_template(
            session_id="ui_personal_bio",
            template_key="content_generation",
            params=params,
            history_limit=20,
        )
        return generated_content, current_canvas + f"\n\n{generated_content}"
    else:
        return "Mode not supported", current_canvas

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
        st.rerun()

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
    st.markdown("### Canvas Editor")

    canvas_content = st.text_area(
        "Your Content",
        value=st.session_state.canvas_content,
        height=400
    )

    if canvas_content != st.session_state.canvas_content:
        st.session_state.canvas_history.append(st.session_state.canvas_content)
        st.session_state.canvas_content = canvas_content

    with st.expander("Preview"):
        st.markdown(st.session_state.canvas_content)

# Footer
st.markdown("---")
st.caption("© DevFolio AI — Create your professional story.")
