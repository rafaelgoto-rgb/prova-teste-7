from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from backend.infrastructure.session import get_db
from backend.repository.quiz_repo import QuizRepo
from backend.schemas.quiz_schema import QuizCreate, QuizOut, AnswerIn, AnswerOut
from backend.services.quiz_service import generate_and_save_quiz, save_and_check_answer

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.get("/", response_model=List[QuizOut])
def list_quizzes(db: Session = Depends(get_db)) -> List[QuizOut]:
    """
    Recupera e retorna todos os quizzes registrados no sistema.

    Args:
        db (Session, optional): Sessão do SQLAlchemy utilizada para acesso
            ao banco de dados. Obtida automaticamente via Depends(get_db).

    Returns:
        List[QuizOut]: Uma lista de instâncias de QuizOut, cada uma representando
        um quiz disponível.
    """
    quizzes = QuizRepo(db).list_quizzes()
    return quizzes

@router.post("/generate", response_model=QuizOut)
def create_quiz(q: QuizCreate, db: Session = Depends(get_db)) -> QuizOut:
    """
    Cria um novo quiz com base nos dados fornecidos, salva-o no banco de dados
    e retorna o quiz completo, incluindo as perguntas.

    Args:
        q (QuizCreate): Dados necessários para criar o quiz.
        db (Session, optional): Sessão do SQLAlchemy para operação no banco de dados.
            Obtida automaticamente via Depends(get_db).

    Returns:
        QuizOut: Objeto contendo os detalhes do quiz criado e sua lista de perguntas.

    Raises:
        HTTPException: Lança um erro 500 se não for possível recuperar o quiz
            gerado após a criação.
    """
    quiz_id = generate_and_save_quiz(db, q)
    quiz = QuizRepo(db).get_quiz_with_questions(quiz_id)
    if not quiz:
        raise HTTPException(status_code=500, detail="Falha ao recuperar quiz gerado")
    return quiz
 
@router.post("/{quiz_id}/answer", response_model=AnswerOut, summary="Registra e avalia uma resposta de quiz")
def answer_question(quiz_id: int, ans: AnswerIn, db: Session = Depends(get_db)) -> AnswerOut:
    """
    Registra a resposta de uma pergunta de um quiz e retorna o resultado da avaliação.

    Args:
        quiz_id (int): Identificador do quiz no qual a resposta está sendo registrada.
        ans (AnswerIn): Dados da resposta.
        db (Session, optional): Sessão do SQLAlchemy para operações de banco de dados.
            Obtida automaticamente via Depends(get_db).

    Returns:
        AnswerOut: Objeto contendo o resultado da avaliação.

    Raises:
        HTTPException 404: Se o quiz com `quiz_id` não for encontrado.
        HTTPException 404: Se a pergunta especificada por `ans.question_id` não for encontrada
            dentro do quiz.
    """
    # Verifica se o quiz existe
    if not QuizRepo(db).get_quiz_with_questions(quiz_id):
        raise HTTPException(status_code=404, detail="Quiz não encontrado")

    # Chama o serviço que salva e avalia
    result = save_and_check_answer(quiz_id=quiz_id,question_id=ans.question_id, given_answer=ans.given_answer, db=db)
    if result is None:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada")
    
    return result

@router.delete("/{quiz_id}", response_model=Dict[str, str], summary="Deleta um quiz")
def delete_quiz(quiz_id: int, db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    Exclui um quiz pelo seu identificador e retorna uma mensagem de confirmação.

    Args:
        quiz_id (int): Identificador do quiz a ser removido.
        db (Session, optional): Sessão do SQLAlchemy para operações no banco de dados.
            Obtida automaticamente via Depends(get_db).

    Returns:
        Dict[str, str]: Dicionário contendo a chave "message" com a mensagem de sucesso:
            {"message": "Quiz deletado com sucesso"}.

    Raises:
        HTTPException 404: Se não existir quiz correspondente ao `quiz_id` informado.
    """
    deleted = QuizRepo(db).delete_quiz(quiz_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Quiz não encontrado")
    return {"message": "Quiz deletado com sucesso"}
