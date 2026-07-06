"""Tests for the API endpoints."""

import pytest


class TestHealthEndpoint:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestToolsEndpoint:
    def test_list_tools(self, client):
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        tools = resp.json()
        assert len(tools) == 6
        names = [t["name"] for t in tools]
        assert "predict_species" in names


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
        assert data["tools_count"] == 6

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


class TestQueryEndpoint:
    def test_function_call(self, client, db_session):
        resp = client.post("/api/query", json={
            "query": "predict species for 5.1 3.5 1.4 0.2",
            "approach": "function_call",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["approach"] == "function_call"
        assert data["rag_used"] is False
        assert len(data["tools_called"]) == 1

    def test_combined_tools(self, client, db_session):
        resp = client.post("/api/query", json={
            "query": "tell me about setosa",
            "approach": "combined_tools",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["approach"] == "combined_tools"
        assert data["rag_used"] is True
        assert len(data["knowledge"]) >= 1

    def test_empty_query_rejected(self, client):
        resp = client.post("/api/query", json={
            "query": "",
            "approach": "function_call",
        })
        assert resp.status_code == 422

    def test_invalid_approach_rejected(self, client):
        resp = client.post("/api/query", json={
            "query": "test",
            "approach": "invalid",
        })
        assert resp.status_code == 422

    def test_logs_to_db(self, client, db_session):
        client.post("/api/query", json={
            "query": "stats for setosa",
            "approach": "function_call",
        })
        from app.models.models import PredictionLog
        log = db_session.query(PredictionLog).first()
        assert log is not None
        assert log.approach == "function_call"


class TestCompareEndpoint:
    def test_compare(self, client, db_session):
        resp = client.get("/api/compare?query=predict%205.1%203.5%201.4%200.2")
        assert resp.status_code == 200
        data = resp.json()
        assert "function_call" in data
        assert "combined_tools" in data
        assert data["function_call"]["rag_used"] is False
        assert data["combined_tools"]["rag_used"] is True

    def test_compare_missing_query(self, client):
        resp = client.get("/api/compare")
        assert resp.status_code == 422


class TestHistoryEndpoint:
    def test_history_empty(self, client, db_session):
        resp = client.get("/api/history")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_history_with_data(self, client, db_session):
        client.post("/api/query", json={
            "query": "test query one",
            "approach": "function_call",
        })
        client.post("/api/query", json={
            "query": "test query two",
            "approach": "combined_tools",
        })
        resp = client.get("/api/history?limit=10")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        query_texts = {e["query_text"] for e in data}
        assert "test query one" in query_texts
        assert "test query two" in query_texts

    def test_history_limit(self, client, db_session):
        for i in range(5):
            client.post("/api/query", json={
                "query": f"query {i}",
                "approach": "function_call",
            })
        resp = client.get("/api/history?limit=2")
        assert len(resp.json()) == 2
