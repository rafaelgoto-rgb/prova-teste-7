# backend/chains/qa_chain.py
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from backend.infrastructure.vectorstore import get_vectorstore_client
from backend.infrastructure.config import settings
def create_chat_chain():
    vs = get_vectorstore_client()  

    llm = ChatOpenAI(
        model=settings.CHAT_MODEL,
        streaming=True,
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vs.as_retriever(),
        return_source_documents=True,
    )