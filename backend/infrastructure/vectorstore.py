# backend/infra/vectorstore.py
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from backend.infrastructure.config     import settings
from backend.services.docs_loader import load_and_index

import os

def get_vectorstore_client():
    embeddings = OpenAIEmbeddings(model=settings.EMBEDDINGS_MODEL)

    if os.path.exists(settings.VS_PATH):
        return FAISS.load_local(
            settings.VS_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    return load_and_index()
