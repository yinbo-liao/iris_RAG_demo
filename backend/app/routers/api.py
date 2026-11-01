"""API route handlers for the Iris RAG application."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import get_db
from app.models.models import KnowledgeDoc, PredictionLog
from app.schemas.schemas import (
    KnowledgeDocOut,
    StatsResponse,
    HistoryEntry,
    HistoryClearResponse,
    SeedResponse,
    SpeciesStats,
    FeatureRange,
)
from app.services.iris_service import (
    df,
    KNOWLEDGE_DOCS,
    rebuild_vector_store,
)

router = APIRouter()


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/knowledge", response_model=list[KnowledgeDocOut])
def list_knowledge(db: Session = Depends(get_db)):
    """Return knowledge documents (from DB if seeded, otherwise from in-memory)."""
    docs = db.query(KnowledgeDoc).all()
    if docs:
        return docs
    return KNOWLEDGE_DOCS


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """Return dataset and system statistics."""
    species_dist = (
        df.groupby("species")
        .size()
        .reset_index(name="count")
        .assign(species=lambda x: x["species"])
    )
    dist = [SpeciesStats(species=r["species"], count=r["count"]) for _, r in species_dist.iterrows()]

    feature_ranges = FeatureRange(
        sepal_length={"min": 4.3, "max": 7.9, "avg": 5.84},
        sepal_width={"min": 2.0, "max": 4.4, "avg": 3.06},
        petal_length={"min": 1.0, "max": 6.9, "avg": 3.76},
        petal_width={"min": 0.1, "max": 2.5, "avg": 1.20},
    )

    doc_count = db.query(KnowledgeDoc).count() or len(KNOWLEDGE_DOCS)

    return StatsResponse(
        total_samples=len(df),
        species_distribution=dist,
        feature_ranges=feature_ranges,
        knowledge_doc_count=doc_count,
    )


@router.get("/history", response_model=list[HistoryEntry])
def get_history(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Return recent query history."""
    logs = (
        db.query(PredictionLog)
        .order_by(PredictionLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return logs


@router.delete("/history", response_model=HistoryClearResponse)
def clear_history(db: Session = Depends(get_db)):
    """Delete all query history entries."""
    deleted = db.query(PredictionLog).delete()
    db.commit()
    return HistoryClearResponse(deleted=deleted)


def _sync_vector_store(db: Session) -> None:
    """Point RAG retrieval at the DB-backed knowledge documents."""
    docs = [
        {"doc_id": d.doc_id, "title": d.title, "content": d.content, "category": d.category}
        for d in db.query(KnowledgeDoc).all()
    ]
    rebuild_vector_store(docs)


@router.post("/seed", response_model=SeedResponse)
def seed_database(db: Session = Depends(get_db)):
    """Seed the database with knowledge documents and refresh RAG retrieval."""
    existing = db.query(KnowledgeDoc).count()
    if existing > 0:
        _sync_vector_store(db)
        return SeedResponse(message="Database already seeded", count=existing)

    count = 0
    for doc in KNOWLEDGE_DOCS:
        kd = KnowledgeDoc(
            doc_id=doc["doc_id"],
            title=doc["title"],
            content=doc["content"],
            category=doc["category"],
        )
        db.add(kd)
        count += 1

    try:
        db.commit()
    except IntegrityError:
        # Another seed call won the race on the unique doc_id — its rows are fine.
        db.rollback()
        _sync_vector_store(db)
        return SeedResponse(
            message="Database already seeded",
            count=db.query(KnowledgeDoc).count(),
        )

    _sync_vector_store(db)
    return SeedResponse(message=f"Seeded {count} knowledge documents", count=count)
