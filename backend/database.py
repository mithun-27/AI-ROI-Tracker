"""
Database configuration for AI ROI Tracker.
Uses SQLite locally, supports PostgreSQL via DATABASE_URL env var.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Compute an absolute path to the db file in the backend directory
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_DB = f"sqlite:///{os.path.join(_BACKEND_DIR, 'roi_tracker.db').replace(os.sep, '/')}"
DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_DB)

# For SQLite, need check_same_thread=False
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
