"""Shared pytest fixtures.

Tests run against an in-memory SQLite database so they need no running
Postgres instance. The app's ``get_db`` dependency is overridden to use a
session bound to that database, and the schema is created fresh for each
test for full isolation.
"""
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.db.dependencies import get_db
from src.main import app

# Import models so they register with Base.metadata before create_all.
import src.models  # noqa: F401


@pytest.fixture
def db_engine():
    """A fresh in-memory SQLite engine with all tables created."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """A SQLAlchemy session bound to the in-memory engine."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session) -> Generator[TestClient, None, None]:
    """A TestClient whose get_db dependency yields the test session."""

    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db_session
        finally:
            pass  # session lifecycle handled by the db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
