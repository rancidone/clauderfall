"""Database setup for the local MVP datastore."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DEFAULT_DB_PATH = Path(".clauderfall") / "clauderfall.db"


def create_sqlite_engine(db_path: Path | None = None):
    """Create a SQLite engine for local development."""

    resolved_path = db_path or DEFAULT_DB_PATH
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{resolved_path}", future=True)


def create_session_factory(db_path: Path | None = None) -> sessionmaker:
    """Build a configured SQLAlchemy session factory."""

    engine = create_sqlite_engine(db_path=db_path)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

