"""RAG Knowledge Agent — read-only retrieval over the TF-IDF knowledge base."""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult, BaseAgent
from app.services.iris_service import vector_store


class RAGKnowledgeAgent(BaseAgent):
    name = "RAG Knowledge Agent"
    role = "Retrieve botanical, dataset, and ML-practice knowledge to explain results."
    suggested_model = "GPT-4o-mini (retrieval-tuned small model)"
    permissions = ("read:vector_store", "read:knowledge_base")
    allowed_inputs = ("query", "evaluation", "pattern_analysis")

    def run(self, context: dict[str, Any]) -> AgentResult:
        user_query = context.get("query", "")
        evaluation = context.get("evaluation") or {}
        pattern = context.get("pattern_analysis") or {}

        enrichment: list[str] = []
        if evaluation.get("best_model"):
            enrichment.append(str(evaluation["best_model"]))
        ranked = pattern.get("ranked_features") or []
        if ranked:
            enrichment.append(str(ranked[0]))
        retrieval_query = " ".join([user_query, *enrichment]).strip()

        top_k = 4
        documents = vector_store.search(retrieval_query, top_k=top_k)

        citations = [
            {
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "score": doc["score"],
            }
            for doc in documents
        ]

        return AgentResult(
            output={
                "retrieval_query": retrieval_query,
                "top_k": top_k,
                "documents": documents,
                "citations": citations,
                "document_count": len(documents),
            },
            reasoning=(
                f"Embedded the query plus evaluation/EDA hints with TF-IDF and retrieved "
                f"{len(documents)} documents by cosine similarity (threshold 0.01)."
            ),
        )
