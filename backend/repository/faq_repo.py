# backend/repository/faq_repo.py

from sqlalchemy.orm import Session
from backend.models.faq import FAQ

class FAQRepo:
    def __init__(self, db_session: Session):
        self.db = db_session

    def upsert(self, question: str, answer: str, excerpt: str, link: str):
        """
        Atualiza uma FAQ se a pergunta já existir, senão cria uma nova.
        """
        faq = self.db.query(FAQ).filter(FAQ.question == question).first()
        if faq:
            faq.answer = answer
            faq.source = excerpt
        else:
            faq = FAQ(question=question, answer=answer, excerpt=excerpt, link=link)
            self.db.add(faq)
        
        self.db.commit()
        self.db.refresh(faq)
        return faq

    def list_all(self):
        """
        Retorna todas as FAQs cadastradas.
        """
        return self.db.query(FAQ).all()

    def get_by_question(self, question: str):
        """
        Busca uma FAQ específica pela pergunta.
        """
        return self.db.query(FAQ).filter(FAQ.question == question).first()

    def delete(self, question: str):
        """
        Remove uma FAQ pelo texto da pergunta.
        """
        faq = self.get_by_question(question)
        if faq:
            self.db.delete(faq)
            self.db.commit()
        return faq