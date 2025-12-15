# backend/services/faq_service.py

import json
from difflib import SequenceMatcher
from typing import List, Dict

from backend.infrastructure.session import get_db
from backend.repository.email_repo import EmailRepo
from backend.repository.faq_repo import FAQRepo
from backend.chains.faq_chains import run_faq_chain

SIMILARITY_THRESHOLD = 0.7  

def find_best_match(question: str, candidates: List[str]) -> str | None:
    """
    Retorna a pergunta candidata com maior similaridade acima do limiar,
    ou None se nenhuma for parecida o suficiente.
    """
    best = None
    best_ratio = 0.0
    for cand in candidates:
        ratio = SequenceMatcher(None, question, cand).ratio()
        if ratio > best_ratio:
            best_ratio, best = ratio, cand
    if best_ratio >= SIMILARITY_THRESHOLD:
        return best
    return None

def generate_and_save_faqs() -> List[Dict]:
    db = next(get_db())
    email_repo = EmailRepo(db)
    faq_repo = FAQRepo(db)

    # 1) Pega todos os e-mails simulados
    raw_emails = [e.body for e in email_repo.list_all()]
    if not raw_emails:
        return []

    # 2) Gera as FAQs via LangChain
    faqs_generated = run_faq_chain(raw_emails)

    # 3) Carrega as perguntas já existentes
    existing_faqs = faq_repo.list_all()
    existing_questions = [f.question for f in existing_faqs]

    saved = []
    for item in faqs_generated:
        q_new = item["question"]
        # 4) Verifica se já existe pergunta similar
        q_matched = find_best_match(q_new, existing_questions)
        upsert_q = q_matched if q_matched else q_new

        faq = faq_repo.upsert(
            question=upsert_q,
            answer=item["answer"],
            excerpt=item["excerpt"],
            link=item["link"]

        )
        saved.append(faq)

        # Se criamos novo, garantir que entre nos candidatos para próximas iterações
        if q_matched is None:
            existing_questions.append(q_new)

    return saved
