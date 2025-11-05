from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import session_memory as memory
import config


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


def chat_with_history(session_id: str, user_input: str, history_limit: int = 20, system_prompt: str | None = None) -> str:
    history = memory.get_history(session_id)
    if system_prompt and not any(m.get("role") == "system" for m in history):
        memory.append_message(session_id, "system", system_prompt)
        history = memory.get_history(session_id)

    recent = history[-history_limit:] if history_limit else history
    messages = [_to_lc_message(m) for m in recent]
    messages.append(HumanMessage(content=user_input))

    llm = ChatGoogleGenerativeAI(model=config.MODEL_NAME, temperature=config.TEMPERATURE)
    resp = llm.invoke(messages)

    memory.append_message(session_id, "human", user_input)
    memory.append_message(session_id, "ai", resp.content)

    return resp.content
