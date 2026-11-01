"""Tests for the core Iris service layer."""

from app.services.iris_service import (
    df,
    iris,
    vector_store,
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
