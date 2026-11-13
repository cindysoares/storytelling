import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PROJECT_DIR = Path(__file__).resolve().parent.parent
# Variáveis do ambiente (por exemplo, Render) têm prioridade sobre arquivos locais.
load_dotenv(PROJECT_DIR / ".env.local", override=False)
load_dotenv(PROJECT_DIR / ".env", override=False)


def normalize_database_url(url: str) -> str:
    # Render/Neon podem fornecer URLs no formato postgres:// ou postgresql://.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL", "sqlite:///./storytelling.db")
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)
# DDL usa a conexão direta; consultas da aplicação usam DATABASE_URL (pooler).
unpooled_url = os.getenv("DATABASE_URL_UNPOOLED")
schema_engine = (
    create_engine(normalize_database_url(unpooled_url), pool_pre_ping=True)
    if unpooled_url
    else engine
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
