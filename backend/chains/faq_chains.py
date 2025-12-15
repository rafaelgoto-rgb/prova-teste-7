# backend/chains/faq_chains.py

import json
from typing import List, Dict
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from backend.infrastructure.config import settings
from backend.infrastructure.vectorstore import get_vectorstore_client
import re

# 1) Template
faq_template = PromptTemplate(
    input_variables=["emails"],
    template="""
Você é um assistente que recebe várias dúvidas de alunos por e-mails e deve:
1) Agrupar perguntas semelhantes.
2) Para cada grupo, gerar uma pergunta FAQ clara e sua resposta.
3) No campo 'excerpt', inclua obrigatoriamente o trecho exato encontrado na documentação 
4) No campo 'link' inclua o link para a página de origem do trecho de 'excerpt'.

Emails:
{emails}

Retorne em JSON: [{{"question": ..., "answer": ..., "excerpt": ..., "link":...}}, ...]
"""
)

# 2) Retriever + LLM
vs = get_vectorstore_client()
retriever = vs.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model=settings.CHAT_MODEL)

# 3) Chain
faq_chain = faq_template | llm

def build_enriched_emails(emails: List[str]) -> List[str]:
    """
    Para cada e-mail, busca os docs relevantes e 
    adiciona ao texto original para contexto.
    """
    enriched = []
    for body in emails:
        docs = retriever.invoke(body)
        context = "\n\n".join(d.page_content for d in docs)
        enriched.append(f"E-mail:\n{body}\n\nContexto encontrado:\n{context}")
    return enriched

def run_faq_chain(raw_emails: List[str]) -> List[Dict]:
    # 1) Enriquecer os e-mails com contexto
    enriched = build_enriched_emails(raw_emails)

    # 2) Invocar o chain
    result = faq_chain.invoke({"emails": enriched})

    # 3) Extrair o texto bruto de onde der
    if isinstance(result, str):
        text = result
    elif hasattr(result, "content"):
        text = result.content
    elif hasattr(result, "generations"):
        text = result.generations[0][0].text
    else:
        text = str(result)

    # 4) Remove fences Markdown ```json e ``` se existirem
    text = re.sub(r"^```(?:json)?\s*", "", text)    # remove ```json or ```
    text = re.sub(r"\s*```$", "", text)             # remove trailing ```
    text = text.strip()

    # 5) Tenta fazer o loads
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print("=== RAW LLM OUTPUT (FAILED TO PARSE) ===")
        print(text)
        print("=== END RAW OUTPUT ===")
        
        raise RuntimeError(
            f"Resposta do chain não é JSON válido: {e}\n\n"
            f"--- RAW OUTPUT ---\n{text}\n------------------"
        )
