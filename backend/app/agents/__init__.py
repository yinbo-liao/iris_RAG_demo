"""Multi-agent Iris analytics package.

Each agent has a single role, a deterministic implementation, an explicit set of
allowed inputs (least privilege), and an auditable run record.
"""

from app.agents.base import AgentRun, BaseAgent
from app.agents.data_pattern_agent import DataPatternAgent
from app.agents.model_agents import RandomForestAgent, SVMAgent, XGBoostAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.rag_agent import RAGKnowledgeAgent
from app.agents.orchestrator import MainOrchestratorAgent, orchestrator

__all__ = [
    "AgentRun",
    "BaseAgent",
    "DataPatternAgent",
    "RandomForestAgent",
    "SVMAgent",
    "XGBoostAgent",
    "EvaluationAgent",
    "RAGKnowledgeAgent",
    "MainOrchestratorAgent",
    "orchestrator",
]
