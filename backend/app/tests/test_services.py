"""Tests for the core Iris service layer."""

import pytest
from app.services.iris_service import (
    df,
    model,
    scaler,
    iris,
    vector_store,
    KNOWLEDGE_DOCS,
    TOOL_SCHEMAS,
    TOOL_MAP,
    _predict_species,
    _get_species_stats,
    _filter_flowers,
    _compare_species,
    _retrieve_knowledge,
    _get_all_species,
    _extract_numbers,
    _extract_species,
    _decide_tools,
    _exec_tool,
    function_call_processor,
    combined_tools_processor,
    VectorStore,
)


class TestDataLoading:
    def test_dataset_loaded(self):
        assert len(df) == 150
        assert list(df.columns) == [
            "sepal length (cm)",
            "sepal width (cm)",
            "petal length (cm)",
            "petal width (cm)",
            "species",
        ]

    def test_species_distribution(self):
        counts = df["species"].value_counts()
        for s in iris.target_names:
            assert counts[s] == 50

    def test_model_accuracy(self):
        """RandomForest should have near-perfect accuracy on the training data."""
        X_scaled = scaler.transform(iris.data)
        preds = model.predict(X_scaled)
        acc = (preds == iris.target).mean()
        assert acc >= 0.95


class TestVectorStore:
    def test_initialization(self):
        assert len(vector_store.documents) == 6
        assert vector_store.doc_vectors.shape[0] == 6

    def test_search_returns_results(self):
        results = vector_store.search("setosa flower characteristics", top_k=2)
        assert len(results) >= 1
        assert results[0]["score"] > 0.0
        assert "doc_id" in results[0]

    def test_search_all_top_k(self):
        results = vector_store.search("iris", top_k=6)
        # May return fewer than 6 if some docs score below the 0.01 threshold
        assert len(results) >= 4

    def test_search_irrelevant_query(self):
        results = vector_store.search("zzzxyqwrt not in any document", top_k=3)
        # Should return empty or very low score results filtered out
        assert all(r["score"] <= 0.05 for r in results) if results else True

    def test_custom_vector_store(self):
        docs = [{"doc_id": "a", "title": "A", "content": "hello world"}]
        vs = VectorStore(docs)
        results = vs.search("hello")
        assert len(results) == 1
        assert results[0]["doc_id"] == "a"


class TestTools:
    def test_predict_species(self):
        result = _predict_species(5.1, 3.5, 1.4, 0.2)
        assert result["predicted_species"] == "setosa"
        assert result["confidence"] > 50

    def test_predict_versicolor(self):
        result = _predict_species(5.9, 2.8, 4.2, 1.3)
        species = result["predicted_species"]
        assert species in ["versicolor", "virginica"]

    def test_get_species_stats(self):
        result = _get_species_stats("setosa")
        assert result["sample_count"] == 50
        assert "statistics" in result
        stats = result["statistics"]["sepal length (cm)"]
        assert 4.0 < stats["mean"] < 6.0

    def test_get_species_stats_invalid(self):
        result = _get_species_stats("nonexistent")
        assert "error" in result

    def test_filter_flowers(self):
        result = _filter_flowers(species="setosa")
        assert result["count"] == 50

    def test_filter_flowers_range(self):
        result = _filter_flowers(feature="petal length (cm)", min_val=3.0, max_val=6.0)
        assert result["count"] > 0

    def test_compare_species(self):
        result = _compare_species("setosa", "virginica")
        assert result["species1"]["name"] == "setosa"
        assert result["species2"]["name"] == "virginica"
        assert "comparison" in result

    def test_compare_species_invalid(self):
        result = _compare_species("setosa", "nope")
        assert "error" in result

    def test_retrieve_knowledge(self):
        result = _retrieve_knowledge("classification guide")
        assert result["results_count"] >= 1
        assert result["results"][0]["score"] > 0.0

    def test_get_all_species(self):
        result = _get_all_species()
        assert len(result["species_list"]) == 3
        names = [s["species"] for s in result["species_list"]]
        assert "setosa" in names

    def test_all_tools_registered(self):
        for schema in TOOL_SCHEMAS:
            assert schema["name"] in TOOL_MAP


class TestQueryParsing:
    def test_extract_numbers(self):
        assert _extract_numbers("5.1 3.5 1.4 0.2") == [5.1, 3.5, 1.4, 0.2]
        assert _extract_numbers("no numbers") == []

    def test_extract_species(self):
        assert "setosa" in _extract_species("tell me about setosa")
        assert "versicolor" in _extract_species("versicolor stats")

    def test_decide_tools_predict(self):
        tools = _decide_tools("predict species from 5.1 3.5 1.4 0.2")
        assert "predict_species" in tools

    def test_decide_tools_compare(self):
        tools = _decide_tools("compare setosa vs versicolor")
        assert "compare_species" in tools

    def test_decide_tools_all(self):
        tools = _decide_tools("list all species")
        assert "get_all_species" in tools

    def test_decide_tools_fallback(self):
        tools = _decide_tools("xyzxyz")
        assert "retrieve_knowledge" in tools

    def test_exec_tool_predict(self):
        result = _exec_tool("predict_species", "predict 5.1 3.5 1.4 0.2")
        assert result["tool"] == "predict_species"
        assert result["result"]["predicted_species"] == "setosa"


class TestFunctionCallProcessor:
    def test_basic_query(self):
        result = function_call_processor.process(
            "predict species for 5.1 3.5 1.4 0.2"
        )
        assert result["approach"] == "function_call"
        assert len(result["tools_called"]) == 1
        assert result["rag_used"] is False

    def test_stats_query(self):
        result = function_call_processor.process("stats for setosa")
        assert result["approach"] == "function_call"
        assert "tools_called" in result


class TestCombinedToolsProcessor:
    def test_basic_query(self):
        result = combined_tools_processor.process(
            "tell me about setosa and its statistics"
        )
        assert result["approach"] == "combined_tools"
        assert result["rag_used"] is True
        assert len(result["knowledge"]) >= 1
        assert len(result["results"]) >= 1
        assert len(result["synthesis"]) > 0

    def test_compare_query(self):
        result = combined_tools_processor.process(
            "compare setosa and versicolor"
        )
        assert len(result["knowledge"]) >= 1
        assert len(result["results"]) >= 1
        assert "synthesis" in result

    def test_fallback_query(self):
        result = combined_tools_processor.process("iris classification")
        assert result["rag_used"] is True
        assert len(result["knowledge"]) >= 1
        assert len(result["results"]) >= 1
