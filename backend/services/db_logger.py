# backend/services/db_logger.py

import uuid
from sqlalchemy.orm import Session
from backend.models.message import Message

def new_session_id() -> str:
    """Gera um UUID para identificar a sessão de chat."""
    return str(uuid.uuid4())

def log_message(
    db: Session,
    session_id: str,
    role: str,
    content: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0
) -> None:
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens
    )
    db.add(msg)
    db.commit()