"""Multi-agent analytics endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents import orchestrator
from app.models import get_db
from app.schemas.schemas import (
    AgentDefinition,
    MultiAgentRequest,
    MultiAgentResponse,
)
from app.services.audit import log_prediction

router = APIRouter()


@router.get("/agents/registry", response_model=list[AgentDefinition])
async def list_agents():
    """Return the agent roster, roles, suggested models, and permission scopes."""
    return orchestrator.registry()


@router.post("/agents/analyze", response_model=MultiAgentResponse)
def analyze(req: MultiAgentRequest, db: Session = Depends(get_db)):
    """Run the full multi-agent pipeline (sync endpoint: CPU-bound work runs in a threadpool)."""
    result = orchestrator.analyze(req.query)

    agent_names = [run["agent"] for run in result["agents"]]
    ranked = result.get("evaluation", {}).get("ranked_models") or []
    confidence: Any = ranked[0].get("f1") if ranked else None
    log_prediction(
        db,
        approach="multi_agent",
        query=req.query,
        tools_called=agent_names,
        result_data=result,
        rag_used=bool(result.get("knowledge")),
        confidence=confidence,
    )
    return result
