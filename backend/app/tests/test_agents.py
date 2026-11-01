"""Tests for the multi-agent analytics system."""

import pytest

from app.agents.base import AgentResult, BaseAgent
from app.agents.data_pattern_agent import DataPatternAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.model_agents import RandomForestAgent, SVMAgent, XGBoostAgent
from app.agents.orchestrator import MainOrchestratorAgent, orchestrator
from app.agents.rag_agent import RAGKnowledgeAgent
from app.models.models import PredictionLog


class TestLeastPrivilege:
    def test_agent_only_receives_allowed_inputs(self):
        class SpyAgent(BaseAgent):
            allowed_inputs = ("allowed",)

            def run(self, context):
                return AgentResult(output={"seen_keys": sorted(context.keys())})

        run = SpyAgent().execute({"allowed": 1, "secret": 2, "model_results": []})
        assert run.output["seen_keys"] == ["allowed"]
        assert run.status == "success"

    def test_failed_agent_is_recorded_not_raised(self):
        class BrokenAgent(BaseAgent):
            def run(self, context):
                raise RuntimeError("boom")

        run = BrokenAgent().execute({})
        assert run.status == "error"
        assert run.error == "boom"
        assert "boom" in run.reasoning


class TestDataPatternAgent:
    def test_eda_output_contract(self):
        run = DataPatternAgent().execute({"query": "explore"})
        assert run.status == "success"
        out = run.output
        assert out["sample_count"] == 150
        assert out["feature_count"] == 4
        assert len(out["class_distribution"]) == 3
        assert all(item["count"] == 50 for item in out["class_distribution"])
        assert set(out["feature_stats"]) == {
            "sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"
        }
        assert len(out["findings"]) >= 3
        assert out["ranked_features"][0] == max(out["fisher_scores"], key=out["fisher_scores"].get)

    def test_separability_metrics(self):
        out = DataPatternAgent().execute({"query": "explore"}).output
        assert out["separability"]["setosa_vs_rest_accuracy"] > 0.95
        low, high = out["separability"]["versicolor_virginica_overlap_range"]
        assert low < high

    def test_eda_never_trains_a_model(self):
        out = DataPatternAgent().execute({"query": "explore"}).output
        assert "metrics" not in out
        assert "confusion_matrix" not in out


class TestModelAgents:
    @pytest.mark.parametrize(
        "agent,expected_name",
        [(RandomForestAgent(), "Random Forest"), (SVMAgent(), "SVM"), (XGBoostAgent(), "XGBoost")],
    )
    def test_metric_contract(self, agent, expected_name):
        run = agent.execute({"query": "train"})
        assert run.status == "success", run.error
        out = run.output
        assert out["model"] == expected_name
        assert out["split"] == {"train": 112, "test": 38}
        for metric in ("accuracy", "precision", "recall", "f1"):
            value = out["metrics"][metric]
            assert 0.0 <= value <= 1.0
        assert out["metrics"]["f1"] > 0.85
        assert len(out["confusion_matrix"]) == 3
        assert sum(sum(row) for row in out["confusion_matrix"]) == 38
        assert set(out["per_class"]) == {"setosa", "versicolor", "virginica"}
        assert set(out["cv_f1_macro"]) == {"mean", "std", "folds"}

    def test_xgboost_declares_its_engine(self):
        out = XGBoostAgent().execute({"query": "train"}).output
        assert "xgboost" in out["engine"].lower() or "gradientboosting" in out["engine"].lower()

    def test_agents_do_not_read_evaluation_results(self):
        assert "model_results" not in RandomForestAgent().allowed_inputs


class TestEvaluationAgent:
    RESULTS = [
        {"model": "A", "metrics": {"accuracy": 0.90, "precision": 0.90, "recall": 0.90, "f1": 0.90},
         "cv_f1_macro": {"mean": 0.90}},
        {"model": "B", "metrics": {"accuracy": 0.95, "precision": 0.95, "recall": 0.95, "f1": 0.95},
         "cv_f1_macro": {"mean": 0.94}},
        {"model": "C", "metrics": {"accuracy": 0.10, "precision": 0.10, "recall": 0.10, "f1": 0.10},
         "cv_f1_macro": {"mean": 0.10}},
    ]

    def test_ranking_order_and_best(self):
        out = EvaluationAgent().execute({"model_results": self.RESULTS}).output
        assert out["ranking"] == ["B", "A", "C"]
        assert out["best_model"] == "B"
        assert out["ranked_models"][0]["score"] > out["ranked_models"][1]["score"]
        assert out["margin_over_runner_up"] > 0

    def test_empty_results_are_safe(self):
        out = EvaluationAgent().execute({"model_results": []}).output
        assert out["ranking"] == []
        assert out["best_model"] is None

    def test_evaluation_ignores_extra_context(self):
        base = EvaluationAgent().execute({"model_results": self.RESULTS}).output
        noisy = EvaluationAgent().execute({"model_results": self.RESULTS, "metrics": {"f1": 1.0}}).output
        assert base["ranking"] == noisy["ranking"]


