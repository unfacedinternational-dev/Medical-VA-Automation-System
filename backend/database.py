import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Production uses Supabase PostgreSQL through MEDICAL_VA_DATABASE_URL.
# Local development keeps SQLite as the fallback.
if os.environ.get("VERCEL"):
    default_db_path = Path("/tmp") / "medical_va.db"
else:
    default_db_path = Path(__file__).resolve().parent.parent / "medical_va.db"

DATABASE_URL = os.environ.get("MEDICAL_VA_DATABASE_URL") or f"sqlite:///{default_db_path}"
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
