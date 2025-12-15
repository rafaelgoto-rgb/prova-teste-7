from sqlalchemy import Column, Integer, String, Text
from backend.infrastructure.session import Base

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, unique=True, index=True)
    answer = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=False)
    link = Column(String)