class TestRAGKnowledgeAgent:
    def test_retrieves_ranked_documents(self):
        out = RAGKnowledgeAgent().execute({"query": "petal width setosa"}).output
        assert out["document_count"] > 0
        assert out["document_count"] <= out["top_k"]
        scores = [doc["score"] for doc in out["documents"]]
        assert scores == sorted(scores, reverse=True)
        assert all(score > 0.01 for score in scores)
        assert out["citations"][0]["doc_id"] == out["documents"][0]["doc_id"]

    def test_uses_evaluation_to_enrich_query(self):
        out = RAGKnowledgeAgent().execute({
            "query": "explain",
            "evaluation": {"best_model": "SVM"},
        }).output
        assert "SVM" in out["retrieval_query"]


@pytest.fixture(scope="module")
def pipeline_result():
    return orchestrator.analyze("Analyze Iris dataset and recommend the best classifier.")


class TestOrchestrator:
    def test_all_seven_agents_succeed(self, pipeline_result):
        assert pipeline_result["agent_count"] == 7
        assert [run["status"] for run in pipeline_result["agents"]] == ["success"] * 7
        names = [run["agent"] for run in pipeline_result["agents"]]
        assert names == [
            "Data Pattern Analysis Agent",
            "Random Forest Agent",
            "SVM Agent",
            "XGBoost Agent",
            "Evaluation Agent",
            "RAG Knowledge Agent",
            "Main Orchestrator Agent",
        ]

    def test_plan_is_decomposed(self, pipeline_result):
        assert len(pipeline_result["plan"]) >= 5
        assert len(set(pipeline_result["plan"])) == len(pipeline_result["plan"])

    def test_model_results_match_ranking(self, pipeline_result):
        models = {m["model"] for m in pipeline_result["model_results"]}
        assert models == {"Random Forest", "SVM", "XGBoost"}
        ranking = pipeline_result["evaluation"]["ranking"]
        assert set(ranking) == models
        assert pipeline_result["evaluation"]["best_model"] == ranking[0]

    def test_final_report_is_complete(self, pipeline_result):
        report = pipeline_result["final_report"]
        assert report["headline"].startswith("Recommended classifier:")
        assert report["confidence"] in {"high", "medium", "low"}
        assert len(report["recommendations"]) >= 3
        assert report["evidence"]["best_metrics"]["model"] == pipeline_result["evaluation"]["best_model"]

    def test_knowledge_is_attached(self, pipeline_result):
        assert len(pipeline_result["knowledge"]) > 0
        assert len(pipeline_result["citations"]) == len(pipeline_result["knowledge"])

    def test_run_is_auditable(self, pipeline_result):
        for run in pipeline_result["agents"]:
            assert run["permissions"]
            assert run["reasoning"]
            assert run["duration_ms"] >= 0
            assert run["model"]
            assert run["suggested_model"]
        assert len(pipeline_result["run_id"]) == 32

    def test_registry_lists_roster_and_scopes(self):
        registry = MainOrchestratorAgent().registry()
        assert len(registry) == 7
        by_name = {entry["agent"]: entry for entry in registry}
        assert by_name["Evaluation Agent"]["allowed_inputs"] == ["model_results"]
        assert "train:own_classifier" in by_name["SVM Agent"]["permissions"]
        assert by_name["RAG Knowledge Agent"]["allowed_inputs"] != by_name["Random Forest Agent"]["allowed_inputs"]


class TestMultiAgentAPI:
    def test_registry_endpoint(self, client):
        resp = client.get("/api/agents/registry")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 7
        assert all("allowed_inputs" in entry for entry in data)

    def test_analyze_endpoint_returns_pipeline(self, client):
        resp = client.post("/api/agents/analyze", json={"query": "Which classifier is best?"})
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert data["agent_count"] == 7
        assert data["query"] == "Which classifier is best?"
        assert data["evaluation"]["best_model"] in {"Random Forest", "SVM", "XGBoost"}
        assert data["final_report"]["headline"]

    def test_analyze_persists_multi_agent_audit_log(self, client, db_session):
        resp = client.post("/api/agents/analyze", json={"query": "Recommend a classifier."})
        assert resp.status_code == 200
        logs = db_session.query(PredictionLog).filter(PredictionLog.approach == "multi_agent").all()
        assert logs
        log = logs[-1]
        assert log.query_text == "Recommend a classifier."
        assert "Main Orchestrator Agent" in log.tools_called
        assert log.rag_used == "yes"
        assert log.confidence == pytest.approx(log.result_data["evaluation"]["ranked_models"][0]["f1"])

    def test_empty_query_is_rejected(self, client):
        resp = client.post("/api/agents/analyze", json={"query": ""})
        assert resp.status_code == 422
