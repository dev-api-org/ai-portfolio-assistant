import streamlit as st
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="DevFolio AI",
    page_icon=None,  # Using a logo in the header
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 1rem 0;
        margin-bottom: 0.5rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 10px;
    }
    div[data-testid="stButton"] button[key="mode_Personal Bio"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    div[data-testid="stButton"] button[key="mode_Project Summaries"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
        border: none !important;
    }
    div[data-testid="stButton"] button[key="mode_Learning Reflections"] {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        color: white !important;
        border: none !important;
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

# Default canvas content
def get_default_content(mode):
    defaults = {
        "Personal Bio": """# Your Professional Bio

## About Me
[Add your introduction here]

## Skills & Expertise
- Skill 1
- Skill 2
- Skill 3

## Experience
[Describe your professional journey]

## Achievements
[Highlight your key accomplishments]

## Contact
[Your contact information]
""",
        "Project Summaries": """# Project Title

## Overview
[Brief project description]

## Objectives
- Objective 1
- Objective 2
- Objective 3

## Key Features
[List main features]

## Technologies Used
[Technologies and tools]

## Outcomes
[Project results and impact]

## Timeline
[Project duration and milestones]
""",
        "Learning Reflections": """# Learning Reflection

## Topic
[What did you learn?]

## Key Takeaways
- Insight 1
- Insight 2
- Insight 3

## Challenges Faced
[Difficulties encountered]

## How I Overcame Them
[Your problem-solving approach]

## Applications
[How will you use this knowledge?]

## Next Steps
[Future learning goals]
"""
    }
    return defaults.get(mode, "")

# Simulate AI response
def simulate_ai_response(user_input, current_canvas, mode):
    responses = {
        "Personal Bio": f"I'll help you enhance your bio. Let me add that to your profile...",
        "Project Summaries": f"Great project detail! I'm updating your summary...",
        "Learning Reflections": f"Excellent reflection! I'm documenting this insight..."
    }

    if "skill" in user_input.lower():
        current_canvas += f"\n- {user_input}"
    elif "project" in user_input.lower():
        current_canvas += f"\n\n## New Project\n{user_input}"
    elif "learn" in user_input.lower():
        current_canvas += f"\n- Learning: {user_input}"
    else:
        current_canvas += f"\n\n[Updated based on: {user_input[:50]}...]"

    return responses.get(mode, "I'm processing your input..."), current_canvas

# Main header with logo
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("frontend/img/devfolio-logo.png", width=500)
with col2:
    st.markdown('<h1 style="color:#764ba2;">DevFolio AI</h1>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### About DevFolio AI")
    st.markdown(
        "This AI Canvas Chat helps you draft and refine content for three modes: Personal Bio, Project Summaries, and Learning Reflections. "
        "Select a mode below, then chat with the assistant — the canvas on the right will update automatically. "
        "You can also manually edit the canvas, save or copy your content, and undo recent changes."
    )
    st.markdown("#### 🎯 Select Your Mode")

    modes = {
        "Personal Bio": {"icon": "🧑", "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"},
        "Project Summaries": {"icon": "📊", "gradient": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"},
        "Learning Reflections": {"icon": "📚", "gradient": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"}
    }

    for mode_name, mode_info in modes.items():
        is_selected = st.session_state.mode == mode_name
        button_label = f"{mode_info['icon']} {mode_name}"
        if st.button(button_label, key=f"mode_{mode_name}", use_container_width=True):
            if not is_selected:
                st.session_state.mode = mode_name
                st.session_state.messages = []
                st.session_state.canvas_content = get_default_content(mode_name)
                st.rerun()

# Main layout
col_left, col_right = st.columns([1, 1], gap="large")

# Left column - Chat Interface
with col_left:
    st.markdown("### 💬 Chat Interface")
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "timestamp" in message:
                    st.caption(message["timestamp"])

    if prompt := st.chat_input(f"Ask me to help with your {st.session_state.mode.lower()}..."):
        timestamp = datetime.now().strftime("%H:%M")
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": timestamp
        })
        st.session_state.canvas_history.append(st.session_state.canvas_content)
        if len(st.session_state.canvas_history) > 10:
            st.session_state.canvas_history.pop(0)

        ai_response, updated_canvas = simulate_ai_response(prompt, st.session_state.canvas_content, st.session_state.mode)
        st.session_state.canvas_content = updated_canvas
        st.session_state.messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": timestamp
        })
        st.rerun()

# Right column - Live Canvas
with col_right:
    st.markdown("### 🎨 Live Canvas")
    st.caption("This canvas updates automatically as you chat")
    canvas_content = st.text_area(
        "Edit your content:",
        value=st.session_state.canvas_content,
        height=400,
        key="canvas_editor",
        help="You can manually edit this content, or let the AI update it through conversation"
    )
    if canvas_content != st.session_state.canvas_content:
        st.session_state.canvas_history.append(st.session_state.canvas_content)
        if len(st.session_state.canvas_history) > 10:
            st.session_state.canvas_history.pop(0)
        st.session_state.canvas_content = canvas_content

    with st.expander("👁️ Preview Formatted", expanded=False):
        st.markdown(st.session_state.canvas_content)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("💾 Save", use_container_width=True):
            st.success("Canvas saved!")
    with col_b:
        if st.button("📋 Copy", use_container_width=True):
            try:
                js = f"<script>navigator.clipboard.writeText({json.dumps(st.session_state.canvas_content)});</script>"
                st.markdown(js, unsafe_allow_html=True)
                st.success("Canvas copied to clipboard!")
            except Exception:
                st.error("Unable to copy to clipboard in this environment.")

# Footer
st.markdown("---")
st.markdown(
    "<center>Made with ❤️ using Streamlit | Toggle modes to switch between different content types</center>",
    unsafe_allow_html=True
)
