from langchain_core.prompts import PromptTemplate
from backend.infrastructure.vectorstore import get_vectorstore_client
from langchain_openai import ChatOpenAI
from backend.infrastructure.config import settings
import json
from typing import List, Dict, Any

# PromptTemplate precisa de chaves duplas para JSON literal
quiz_template = PromptTemplate(
    input_variables=["theme", "n_questions"],
    template="""
Você é um assistente que gera quizzes baseados na documentação oficial de Python, FastAPI e Streamlit.
Gere exatamente {n_questions} perguntas de múltipla escolha sobre o tema "{theme}".
Retorne a saída no seguinte formato JSON:
[
  {{
    "prompt": "<texto da pergunta>",
    "options": {{
      "A": "<texto alternativa A>",
      "B": "<texto alternativa B>",
      "C": "<texto alternativa C>",
      "D": "<texto alternativa D>"
    }},
    "correct_answer": "<letra correta (A|B|C|D)>",
    "explanation": "<explicação sucinta>"
  }},
  ...
]
"""
)

# Retriever + LLM
vs = get_vectorstore_client()
retriever = vs.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(model=settings.CHAT_MODEL)

# Chain direta: só gera o texto bruto
quiz_chain = quiz_template | llm

def run_quiz_chain(theme: str, n_questions: int) -> List[Dict[str, Any]]:
    """
    Executa a chain para gerar um quiz e retorna lista de perguntas já normalizadas.
    """
    raw = quiz_chain.invoke({"theme": theme, "n_questions": n_questions})

    try:
        data = json.loads(raw.content)
        if not isinstance(data, list):
            raise ValueError("Formato esperado é uma lista de perguntas.")

        questions: List[Dict[str, Any]] = []
        for item in data:
            prompt = item.get("prompt", "")
            explanation = item.get("explanation", "")
            options = item.get("options", {})
            correct_letter = item.get("correct_answer")
            if correct_letter not in options:
                raise ValueError(f"Letra correta '{correct_letter}' não encontrada em options {options}")

            # Texto da resposta correta
            correct_text = options[correct_letter]
            # Converte options em lista de alternativas
            alternatives = [
                {"letter": letter, "text": text}
                for letter, text in options.items()
            ]

            questions.append({
                "prompt": prompt,
                "explanation": explanation,
                "correct_answer_letter": correct_letter,
                "correct_answer_text": correct_text,
                "alternatives": alternatives
            })
        return questions

    except json.JSONDecodeError as e:
        raise ValueError(f"Erro ao decodificar JSON do quiz: {e}\nRaw output:\n{raw.content}")
    except Exception:
        raise
