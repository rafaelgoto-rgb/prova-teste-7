from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

class settings():
    BASE_DIR: str         = Path(__file__).parent.parent
    DB_DIR: str           = BASE_DIR / "db"
    VS_PATH: str          = str(DB_DIR / "faiss_index")
    USAGE_DB : str        = str(DB_DIR / "usage.db")
    OPENAI_API_KEY: str   = os.getenv("OPENAI_API_KEY")
    CHAT_MODEL: str       = os.getenv("CHAT_MODEL") 
    EMBEDDINGS_MODEL: str = os.getenv("EMBEDDINGS_MODEL")
    DOC_URLS              = [
        "https://docs.python.org/3/tutorial/",
        "https://fastapi.tiangolo.com/",
        "https://docs.streamlit.io/get-started/",
        "https://docs.streamlit.io/develop/",
        "https://docs.streamlit.io/deploy/",
        "https://docs.streamlit.io/knowledge-base/"
    ]