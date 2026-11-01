from __future__ import annotations
from typing import Any, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ── Request ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Natural language query")
    approach: Literal["function_call", "combined_tools"] = Field(
        ..., description="Processing approach: single tool or combined tools + RAG"
    )


# ── Tool schema ──────────────────────────────────────────────────────

class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: dict[str, Any]


# ── Knowledge document ───────────────────────────────────────────────

class KnowledgeDocOut(BaseModel):
    doc_id: str
    title: str
    content: str
    category: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ── Statistics ───────────────────────────────────────────────────────

class SpeciesStats(BaseModel):
    count: int
    species: str


class FeatureRange(BaseModel):
    sepal_length: dict[str, float]
    sepal_width: dict[str, float]
    petal_length: dict[str, float]
    petal_width: dict[str, float]


class StatsResponse(BaseModel):
    total_samples: int
    species_distribution: list[SpeciesStats]
    feature_ranges: FeatureRange
    knowledge_doc_count: int
    tools_count: int


# ── History ──────────────────────────────────────────────────────────

class HistoryEntry(BaseModel):
    id: int
    approach: str
    query_text: str
    tools_called: list[str]
    result_data: dict[str, Any] = Field(default_factory=dict)
    rag_used: str
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class HistoryClearResponse(BaseModel):
    deleted: int


# ── Tool result ──────────────────────────────────────────────────────

class ToolResult(BaseModel):
    tool: str
    result: Any


class KnowledgeResult(BaseModel):
    doc_id: str
    title: str
    content: str
    score: float


# ── Responses ────────────────────────────────────────────────────────

class FunctionCallResponse(BaseModel):
    approach: str = "function_call"
    approach_label: str = "Function Call"
    tools_called: list[str]
    rag_used: bool = False
    result: Any
    explanation: str
    query: str


class CombinedToolsResponse(BaseModel):
    approach: str = "combined_tools"
    approach_label: str = "Combined Tools (RAG + Functions)"
    tools_called: list[str]
    rag_used: bool = True
    results: list[ToolResult]
    knowledge: list[KnowledgeResult]
    synthesis: str
    explanation: str
    query: str


class CompareResponse(BaseModel):
    query: str
    function_call: FunctionCallResponse
    combined_tools: CombinedToolsResponse


# ── Seed response ────────────────────────────────────────────────────

class SeedResponse(BaseModel):
    message: str
    count: int


# ── Multi-agent ──────────────────────────────────────────────────────

class MultiAgentRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Natural language analytics request")


class AgentDefinition(BaseModel):
    agent: str
    role: str
    model: str
    suggested_model: str
    permissions: list[str]
    allowed_inputs: list[str]


class AgentRunOut(AgentDefinition):
    status: str
    duration_ms: float
    reasoning: str
    output: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None


class MultiAgentResponse(BaseModel):
    run_id: str
    query: str
    plan: list[str]
    agents: list[AgentRunOut]
    agent_count: int
    pattern_analysis: dict[str, Any]
    model_results: list[dict[str, Any]]
    evaluation: dict[str, Any]
    knowledge: list[dict[str, Any]]
    citations: list[dict[str, Any]]
    final_report: dict[str, Any]
    duration_ms: float
