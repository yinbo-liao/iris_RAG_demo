"""Main Orchestrator Agent — decomposes, delegates, collects, and synthesizes."""

from __future__ import annotations

import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.agents.base import AgentRun, BaseAgent
from app.agents.data_pattern_agent import DataPatternAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.model_agents import RandomForestAgent, SVMAgent, XGBoostAgent
from app.agents.rag_agent import RAGKnowledgeAgent

PLAN_STEPS = [
    "Decompose the user request into analysis, modeling, evaluation, and explanation tasks.",
    "Dispatch the Data Pattern Analysis Agent for dataset EDA.",
    "Train Random Forest, SVM, and XGBoost candidate classifiers in parallel.",
    "Send the metric report to the Evaluation Agent for objective ranking.",
    "Retrieve supporting botanical and ML knowledge with the RAG Knowledge Agent.",
    "Synthesize the executive report and recommendations.",
]


def _label(item: dict[str, Any] | None) -> str:
    """Report-facing model name; falls back to the raw name for older payloads."""
    if not item:
        return "unknown"
    return item.get("display_name") or item.get("model") or "unknown"


def _build_final_report(
    query: str,
    pattern: dict[str, Any],
    evaluation: dict[str, Any],
    knowledge: dict[str, Any],
) -> dict[str, Any]:
    ranked = evaluation.get("ranked_models") or []
    best = ranked[0] if ranked else None
    runner_up = ranked[1] if len(ranked) > 1 else None
    findings = pattern.get("findings") or []
    citations = knowledge.get("citations") or []

    if best:
        headline = f"Recommended classifier: {_label(best)}"
        summary = (
            f"For \"{query}\", three classifiers were trained and compared. "
            f"{_label(best)} ranked first with accuracy {best['accuracy']:.3f}, "
            f"macro F1 {best['f1']:.3f}, precision {best['precision']:.3f}, and recall {best['recall']:.3f}"
        )
        if runner_up:
            summary += f", ahead of {_label(runner_up)} (F1 {runner_up['f1']:.3f})"
        summary += ". " + (findings[0] if findings else "")
    else:
        headline = "No model could be evaluated"
        summary = "All candidate model agents failed; inspect the agent audit trail for errors."

    margin = evaluation.get("margin_over_runner_up")
    best_f1 = best["f1"] if best else 0.0
    if best and best_f1 >= 0.95 and (margin is None or margin >= 0.01):
        confidence = "high"
    elif best and best_f1 >= 0.90:
        confidence = "medium"
    else:
        confidence = "low"

    recommendations = []
    if best:
        recommendations.append(
            f"Adopt {_label(best)} as the primary classifier; it leads the weighted ranking "
            f"(score {best['score']:.4f})."
        )
    if pattern:
        ranked_features = pattern.get("ranked_features") or []
        if ranked_features:
            recommendations.append(
                f"Prioritize {ranked_features[0]} in feature collection and monitoring; "
                "it has the strongest class separation."
            )
        separability = pattern.get("separability", {})
        if separability.get("overlapping_samples"):
            recommendations.append(
                "Expect residual errors between versicolor and virginica: petal width overlaps "
                f"between {separability['versicolor_virginica_overlap_range'][0]} and "
                f"{separability['versicolor_virginica_overlap_range'][1]} cm."
            )
    if runner_up and margin is not None and margin < 0.01:
        recommendations.append(
            f"Keep {_label(runner_up)} as a challenger; the gap to the leader is under 0.01."
        )
    recommendations.append("Continue using stratified cross-validation when the dataset grows.")

    return {
        "headline": headline,
        "summary": summary,
        "confidence": confidence,
        "recommendations": recommendations,
        "evidence": {
            "best_metrics": best,
            "runner_up": runner_up,
            "pattern_findings": findings,
            "citations": citations,
        },
    }


class MainOrchestratorAgent(BaseAgent):
    name = "Main Orchestrator Agent"
    role = "Decompose requests, delegate to specialists, collect results, and write the final report."
    suggested_model = "GPT-5 / GPT-4o / Claude Sonnet"
    permissions = ("read:user_request", "invoke:subagents", "read:subagent_outputs", "write:final_report")
    allowed_inputs = ("query",)

    def __init__(self) -> None:
        self.data_agent = DataPatternAgent()
        self.model_agents = [RandomForestAgent(), SVMAgent(), XGBoostAgent()]
        self.evaluation_agent = EvaluationAgent()
        self.rag_agent = RAGKnowledgeAgent()

    def specialist_agents(self) -> list[BaseAgent]:
        return [self.data_agent, *self.model_agents, self.evaluation_agent, self.rag_agent]

    def registry(self) -> list[dict[str, Any]]:
        return [self.definition(), *[agent.definition() for agent in self.specialist_agents()]]

    def analyze(self, query: str) -> dict[str, Any]:
        started = time.perf_counter()
        query = query.strip()

        # 1) EDA + model training run in parallel (independent tasks).
        parallel_agents: list[BaseAgent] = [self.data_agent, *self.model_agents]
        with ThreadPoolExecutor(max_workers=len(parallel_agents)) as pool:
            futures = [pool.submit(agent.execute, {"query": query}) for agent in parallel_agents]
            parallel_runs: list[AgentRun] = [future.result() for future in futures]

        pattern_run = parallel_runs[0]
        model_runs = parallel_runs[1:]
        pattern_output = pattern_run.output if pattern_run.status == "success" else {}
        model_results = [
            run.output for run in model_runs
            if run.status == "success" and "metrics" in run.output
        ]

        # 2) Evaluation reads only the metrics.
        evaluation_run = self.evaluation_agent.execute({"model_results": model_results})
        evaluation_output = evaluation_run.output if evaluation_run.status == "success" else {}

        # 3) RAG reads the query plus prior analysis (never raw training data).
        rag_run = self.rag_agent.execute({
            "query": query,
            "evaluation": evaluation_output,
            "pattern_analysis": pattern_output,
        })
        rag_output = rag_run.output if rag_run.status == "success" else {}

        # 4) Synthesize.
        final_report = _build_final_report(query, pattern_output, evaluation_output, rag_output)

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        orchestrator_run = self._record(
            status="success",
            output={},
            reasoning=(
                f"Decomposed the request into {len(PLAN_STEPS)} steps, ran "
                f"{len(parallel_agents)} agents in parallel, then evaluated and synthesized."
            ),
            duration_ms=duration_ms,
        )

        agent_runs = [*parallel_runs, evaluation_run, rag_run, orchestrator_run]
        return {
            "run_id": uuid.uuid4().hex,
            "query": query,
            "plan": PLAN_STEPS,
            "agents": [run.to_dict() for run in agent_runs],
            "agent_count": len(agent_runs),
            "pattern_analysis": pattern_output,
            "model_results": model_results,
            "evaluation": evaluation_output,
            "knowledge": rag_output.get("documents", []),
            "citations": rag_output.get("citations", []),
            "final_report": final_report,
            "duration_ms": duration_ms,
        }


orchestrator = MainOrchestratorAgent()
