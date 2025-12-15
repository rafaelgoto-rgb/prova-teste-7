# backend/models/message.py
from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from backend.infrastructure.session import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)       
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    prompt_tokens     = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)