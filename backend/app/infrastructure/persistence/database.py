"""Configure the SQLAlchemy database engine and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Provide the shared declarative base for the application's ORM models."""


engine = create_engine("sqlite:///./btp.db")

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session and close it after use."""
    with SessionLocal() as session:
        yield session
