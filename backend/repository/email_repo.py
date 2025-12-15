# backend/repository/email_repo.py

from sqlalchemy.orm import Session
from backend.models.email import Email

class EmailRepo:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, sender: str, subject: str, body: str):
        email = Email(sender=sender, subject=subject, body=body)
        self.db.add(email)
        self.db.commit()
        self.db.refresh(email)
        return email

    def list_all(self):
        return self.db.query(Email).all()