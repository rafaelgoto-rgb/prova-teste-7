from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Define o caminho para o banco SQLite (no diretório backend/db/usage.db)
db_path = os.path.join(os.path.dirname(__file__), "../db/usage.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

# Cria o engine de conexão com SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  
)

# Cria uma classe base para os modelos ORM
Base = declarative_base()

# Configura SessionLocal para criar sessões de banco de dados
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Função auxiliar para obter sessão no FastAPI Dependency
def get_db():
    """
    Gera uma sessão de banco de dados e garante o fechamento após o uso.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
