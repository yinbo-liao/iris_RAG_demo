"""Shared fixtures for the Iris RAG test suite."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, get_db, override_engine
from app.models.models import KnowledgeDoc
from app.services.iris_service import KNOWLEDGE_DOCS


@pytest.fixture(scope="function")
def db_engine():
    """In-memory SQLite engine (single-connection via StaticPool so all sessions share data)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """SQLAlchemy session bound to in-memory SQLite."""
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def seeded_session(db_session):
    """Session pre-seeded with knowledge documents."""
    for doc in KNOWLEDGE_DOCS:
        kd = KnowledgeDoc(
            doc_id=doc["doc_id"],
            title=doc["title"],
            content=doc["content"],
            category=doc["category"],
        )
        db_session.add(kd)
    db_session.commit()
    return db_session


@pytest.fixture(scope="function")
def client(db_engine):
    """FastAPI TestClient with test DB override (SQLite)."""
    from app.models import get_session_factory

    override_engine(db_engine)

    from app.main import app

    def _override_get_db():
        """Drop-in replacement for get_db that uses the test engine."""
        db = get_session_factory()()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db

    from fastapi.testclient import TestClient
    with TestClient(app) as tc:
        yield tc
    app.dependency_overrides.clear()
