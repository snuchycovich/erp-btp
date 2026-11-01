"""Fixtures for quote API integration tests."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.infrastructure.persistence.database import Base
from app.main import app
from app.presentation.api.dependencies import get_session


@pytest.fixture
def database_engine() -> Generator[Engine, None, None]:
    """Provide an isolated in-memory database engine."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def client(database_engine: Engine) -> Generator[TestClient, None, None]:
    """Provide an API client backed by the isolated database engine."""

    def override_get_session() -> Generator[Session, None, None]:
        with Session(database_engine) as session:
            yield session

    previous_override = app.dependency_overrides.get(get_session)
    app.dependency_overrides[get_session] = override_get_session

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_session, None)
        else:
            app.dependency_overrides[get_session] = previous_override
