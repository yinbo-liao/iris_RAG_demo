"""Shared persistence helper for query/agent audit logs."""

from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np
from sqlalchemy.orm import Session

from app.models.models import PredictionLog

logger = logging.getLogger(__name__)


def json_safe(value: Any) -> Any:
    """Recursively convert numpy scalars/arrays so the JSON column can store them."""
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def log_prediction(
    db: Session,
    approach: str,
    query: str,
    tools_called: list[str],
    result_data: dict[str, Any],
    rag_used: bool,
    confidence: Optional[float] = None,
) -> None:
    """Best-effort audit write; a logging failure must not fail the request."""
    try:
        db.add(
            PredictionLog(
                approach=approach,
                query_text=query,
                tools_called=tools_called,
                result_data=json_safe(result_data),
                rag_used="yes" if rag_used else "no",
                confidence=confidence,
            )
        )
        db.commit()
    except Exception:
        logger.exception("Failed to write prediction log")
        db.rollback()
