from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.infrastructure.session import get_db
from backend.repository.faq_repo import FAQRepo
from backend.schemas.faq_schema import FAQRead, FAQCreate

router = APIRouter(prefix="/faq", tags=["FAQ"])

@router.get("/", response_model=List[FAQRead])
def list_faqs(db: Session = Depends(get_db)):
    """
    Recupera todas as FAQs cadastradas no sistema.

    Este endpoint consulta o repositório de FAQs e retorna
    a lista completa de perguntas e respostas no formato definido
    pelo modelo FAQRead.

    Args:
        db (Session, optional): sessão de banco de dados fornecida pelo Depends.

    Returns:
        List[FAQRead]: lista de objetos FAQRead.
    """
    faqs = FAQRepo(db).list_all()
    return faqs

@router.post("/", response_model=FAQRead)
def create_or_update_faq(f: FAQCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova FAQ ou atualiza uma existente no sistema.

    Este endpoint recebe os dados de uma FAQ (pergunta, resposta e fonte),
    realiza operação de upsert no repositório — ou seja, insere se não existir
    ou atualiza o registro existente baseado na pergunta — e retorna o objeto
    resultante no formato FAQRead.

    Args:
        f (FAQCreate): objeto com os campos necessários para criação ou atualização da FAQ,
        db (Session, optional): sessão de banco de dados fornecida pelo Depends.

    Returns:
        FAQRead: objeto contendo os dados da FAQ criada ou atualizada.
    """
    faq = FAQRepo(db).upsert(
        question=f.question,
        answer=f.answer,
        source=f.source
    )
    return faq

@router.delete("/", response_model=dict)
def delete_faq(question: str, db: Session = Depends(get_db)):
    """
    Remove uma entrada de FAQ com base na pergunta fornecida.

    Args:
        question (str): A pergunta exata da FAQ a ser removida do banco de dados.
        db (Session, optional): Sessão do SQLAlchemy para interação com o banco.  
            Obtida automaticamente via Depends(get_db).

    Returns:
        dict: Um dicionário contendo uma chave "message" com uma mensagem de sucesso
        ou erro.  
        - Se a FAQ for encontrada e removida, retorna:
            {"message": "FAQ deletada com sucesso"}  
        - Se não houver FAQ correspondente à pergunta, retorna:
            {"message": "FAQ não encontrada"}
    """
    deleted = FAQRepo(db).delete(question)
    if deleted:
        return {"message": "FAQ deletada com sucesso"}
    return {"message": "FAQ não encontrada"}

@router.post("/generate", response_model=List[FAQRead])
def generate_faqs(db: Session = Depends(get_db)):
    """
    Gera novas entradas de FAQ automaticamente e as persiste no banco de dados.

    Args:
        db (Session, optional): Sessão do SQLAlchemy para interação com o banco.  
            Obtida automaticamente via Depends(get_db).

    Returns:
        List[FAQRead]: Lista de objetos FAQRead representando as FAQs que foram
        geradas e salvas com sucesso.
    """
    from backend.services.faq_service import generate_and_save_faqs
    return generate_and_save_faqs()
