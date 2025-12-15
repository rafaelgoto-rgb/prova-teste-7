# backend/models/email.py

from sqlalchemy import Column, Integer, String, Text
from backend.infrastructure.session import Base

class Email(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(255), nullable=False)  # Quem mandou o e-mail
    subject = Column(String(255), nullable=False) # Assunto do e-mail
    body = Column(Text, nullable=False)           # Corpo da mensagem