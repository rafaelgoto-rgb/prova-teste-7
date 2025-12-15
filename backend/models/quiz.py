import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.infrastructure.session import Base

class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True, index=True)
    theme = Column(String, nullable=False)
    n_questions = Column(Integer, nullable=False)

    # Relacionamento com perguntas
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan"
    )

class Question(Base):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    prompt = Column(Text, nullable=False)
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text, nullable=False)

    # Relacionamentos
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan"
    )
    options = relationship(
        "Option",
        back_populates="question",
        cascade="all, delete-orphan"
    )

class Option(Base):
    __tablename__ = 'options'

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    letter = Column(String(1), nullable=False)
    text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)

    # Relacionamento de volta para pergunta
    question = relationship("Question", back_populates="options")

class Answer(Base):
    __tablename__ = 'answers'

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey('questions.id'), nullable=False)
    given_answer = Column(String(1), nullable=False) 
    text = Column(Text, nullable=False)  
    is_correct = Column(Boolean, nullable=False)

    question = relationship("Question", back_populates="answers")