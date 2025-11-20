# DevFolio AI — AI Portfolio Assistant

A concise slide-style overview you can present or convert to slides.

---

## 1) Project Overview
- **What it is**: An AI assistant that generates professional bios, project summaries, and learning reflections in polished README-style Markdown.
- **Who it's for**: Students and professionals building portfolios and CVs who need structured, high‑quality content fast.
- **Primary value**: Turns unstructured chat input into clear, presentation-ready content with headings, sections, and bullet points.

---

## 2) Problem & Insight
- **Problem**: Writing portfolio content is time‑consuming and inconsistent across projects, roles, and audiences.
- **Insight**: Users often share experience and details conversationally. Capturing that context and guiding structure yields better, faster content.
- **Solution**: A chat-driven workflow that extracts key facts and dynamically generates professional writeups.

---

## 3) High-Level Solution
- **Chat UI (Streamlit)** to collect user context naturally.
- **Heuristic extractors** parse chat history for name, title, tech stack, experience, contact, projects, etc.
- **LLM (Gemini via LangChain)** generates structured Markdown tailored to the selected mode:
  - Personal Bio
  - Project Summaries
  - Learning Reflections
- **Live Preview** updates as the conversation evolves.

---

## 4) Architecture
- **Frontend**: Streamlit app (`frontend/streamlit_chat_canvas.py`)
  - Chat interface, live Markdown preview, mode switcher, sidebar with extracted info
  - Reads `backend/prompts.json` and `backend/systemprompts.json` if present
- **Backend Core**: (`backend/chat_core.py`)
  - Session chat history and system prompts
  - Prompt assembly and Gemini invocation via `langchain_google_genai.ChatGoogleGenerativeAI`
  - Generic content generator `generate_generic_content(...)`
- **Config**: (`backend/config.py`)
  - `MODEL_NAME`, `MODEL_TEMPERATURE`, and `GLOBAL_SYSTEM_PROMPT` (from `.env` or JSON)
- **LLM Test**: (`backend/llm_service.py`)
  - `test_gemini_connection()` simple terminal chat for local verification

---

## 5) Key Components (Code)
- `extract_user_info_from_chat(messages)` (frontend)
  - Safely parses last N user messages for: name, title, contact, technologies (categorized), experience years/companies, education, projects, achievements, certifications.
- `generate_generic_content(...)` (backend)
  - Builds a dynamic system prompt based on chosen content type
  - Summarizes extracted info and chat context
  - Calls `chat_with_history(...)` to produce README-format output
- `chat_with_history(session_id, user_input, ...)` (backend)
  - Ensures global and template-specific system prompts are included once per session
  - Invokes Gemini model with recent history to maintain context

---

## 6) Data & Prompts
- `backend/systemprompts.json` (optional): Overrides global system prompt.
- `backend/prompts.json` (optional): Legacy compatibility; not required for generic generation.
- Dynamic prompts emphasize:
  - Markdown structure
  - Conciseness and clarity
  - Using only available/affirmed details

---

## 7) Technology Stack
- **Language**: Python 3.10+
- **Frontend**: Streamlit
- **Backend/LLM**: LangChain + Google Gemini (`langchain_google_genai`)
- **Env**: `.env` with `GOOGLE_API_KEY`, `MODEL_NAME`, `MODEL_TEMPERATURE`

---

## 8) Setup & Run
- Create venv and install dependencies (from project root):
  - Windows (PowerShell)
    - `py -m venv .venv`
    - `.\.venv\Scripts\Activate`
    - `python -m pip install --upgrade pip`
    - `pip install -r requirements.txt`
- Environment:
  - Create `.env` with `GOOGLE_API_KEY=...`
  - Optional: `MODEL_NAME=gemini-2.0-flash`, `MODEL_TEMPERATURE=0.7`
- Run frontend (if using Streamlit app in `frontend/`):
  - `streamlit run frontend/streamlit_chat_canvas.py`
- Optional terminal LLM test:
  - `python -m backend.llm_service` and chat in terminal

---

## 9) Demo Flow (Suggested Slides)
- Start on the chat page with blank preview.
- Share a short background and a few projects in chat.
- Observe the live README preview update with:
  - Header, Contact, Summary, Skills, Experience, Projects, Achievements, Education
- Switch mode to "Project Summaries" or "Learning Reflections" and regenerate.
- Refine by adding metrics, technologies, and outcomes.

---

## 10) Results
- Consistent, well-structured Markdown suitable for portfolio pages, GitHub READMEs, and CV sections.
- Faster turnaround than writing from scratch.
- Content adapts to the target role and user-provided details.

---

## 11) Challenges & Solutions
- **Hallucination risk**: Instruct model to only use available data; show extracted info in sidebar.
- **Varying user detail**: Heuristics fill minimal structure; model prompts guide needed specifics.
- **Context management**: Chat history trimming and per-mode sessions to keep responses relevant.

---

## 12) Security & Privacy
- API key loaded via `.env`; never committed.
- No PII is persisted by default; chat state is in-memory per session.
- Add authentication/log redaction if deploying multi-user.

---

## 13) Extensibility
- Plug additional content modes (e.g., job-specific cover letters).
- Add export options (PDF, DOCX, PPTX) from Markdown.
- Connect uploads for resume parsing and indexing.
- Fine-tune prompts per industry or seniority.

---

## 14) Lessons Learned
- Conversational inputs + structured generation reduce cognitive load.
- Lightweight heuristics + LLMs provide practical, reliable outputs.
- Clear UX (live preview, extracted info) builds user trust.

---

## 15) Appendix
- Key files:
  - `frontend/streamlit_chat_canvas.py`
  - `backend/chat_core.py`
  - `backend/config.py`
  - `backend/llm_service.py`
  - `backend/systemprompts.json` (optional)
  - `backend/prompts.json` (optional)
- Env variables:
  - `GOOGLE_API_KEY`, `MODEL_NAME`, `MODEL_TEMPERATURE`, `GLOBAL_SYSTEM_PROMPT`

---

## How to Export to PowerPoint (Options)
- Use a Markdown-to-slides tool (Marp, Reveal.js, Deckset). Then export to PDF/PPT.
- Or paste each `##` section as a slide into PowerPoint and apply your brand template.
