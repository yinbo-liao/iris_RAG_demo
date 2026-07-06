from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    """Return the current engine, creating it lazily if needed."""
    global _engine
    if _engine is None:
        db_url = settings.get_database_url()
        is_sqlite = "sqlite" in db_url
        engine_kwargs: dict = {}
        if is_sqlite:
            engine_kwargs["connect_args"] = {"check_same_thread": False}
        else:
            engine_kwargs.update(pool_pre_ping=True, pool_size=10, max_overflow=20)
        _engine = create_engine(db_url, **engine_kwargs)
    return _engine


def get_session_factory():
    """Return the session factory bound to the current engine."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def override_engine(engine):
    """Swap the engine (used in tests to inject SQLite in-memory)."""
    global _engine, _SessionLocal
    _engine = engine
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency that yields a database session."""
    db = get_session_factory()()
    try:
        yield db
    finally:
        db.close()
