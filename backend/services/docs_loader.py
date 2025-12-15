# backend/services/docs_loader.py
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from backend.infrastructure.config import settings

# Configurações gerais\
MAX_PAGES = 400  # número máximo de páginas por seed
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Profundidades específicas por domínio
DEPTH_MAP = {
    "docs.python.org": 1,
    "fastapi.tiangolo.com": 0,
    "docs.streamlit.io": 4,
}

# Extensões de arquivos a ignorar no crawl
IGNORE_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".ico", ".webp"
)

def crawl_links(seed_urls, max_depth):
    """
    Navega links internos até max_depth, ignorando arquivos binários.
    """
    visited = set()
    queue = [(url, 0) for url in seed_urls]
    domain = urlparse(seed_urls[0]).netloc

    # Filtro de rota para Python docs
    require_path = "/tutorial/" if domain == "docs.python.org" else None

    while queue and len(visited) < MAX_PAGES:
        current_url, depth = queue.pop(0)
        lower_url = current_url.lower()
        # Ignorar URLs com extensões não-texto
        if any(lower_url.endswith(ext) for ext in IGNORE_EXTENSIONS):
            continue
        if current_url in visited or depth > max_depth:
            continue
        try:
            resp = requests.get(current_url, timeout=5)
            resp.raise_for_status()
        except Exception:
            continue
        visited.add(current_url)

        # Não expande se atingiu max_depth
        if depth == max_depth:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            next_url = urljoin(current_url, href)
            parsed = urlparse(next_url)
            # Restringe ao mesmo domínio
            if parsed.netloc != domain:
                continue
            # Remove fragmentos
            next_url = next_url.split('#')[0]
            lower_next = next_url.lower()
            # Ignorar arquivos binários
            if any(lower_next.endswith(ext) for ext in IGNORE_EXTENSIONS):
                continue
            # Aplica filtro de rota para Python
            if require_path and require_path not in parsed.path:
                continue
            if next_url not in visited:
                queue.append((next_url, depth + 1))

    return list(visited)


def load_and_index():
    """
    Carrega e indexa documentos públicos conforme settings.DOC_URLS e DEPTH_MAP.
    """
    all_urls = []
    for base in settings.DOC_URLS:
        domain = urlparse(base).netloc
        max_depth = DEPTH_MAP.get(domain, 1)
        pages = crawl_links([base], max_depth)
        all_urls.extend(pages)
    # Remove duplicatas mantendo ordem
    all_urls = list(dict.fromkeys(all_urls))

    # Carrega documentos
    loader = UnstructuredURLLoader(urls=all_urls)
    docs = loader.load()

    # Quebra em chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    chunks = splitter.split_documents(docs)

    # Gera embeddings e indexa no FAISS
    embeddings = OpenAIEmbeddings(model=settings.EMBEDDINGS_MODEL)
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(settings.VS_PATH)
    return vs
