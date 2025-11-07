from langchain_google_genai import ChatGoogleGenerativeAI
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
import PyPDF2
import os
from io import BytesIO

# PDF Storage Management
class PDFManager:
    def __init__(self, base_path: str = "pdf_storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
    
    def store_pdf(self, session_id: str, pdf_file: bytes, filename: str) -> str:
        """Store PDF file for a session"""
        session_path = self.base_path / session_id
        session_path.mkdir(exist_ok=True)
        
        file_path = session_path / filename
        with open(file_path, 'wb') as f:
            f.write(pdf_file)
        
        return str(file_path)
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text content from PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {str(e)}")
    
    def get_session_pdfs(self, session_id: str) -> Dict[str, str]:
        """Get all PDFs and their content for a session"""
        session_path = self.base_path / session_id
        if not session_path.exists():
            return {}
        
        pdf_contents = {}
        for pdf_file in session_path.glob("*.pdf"):
            content = self.extract_text(str(pdf_file))
            pdf_contents[pdf_file.name] = content
        
        return pdf_contents
    
    def get_combined_pdf_content(self, session_id: str) -> str:
        """Get combined text from all PDFs in session"""
        pdfs = self.get_session_pdfs(session_id)
        if not pdfs:
            return ""
        
        combined = "PDF Documents Content:\n\n"
        for filename, content in pdfs.items():
            combined += f"--- {filename} ---\n{content}\n\n"
        
        return combined.strip()

# Initialize PDF Manager
pdf_manager = PDFManager()

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
    include_pdfs: bool = True
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

    # 3) Include PDF content if available and requested
    pdf_content = ""
    if include_pdfs:
        pdf_content = pdf_manager.get_combined_pdf_content(session_id)
        if pdf_content:
            user_input = f"PDF Context:\n{pdf_content}\n\nUser Question: {user_input}"

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
        path = Path(__file__).resolve().parent.parent / "prompts" / "prompts.json"
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

def render_template(template_key: str, params: Dict[str, Any]) -> tuple[str, str]:
    prompts = _load_prompts()
    if template_key not in prompts:
        raise KeyError(f"Unknown template '{template_key}'")
    t = prompts[template_key]
    required = list(t.get("parameters", {}).keys())
    missing = [p for p in required if p not in params]
    if missing:
        raise ValueError(f"Missing parameters for '{template_key}': {', '.join(missing)}")
    norm = _normalize_params(params)
    system_prompt = t["system_prompt"].format(**norm)
    user_prompt = t["user_prompt_template"].format(**norm)
    return system_prompt, user_prompt

def generate_from_template(
    session_id: str, 
    template_key: str, 
    params: Dict[str, Any], 
    history_limit: int = 20,
    include_pdfs: bool = True
) -> str:
    system_prompt, user_prompt = render_template(template_key, params)
    return chat_with_history(
        session_id=session_id,
        user_input=user_prompt,
        history_limit=history_limit,
        system_prompt=system_prompt,
        include_pdfs=include_pdfs
    )

# PDF Management Functions
def upload_pdf(session_id: str, pdf_file: bytes, filename: str) -> str:
    """Upload and store PDF for a session"""
    return pdf_manager.store_pdf(session_id, pdf_file, filename)

def get_pdf_content(session_id: str, filename: str | None = None) -> str:
    """Get content from specific PDF or all PDFs in session"""
    if filename:
        pdfs = pdf_manager.get_session_pdfs(session_id)
        return pdfs.get(filename, "")
    else:
        return pdf_manager.get_combined_pdf_content(session_id)

def list_session_pdfs(session_id: str) -> list[str]:
    """List all PDF files in session"""
    pdfs = pdf_manager.get_session_pdfs(session_id)
    return list(pdfs.keys())

def delete_pdf(session_id: str, filename: str) -> bool:
    """Delete specific PDF from session"""
    session_path = pdf_manager.base_path / session_id
    pdf_path = session_path / filename
    if pdf_path.exists():
        pdf_path.unlink()
        return True
    return False

# Enhanced chat function with PDF context
def chat_with_pdf_context(
    session_id: str,
    user_input: str,
    history_limit: int = 20,
    system_prompt: str | None = None
) -> str:
    """Chat function that automatically includes PDF context"""
    return chat_with_history(
        session_id=session_id,
        user_input=user_input,
        history_limit=history_limit,
        system_prompt=system_prompt,
        include_pdfs=True
    )

# Template generation with PDF context
def generate_from_template_with_pdfs(
    session_id: str,
    template_key: str,
    params: Dict[str, Any],
    history_limit: int = 200
) -> str:
    """Generate content from template using PDF data as context"""
    return generate_from_template(
        session_id=session_id,
        template_key=template_key,
        params=params,
        history_limit=history_limit,
        include_pdfs=True
    )