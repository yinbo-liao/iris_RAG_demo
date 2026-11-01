"""Tests for the API endpoints."""

from app.models.models import PredictionLog


def _add_log(db_session, query_text, approach="multi_agent", rag_used="yes"):
    """Insert a prediction log directly, without going through an endpoint."""
    log = PredictionLog(
        approach=approach,
        query_text=query_text,
        tools_called=["Main Orchestrator Agent"],
        result_data={"query": query_text},
        rag_used=rag_used,
    )
    db_session.add(log)
    db_session.commit()
    return log


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestKnowledgeEndpoint:
    def test_list_knowledge_from_memory(self, client):
        resp = client.get("/api/knowledge")
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) == 6

    def test_list_knowledge_from_db(self, client, seeded_session):
        resp = client.get("/api/knowledge")
        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) == 6
        categories = {d["category"] for d in docs}
        assert "species" in categories


class TestStatsEndpoint:
    def test_get_stats(self, client):
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_samples"] == 150
        assert len(data["species_distribution"]) == 3

    def test_species_distribution_sum(self, client):
        resp = client.get("/api/stats")
        data = resp.json()
        total = sum(s["count"] for s in data["species_distribution"])
        assert total == 150


class TestSeedEndpoint:
    def test_seed(self, client, db_session):
        resp = client.post("/api/seed")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 6

    def test_seed_idempotent(self, client, db_session):
        client.post("/api/seed")
        resp = client.post("/api/seed")
        data = resp.json()
        assert data["count"] == 6  # no duplicates
        assert "already seeded" in data["message"].lower()


class TestHistoryEndpoint:
    def test_history_empty(self, client, db_session):
        resp = client.get("/api/history")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_history_with_data(self, client, db_session):
        _add_log(db_session, "test query one")
        _add_log(db_session, "test query two")

        resp = client.get("/api/history?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        query_texts = {e["query_text"] for e in data}
        assert "test query one" in query_texts
        assert "test query two" in query_texts

    def test_history_preserves_legacy_approaches(self, client, db_session):
        # Rows written before the Query/Compare demo was removed are still shown.
        _add_log(db_session, "legacy function query", approach="function_call", rag_used="no")
        _add_log(db_session, "legacy combined query", approach="combined_tools")

        data = client.get("/api/history?limit=10").json()
        by_query = {e["query_text"]: e for e in data}
        assert by_query["legacy function query"]["approach"] == "function_call"
        assert by_query["legacy function query"]["rag_used"] == "no"
        assert by_query["legacy combined query"]["approach"] == "combined_tools"
        assert by_query["legacy combined query"]["rag_used"] == "yes"

    def test_history_limit(self, client, db_session):
        for i in range(5):
            _add_log(db_session, f"query {i}")

        resp = client.get("/api/history?limit=2")
        assert len(resp.json()) == 2

    def test_clear_history(self, client, db_session):
        _add_log(db_session, "delete me")

        resp = client.delete("/api/history")
        assert resp.status_code == 200
        assert resp.json()["deleted"] >= 1
        assert client.get("/api/history").json() == []


class TestRemovedEndpoints:
    def test_query_endpoint_is_gone(self, client):
        resp = client.post("/api/query", json={"query": "test", "approach": "function_call"})
        assert resp.status_code == 404

    def test_compare_endpoint_is_gone(self, client):
        assert client.get("/api/compare", params={"query": "test"}).status_code == 404

    def test_tools_endpoint_is_gone(self, client):
        assert client.get("/api/tools").status_code == 404
