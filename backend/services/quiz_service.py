# backend/services/quiz_service.py

from typing import List, Dict
from backend.infrastructure.session import get_db
from backend.repository.quiz_repo import QuizRepo
from backend.chains.quiz_chains import run_quiz_chain
from backend.schemas.quiz_schema import QuizCreate
from sqlalchemy.orm import Session
from fastapi import HTTPException

def generate_and_save_quiz(db: Session, quiz_create: QuizCreate) -> int:
    quiz_repo = QuizRepo(db)

    # 1) Gera as perguntas via chain (já com prompt, options, correct_letter, etc.)
    questions_generated = run_quiz_chain(
        theme=quiz_create.theme,
        n_questions=quiz_create.n_questions
    )

    # 2) Monte só o payload pro repo, sem gerar placeholders
    questions_with_alternatives = []
    for q in questions_generated:
        questions_with_alternatives.append({
            "prompt":         q["prompt"],
            "explanation":    q["explanation"],
            "correct_answer": q["correct_answer_letter"],
            "alternatives":   q["alternatives"],  
        })

    # 3) Salva no banco
    quiz_id = quiz_repo.create_quiz(
        theme=quiz_create.theme,
        n_questions=len(questions_with_alternatives),
        questions=questions_with_alternatives
    )
    return quiz_id


def save_and_check_answer(quiz_id: int, question_id: int, given_answer: str, db: Session) -> dict:
    repo = QuizRepo(db)   
    question = repo.get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")

    # Valida que a pergunta pertence a este quiz
    if question["quiz_id"] != quiz_id:
        raise HTTPException(status_code=400, detail="Pergunta não pertence a este quiz")

    # Compara resposta (letra)
    is_correct = question["correct_answer"].strip().upper() == given_answer.strip().upper()

    return {
        "question_id":   question["id"],
        "text":          question["prompt"],       # mapeia 'prompt' para 'text'
        "given_answer":  given_answer,
        "is_correct":    is_correct,
        "explanation":   question["explanation"],
    }