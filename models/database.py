import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aivp.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def _run_migrations():
    """Add any missing columns to existing tables (safe to run repeatedly)."""
    migrations = [
        "ALTER TABLE clients ADD COLUMN lora_weight FLOAT DEFAULT 0.8",
        "ALTER TABLE clients ADD COLUMN negative_prompt TEXT DEFAULT ''",
    ]
    with engine.connect() as conn:
        for sql in migrations:
            try:
                conn.execute(__import__("sqlalchemy").text(sql))
                conn.commit()
            except Exception:
                pass  # column already exists


def init_db():
    import models.entities  # noqa: F401 — ensures all models are registered
    Base.metadata.create_all(bind=engine)
    _run_migrations()


def get_session():
    return SessionLocal()
