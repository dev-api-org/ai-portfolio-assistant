SESSIONS: dict[str, list[dict]] = {}


def get_history(session_id: str) -> list[dict]:
    return list(SESSIONS.get(session_id, []))


def append_message(session_id: str, role: str, content: str) -> None:
    history = SESSIONS.setdefault(session_id, [])
    history.append({"role": role, "content": content})


def reset_session(session_id: str) -> None:
    SESSIONS.pop(session_id, None)
