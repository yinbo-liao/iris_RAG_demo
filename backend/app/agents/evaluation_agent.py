"""Evaluation Agent — compares metrics only; it never trains or mutates models."""

from __future__ import annotations

from typing import Any

from app.agents.base import AgentResult, BaseAgent

# F1 leads because the classes are balanced but per-class errors still matter.
METRIC_WEIGHTS = {"f1": 0.5, "accuracy": 0.3, "precision": 0.1, "recall": 0.1}


def _weighted_score(metrics: dict[str, float]) -> float:
    return round(sum(metrics.get(metric, 0.0) * weight for metric, weight in METRIC_WEIGHTS.items()), 4)


class EvaluationAgent(BaseAgent):
    name = "Evaluation Agent"
    role = "Rank classifier results objectively and explain tradeoffs without retraining."
    suggested_model = "GPT-4o-mini / Claude Sonnet"
    permissions = ("read:model_metrics", "write:ranking_report")
    allowed_inputs = ("model_results",)

    def run(self, context: dict[str, Any]) -> AgentResult:
        model_results = context.get("model_results") or []
        if not model_results:
            return AgentResult(
                output={
                    "ranking": [],
                    "ranked_models": [],
                    "best_model": None,
                    "reason": "No model results were provided; nothing to evaluate.",
                    "tradeoffs": [],
                },
                reasoning="Evaluation aborted: empty model_results input.",
            )

        scored = []
        for result in model_results:
            metrics = result.get("metrics", {})
            scored.append({
                "model": result.get("model", "unknown"),
                "accuracy": metrics.get("accuracy", 0.0),
                "precision": metrics.get("precision", 0.0),
                "recall": metrics.get("recall", 0.0),
                "f1": metrics.get("f1", 0.0),
                "cv_f1_macro": (result.get("cv_f1_macro") or {}).get("mean"),
                "score": _weighted_score(metrics),
            })

        scored.sort(key=lambda item: (item["score"], item["f1"], item["accuracy"]), reverse=True)

        ranking = [item["model"] for item in scored]
        best = scored[0]
        runner_up = scored[1] if len(scored) > 1 else None
        margin = round(best["score"] - runner_up["score"], 4) if runner_up else None

        reason = f"{best['model']} ranks first with weighted score {best['score']:.4f}"
        if runner_up:
            reason += f", {margin:.4f} ahead of {runner_up['model']}"
        reason += " (F1 weighted most heavily)."

        tradeoffs: list[str] = []
        if runner_up:
            for metric in ("accuracy", "precision", "recall", "f1"):
                if runner_up[metric] > best[metric]:
                    tradeoffs.append(
                        f"{runner_up['model']} beats {best['model']} on {metric} "
                        f"({runner_up[metric]:.4f} vs {best[metric]:.4f})."
                    )
            if margin is not None and margin < 0.01:
                tradeoffs.append("The top two models are within 0.01 weighted score — treat the choice as a tie.")
            cv_best = best.get("cv_f1_macro")
            cv_runner = runner_up.get("cv_f1_macro")
            if cv_best is not None and cv_runner is not None and cv_runner > cv_best:
                tradeoffs.append(
                    f"{runner_up['model']} has higher cross-validated F1 ({cv_runner:.4f} vs {cv_best:.4f}), "
                    "suggesting better stability."
                )
        if not tradeoffs:
            tradeoffs.append("The winning model leads on every reported metric; no metric-level tradeoff was found.")

        return AgentResult(
            output={
                "ranking": ranking,
                "ranked_models": scored,
                "best_model": best["model"],
                "best_score": best["score"],
                "margin_over_runner_up": margin,
                "metric_weights": METRIC_WEIGHTS,
                "reason": reason,
                "tradeoffs": tradeoffs,
            },
            reasoning=(
                f"Read metrics for {len(scored)} models and ranked by a fixed weighted score. "
                "No training code runs in this agent."
            ),
        )
