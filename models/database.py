import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///aivp.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def init_db():
    import models.entities  # noqa: F401 — ensures all models are registered
    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
