import sys
import pathlib

# Ensure repo root is on sys.path so imports work when running via `streamlit run frontend/streamlit_app.py`
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import streamlit as st
from frontend.components import file_upload


def main():
    st.set_page_config(
        page_title="AI Portfolio Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom styling
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }
        .option-card {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background-color: #f8f9fa;
            margin-bottom: 1rem;
            border: 2px solid #e9ecef;
        }
        .option-card:hover {
            border-color: #6c757d;
            background-color: #f1f3f5;
        }
        .chat-panel {
            margin-top: 2rem;
            padding: 1rem;
            border-radius: 0.5rem;
            background-color: #ffffff;
            border: 1px solid #dee2e6;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='main-header'>AI Portfolio Assistant</h1>", unsafe_allow_html=True)

    # Persistent sidebar with project info
    st.sidebar.title("AI-portfolio assistant")
    st.sidebar.markdown("""
    **Project Description**

    Build an AI-powered assistant that helps generate professional materials such as:

    - Personal bios / “About Me” sections
    - Project summaries
    - Learning reflections

    The assistant helps users craft polished, professional content for portfolios and profiles.
    """)
    st.sidebar.markdown("**Collaborators**\n\n- Olefile\n- Seward\n- Dingaan")

    # Three main options in cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.subheader("Personal Bio")
        st.write("Create or refine your 'About Me' section. Get help crafting a compelling personal narrative.")
        if st.button("Work on Personal Bio"):
            st.session_state.selected_option = "personal_bio"
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.subheader("Project Summaries")
        st.write("Develop clear, impactful descriptions of your projects and achievements.")
        if st.button("Work on Projects"):
            st.session_state.selected_option = "projects"
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='option-card'>", unsafe_allow_html=True)
        st.subheader("Learning Reflections")
        st.write("Document your learning journey, skills development, and growth mindset.")
        if st.button("Work on Reflections"):
            st.session_state.selected_option = "reflections"
        st.markdown("</div>", unsafe_allow_html=True)

    # Initialize session state for chat and selection
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_option" not in st.session_state:
        st.session_state.selected_option = None

    # If an option is selected, show the focused editor area with templates
    if st.session_state.selected_option:
        st.markdown("---")
        st.subheader(f"Editor — {st.session_state.selected_option.replace('_', ' ').title()}")

        # Initialize session state for generated content
        if "generated_content" not in st.session_state:
            st.session_state.generated_content = None

        main_col, side_col = st.columns([3, 1])
        with main_col:
            # Upload section
            st.subheader("📎 Upload Related Files")
            file_upload.render_upload()
            
            st.markdown("---")
            st.subheader("✏️ Input Details")
            
            if st.session_state.selected_option == "personal_bio":
                # Personal Bio inputs
                current_role = st.text_input("Current Role", placeholder="e.g., Senior Software Developer")
                years_exp = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
                key_skills = st.text_area("Key Skills (one per line)", 
                    placeholder="Python\nCloud Architecture\nTeam Leadership", height=100)
                achievements = st.text_area("Key Achievements (one per line)",
                    placeholder="Led a team of 5 developers\nDelivered project 20% under budget", height=100)
                
            elif st.session_state.selected_option == "projects":
                # Project Summary inputs
                project_name = st.text_input("Project Name", placeholder="e.g., AI Portfolio Assistant")
                role = st.text_input("Your Role", placeholder="e.g., Lead Developer")
                tech_stack = st.text_area("Technologies Used (one per line)",
                    placeholder="Python\nStreamlit\nOpenAI API", height=100)
                impact = st.text_area("Project Impact/Results",
                    placeholder="Reduced processing time by 50%\nIncreased user engagement by 30%", height=100)
                
            elif st.session_state.selected_option == "reflections":
                # Learning Reflection inputs
                learning_topic = st.text_input("Topic/Skill Learned", placeholder="e.g., Cloud Architecture")
                duration = st.text_input("Learning Duration", placeholder="e.g., 3 months")
                challenges = st.text_area("Challenges Faced (one per line)",
                    placeholder="Complex system design\nTime management while working", height=100)
                applications = st.text_area("Practical Applications",
                    placeholder="Applied to current project\nImproved team's efficiency", height=100)

            # Generate button
            if st.button("🚀 Generate Content", type="primary"):
                # Simulate AI generation (placeholder until backend is ready)
                if st.session_state.selected_option == "personal_bio":
                    st.session_state.generated_content = f"""
**Professional Bio**

A dedicated {current_role} with {years_exp} years of experience specializing in {key_skills.split()[0] if key_skills else 'technology'}. 
Proven track record of {achievements.split('\\n')[0] if achievements else 'delivering results'}. 
Core competencies include:

{key_skills}

Notable Achievements:
{achievements}
                    """
                elif st.session_state.selected_option == "projects":
                    st.session_state.generated_content = f"""
**{project_name} - Project Summary**

As the {role}, led the development and implementation of {project_name}. 

**Tech Stack:**
{tech_stack}

**Impact & Results:**
{impact}
                    """
                elif st.session_state.selected_option == "reflections":
                    st.session_state.generated_content = f"""
**Learning Journey: {learning_topic}**

Over {duration}, deeply engaged with {learning_topic}, overcoming challenges including:

**Challenges:**
{challenges}

**Practical Applications:**
{applications}
                    """

            # Show generated content if available
            if st.session_state.generated_content:
                st.markdown("### 📝 Generated Content")
                st.markdown(st.session_state.generated_content)
                
                # Add copy button
                if st.button("📋 Copy to Clipboard"):
                    st.info("Content copied! (Note: In the real app, this would copy to clipboard)")

        with side_col:
            st.info("💡 Tips for Best Results")
            if st.session_state.selected_option == "personal_bio":
                st.markdown("""
                - Be specific about your role
                - List technical skills
                - Include measurable achievements
                - Keep achievements STAR format
                """)
            elif st.session_state.selected_option == "projects":
                st.markdown("""
                - Name the technologies used
                - Quantify the impact
                - Highlight your specific role
                - Include team size if relevant
                """)
            elif st.session_state.selected_option == "reflections":
                st.markdown("""
                - Be specific about what you learned
                - Share concrete examples
                - Show growth mindset
                - Link theory to practice
                """)

    else:
        st.info("👋 Select one of the options above to start working on your portfolio content!")

    # Chat panel at the bottom (conversation area)
    st.markdown("<div class='chat-panel'>", unsafe_allow_html=True)
    st.subheader("💭 Conversation")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Show a contextual assistant prompt when a selection is made and no messages exist
    if st.session_state.selected_option and not st.session_state.messages:
        option_prompts = {
            "personal_bio": "Let's work on your personal bio. What would you like to focus on? (e.g., career highlights, skills, or professional journey)",
            "projects": "Tell me about a project you'd like to describe better. What's its main purpose and impact?",
            "reflections": "What learning experience or skill development would you like to reflect on?"
        }
        with st.chat_message("assistant"):
            st.write(option_prompts[st.session_state.selected_option])
        st.session_state.messages.append({"role": "assistant", "content": option_prompts[st.session_state.selected_option]})

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Simulate assistant response (placeholder - will connect to backend later)
        with st.chat_message("assistant"):
            selected = st.session_state.selected_option or "content"
            response = f"I understand you want help with your {selected.replace('_', ' ')}. [Backend response will go here]"
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
