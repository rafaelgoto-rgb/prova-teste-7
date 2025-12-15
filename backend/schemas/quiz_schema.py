from pydantic import BaseModel
from typing import List

class Answer(BaseModel):
    given_answer: str
    text: str              # texto da alternativa
    is_correct: bool

    class Config:
        orm_mode = True

class Question(BaseModel):
    id: int
    prompt: str
    explanation: str       # explicação da resposta correta
    answers: List[Answer]

    class Config:
        orm_mode = True

class QuizCreate(BaseModel):
    theme: str
    n_questions: int

class QuizOut(BaseModel):
    id: int
    theme: str
    n_questions: int
    questions: List[Question]

    class Config:
        orm_mode = True

class AnswerIn(BaseModel):
    question_id: int
    given_answer: str
 
class AnswerOut(BaseModel):
    question_id: int
    given_answer: str
    text: str  
    is_correct: bool
    explanation: str

    class Config:
        orm_mode = True
