# backend/api/main.py
import tiktoken
from fastapi import FastAPI, Request, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from sqlalchemy.orm import Session

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from backend.infrastructure.session import engine, Base, get_db
from backend.infrastructure.vectorstore import get_vectorstore_client
from backend.infrastructure.config import settings
from backend.services.db_logger import new_session_id, log_message

from backend.models.faq import FAQ
from backend.models.message import Message
from backend.models.email import Email

from backend.routers.faq_router import router as faq_router
from backend.routers.email_router import router as email_router
from backend.routers.quiz_router import router as quiz_router

# Cria tabelas no startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Prova IA Generativa – Backend Starter", version="0.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

from contextlib import asynccontextmanager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Descomenta se quiser carregar todas (ou mais) as páginas de novo
    # from backend.services.docs_loader import load_and_index
    # load_and_index()
    get_vectorstore_client
    yield

app.router.lifespan_context = lifespan

# Função para contar tokens
def count_tokens(text: str, model: str = "gpt-4"):
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

@app.post("/chat/stream")
async def chat_stream(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    payload = await request.json()
    user_q = payload.get("question", "")
    session_id = payload.get("session_id") or new_session_id()

    vs = get_vectorstore_client()
    docs = vs.as_retriever().invoke(user_q)
    context = "\n\n".join(d.page_content for d in docs)

    prompt = (
        "Use os trechos abaixo para responder à pergunta."
        "Inclua sempre o trecho de origem.\n\n"
        f"{context}\n\nPergunta: {user_q}\nResposta:"
    )

    # Contagem dos tokens do prompt
    prompt_tokens = count_tokens(prompt, model=settings.CHAT_MODEL)

    # Loga pergunta do usuário
    log_message(
        db,
        session_id,
        role="user",
        content=user_q,
        prompt_tokens=prompt_tokens,
        completion_tokens=0
    )

    llm = ChatOpenAI(
        model=settings.CHAT_MODEL,
        streaming=True,
    )

    def gen():
        collected = ""

        stream = llm.stream([
            SystemMessage(content="Você é um assistente que responde com base em documentações técnicas."),
            HumanMessage(content=prompt),
        ])

        for chunk in stream:
            content = chunk.content
            collected += content
            yield content

        # Contagem dos tokens da resposta
        completion_tokens = count_tokens(collected, model=settings.CHAT_MODEL)

        # Loga mensagem da IA junto com tokens
        background_tasks.add_task(
            log_message,
            db,
            session_id,
            role="assistant",
            content=collected,
            prompt_tokens=0,
            completion_tokens=completion_tokens,
        )

    return StreamingResponse(gen(), media_type="text/plain")

@app.get("/health", tags=["Utils"])
def health_check():
    return {"status": "ok"}

app.include_router(email_router)
app.include_router(faq_router)
app.include_router(quiz_router)