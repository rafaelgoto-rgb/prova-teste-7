from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.infrastructure.session import get_db
from backend.repository.email_repo import EmailRepo
from backend.schemas.email_schema import EmailCreate, EmailRead

router = APIRouter(prefix="/emails", tags=["Emails"])

@router.post("/", response_model=EmailRead)
def create_email(e: EmailCreate, db: Session = Depends(get_db)):
    """
    Cria um novo e-mail no banco de dados.

    Este endpoint recebe os dados de um e-mail (remetente, assunto e corpo),
    persiste no banco e retorna o registro criado.

    Args:
        e (EmailCreate): objeto com os campos necessários para criação do e-mail,
        db (Session, optional): sessão de banco de dados injetada pelo Depends.

    Returns:
        EmailRead: modelo de leitura do e-mail recém-criado, contendo id, sender,
                   subject, body e timestamps (created_at, updated_at).
    """
    email = EmailRepo(db).create(
        sender=e.sender,
        subject=e.subject,
        body=e.body
    )
    return email

@router.get("/", response_model=List[EmailRead])
def list_emails(db: Session = Depends(get_db)):
    """
    Retorna a lista de todos os e-mails cadastrados.

    Este endpoint busca no banco de dados todos os registros de e-mail
    e devolve uma lista formatada segundo o modelo EmailRead.

    Args:
        db (Session, optional): sessão de banco de dados injetada pelo Depends.

    Returns:
        List[EmailRead]: lista de objetos de leitura de e-mail, cada um contendo
                         id, sender, subject, body e timestamps.
    """
    return EmailRepo(db).list_all()
