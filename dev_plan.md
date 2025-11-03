Simplified AI Assistant Project - Chat Interface
Developer Roles

Dev 1: Backend (FastAPI + LangChain integration)
Dev 2: Frontend (Streamlit Chat UI) + GitHub Setup
Dev 3: Prompt Engineering + Documentation + Conversation Flow


Day 1: Setup & Foundation
Dev 1 (Backend):

Set up FastAPI project structure
Install dependencies (fastapi, langchain, uvicorn)
Create basic API with /chat endpoint for conversation

Dev 2 (Frontend + GitHub):

Create GitHub repo with branches (main, dev, prompt-design, ui, api-integration)
Set up Kanban board on GitHub Projects
Create Streamlit project with st.chat_message and st.chat_input

Dev 3 (Prompts + Docs):

Design conversational flow for each feature:

Bot asks questions to gather info
User responds naturally


Create initial system prompts for chat assistant
Define conversation stages (greeting → questions → generation)


Day 2: Core Development
Dev 1 (Backend):

Implement LangChain chat setup with memory/context
Create /chat endpoint that:

Receives user messages
Maintains conversation history
Returns AI responses


Add session management for conversations

Dev 2 (Frontend):

Build chat interface with Streamlit:

Message history display
Chat input box
User/Assistant message styling


Implement conversation state management
Add "Start New Conversation" button

Dev 3 (Prompts + Flow):

Design conversational prompts:

Bio flow: "Hi! I'll help you create a bio. What's your name?" → "What are your key skills?" → etc.
Project flow: "Let's create a project summary! What's the project name?" → "What technologies did you use?" → etc.
Reflection flow: "I'll help you write a learning reflection. What topic did you learn about?" → etc.


Define when bot should ask follow-up questions vs. generate final output


Day 3: Integration & Conversation Logic
Dev 1 (Backend):

Integrate Dev 3's conversational prompts
Add logic to detect when to:

Ask follow-up questions
Generate final output
Offer to start new topic


Implement conversation context tracking

Dev 2 (Frontend):

Connect chat UI to backend /chat endpoint
Display typing indicators during API calls
Add buttons for quick actions:

"Generate Bio"
"Summarize Project"
"Write Reflection"


Implement copy-to-clipboard for final outputs

Dev 3 (Integration):

Work with Dev 1 on conversation state management
Test conversation flows end-to-end
Refine prompts based on testing
Create conversation scripts/examples


Day 4: Polish & Features
Dev 1 (Backend):

Add ability to regenerate responses
Implement conversation export functionality
Add error handling for failed responses
Optimize response time

Dev 2 (Frontend):

Add sidebar with:

Conversation history
Quick action buttons
Examples section


Improve chat UI styling
Add message timestamps
Implement scroll-to-bottom on new messages

Dev 3 (UX + Docs):

Add welcome message with instructions
Create example conversations for each feature
Add helpful hints in chat (e.g., "Tip: Be specific about your skills")
Write user guide documentation
Test conversation flows with edge cases


Day 5: Final Polish & Demo
Dev 1 (Backend):

Final testing and optimization
Code cleanup
Merge branches

Dev 2 (Frontend):

Final UI polish and styling
Add branding/logo
Ensure responsive design
Prepare deployment

Dev 3 (Documentation):

Complete README.md with:

Setup instructions
How to use the chat interface
Example conversations


Document prompt engineering approach
Create demo video/presentation
Final end-to-end testing


Jira Board - 15 Cards
Epic: Project Setup (Day 1)

[Dev 2] Create GitHub repo, branches, and Kanban board
[Dev 1] Set up FastAPI with /chat endpoint structure
[Dev 2] Build basic Streamlit chat interface
[Dev 3] Design conversational flows for all 3 features

Epic: Backend Development (Day 2-3)

[Dev 1] Implement LangChain chat with conversation memory
[Dev 1] Add session management and context tracking
[Dev 1] Integrate conversational prompts and generation logic

Epic: Frontend Development (Day 2-3)

[Dev 2] Build chat UI with message history and input
[Dev 2] Add quick action buttons and navigation
[Dev 2] Connect frontend to backend chat API

Epic: Conversation Design (Day 2-3)

[Dev 3] Create system prompts for bio, summary, and reflection
[Dev 3] Test and refine conversation flows

Epic: Polish & Features (Day 4)

[Dev 1 + Dev 2] Add regenerate, export, and UI enhancements
[Dev 3] Add examples, welcome message, and user guidance

Epic: Documentation & Demo (Day 5)

[Dev 3] Complete documentation and demo preparation


Chat Flow Example
Bio Generation Conversation:
🤖 Assistant: Hi! I'm your AI assistant. I can help you create:
   • Professional bios
   • Project summaries  
   • Learning reflections
   
   What would you like to create today?

👤 User: I need a professional bio

🤖 Assistant: Great! I'll help you create a compelling bio. 
   Let's start with your name - what should I call you?

👤 User: John Doe

🤖 Assistant: Nice to meet you, John! What are your main 
   skills or areas of expertise?

👤 User: Python, machine learning, data analysis

🤖 Assistant: Excellent! Can you share 2-3 key achievements 
   or projects you're proud of?

👤 User: Built a recommendation system, led a team of 5 devs

🤖 Assistant: Perfect! What tone would you like - professional, 
   casual, or creative?

👤 User: Professional

🤖 Assistant: Here's your professional bio:
   
   [Generated Bio Content]
   
   Would you like me to regenerate it, or shall we work 
   on something else?

Key Features of Chat Interface
✅ Natural conversation - feels like chatting with a human assistant
✅ Context-aware - remembers what user said earlier
✅ Guided questions - bot asks for missing information
✅ Quick actions - buttons to jump to specific features
✅ Copy & export - easy to save generated content
✅ Regenerate option - can refine outputs
✅ Conversation history - see past chats in sidebar

Daily Coordination
Day 2 Evening: Dev 3 shares conversation scripts with Dev 1
Day 3 Morning: Dev 1 confirms chat API ready for Dev 2
Day 3 Afternoon: All devs test conversation flows together
Day 4 Morning: Team reviews UX and makes improvements

This chat-based approach makes the app more engaging and user-friendly! 🚀
