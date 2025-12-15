from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
import random
from sqlalchemy import text

from backend.schemas.quiz_schema import QuizOut
from backend.models.quiz import Quiz, Question, Answer

class QuizRepo:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create_quiz(self, theme: str, n_questions: int, questions: List[Dict[str, Any]]) -> int:
        """
        Cria um novo Quiz e suas perguntas associadas.
        Retorna o ID do quiz criado.
        questions: lista de dicts com chaves: prompt, correct_answer, explanation
        """
        quiz = Quiz(theme=theme, n_questions=n_questions)
        self.db.add(quiz)
        self.db.flush()  

        for q in questions:
            question = Question(
                prompt=q["prompt"],
                correct_answer=q["correct_answer"],
                explanation=q["explanation"],
                quiz_id=quiz.id
            )
            self.db.add(question)
            self.db.flush() 

            # Criar respostas (alternativas)
            for alt in q["alternatives"]:
                answer = Answer(
                    question_id=question.id,
                    given_answer=alt["letter"], 
                    text=alt["text"],           
                    is_correct=(alt["letter"] == q["correct_answer"])
                )
                self.db.add(answer)

        self.db.commit()
        self.db.refresh(quiz)
        return quiz.id

    def generate_options(self, question: Question, correct_text: str):
        """
        Gera 4 opções (A, B, C, D) para a questão, incluindo a correta.
        """
        letters = ['A', 'B', 'C', 'D']
        fake_answers = [
            "Resposta errada 1",
            "Resposta errada 2",
            "Resposta errada 3",
        ]
        random.shuffle(fake_answers)

        options_text = fake_answers[:]
        correct_position = random.randint(0, 3)
        options_text.insert(correct_position, correct_text)

        for idx, text in enumerate(options_text):
            answer = Answer(
                question_id=question.id,
                given_answer=letters[idx],
                is_correct=(idx == correct_position)
            )
            self.db.add(answer)

        # Atualiza o campo correct_answer da Question
        question.correct_answer = letters[correct_position]

    def get_quiz_with_questions(self, quiz_id: int) -> QuizOut:
        quiz: Quiz = (
            self.db.query(Quiz)
                   .filter(Quiz.id == quiz_id)
                   .first()
        )
        if not quiz:
            return None

        # monta a lista de perguntas já incluindo a explicação
        questions = []
        for q in quiz.questions:
            questions.append({
                "id": q.id,
                "prompt": q.prompt,
                "explanation": q.explanation,       # <-- aqui!
                "answers": [
                    {
                        "given_answer": a.given_answer,
                        "text":         a.text,       # texto da alternativa
                        "is_correct":   a.is_correct
                    }
                    for a in q.answers
                ]
            })

        return {
            "id":         quiz.id,
            "theme":      quiz.theme,
            "n_questions": quiz.n_questions,
            "questions":  questions
        }

    def save_and_check_answer(self, question_id: int, given_answer: str) -> Optional[Dict[str, Any]]:
        """
        Salva a resposta dada para a pergunta especificada,
        verifica se está correta e retorna:
          - question_id
          - is_correct
          - explanation
        """
        # Busca a pergunta
        question = self.db.query(Question).filter(Question.id == question_id).first()
        if not question:
            return None

        # Verifica correção (case-insensitive)
        is_correct = (given_answer.strip().upper() == question.correct_answer.strip().upper())
        answer = Answer(
            question_id=question.id,
            given_answer=given_answer,
            is_correct=is_correct
        )
        self.db.add(answer)
        self.db.commit()
        self.db.refresh(answer)

        return {
            "question_id": question.id,
            "is_correct": is_correct,
            "explanation": question.explanation
        }

    def list_quizzes(self) -> List[Quiz]:
        """
        Lista todos os quizzes existentes.
        """
        return self.db.query(Quiz).all()

    def delete_quiz(self, quiz_id: int) -> Optional[Quiz]:
        """
        Remove um Quiz pelo ID (e em cascade suas perguntas e respostas).
        Retorna o Quiz removido ou None.
        """
        quiz = self.db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if quiz:
            self.db.delete(quiz)
            self.db.commit()
        return quiz
    
    def get_question_by_id(self, question_id: int):
        query = text("""
            SELECT
                id,
                quiz_id,
                prompt,
                correct_answer,
                explanation
            FROM questions
            WHERE id = :question_id
        """)

        # .mappings() faz com que cada row seja dict-like
        result = self.db.execute(query, {"question_id": question_id}).mappings().first()
        if not result:
            return None

        return {
            "id": result["id"],
            "quiz_id": result["quiz_id"],
            "prompt": result["prompt"],
            "correct_answer": result["correct_answer"],
            "explanation": result["explanation"],
        }