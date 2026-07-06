"""Tests for SQLAlchemy ORM models."""

import json
from app.models.models import PredictionLog, KnowledgeDoc, IrisSample


class TestPredictionLog:
    def test_create_log(self, db_session):
        log = PredictionLog(
            approach="function_call",
            query_text="predict setosa",
            tools_called=["predict_species"],
            result_data={"foo": "bar"},
            rag_used="no",
            confidence=95.5,
        )
        db_session.add(log)
        db_session.commit()

        fetched = db_session.query(PredictionLog).first()
        assert fetched is not None
        assert fetched.approach == "function_call"
        assert fetched.query_text == "predict setosa"
        assert fetched.tools_called == ["predict_species"]
        assert fetched.result_data == {"foo": "bar"}
        assert fetched.rag_used == "no"
        assert fetched.confidence == 95.5

    def test_json_columns_round_trip(self, db_session):
        """JSON columns should serialize/deserialize correctly."""
        log = PredictionLog(
            approach="combined_tools",
            query_text="tell me about setosa",
            tools_called=["retrieve_knowledge", "get_species_stats"],
            result_data={"nested": [1, 2, 3], "deep": {"key": "val"}},
            rag_used="yes",
        )
        db_session.add(log)
        db_session.commit()

        fetched = db_session.query(PredictionLog).first()
        assert len(fetched.tools_called) == 2
        assert fetched.result_data["deep"]["key"] == "val"

    def test_auto_timestamp(self, db_session):
        log = PredictionLog(approach="function_call", query_text="test", tools_called=[], result_data={})
        db_session.add(log)
        db_session.commit()
        assert log.created_at is not None


class TestKnowledgeDoc:
    def test_create_doc(self, db_session):
        doc = KnowledgeDoc(
            doc_id="test_doc",
            title="Test Title",
            content="Test content here.",
            category="test",
        )
        db_session.add(doc)
        db_session.commit()

        fetched = db_session.query(KnowledgeDoc).first()
        assert fetched.doc_id == "test_doc"
        assert fetched.title == "Test Title"
        assert fetched.category == "test"

    def test_unique_doc_id(self, db_session):
        db_session.add(KnowledgeDoc(doc_id="uniq", title="A", content="x", category="c"))
        db_session.commit()
        db_session.add(KnowledgeDoc(doc_id="uniq", title="B", content="y", category="c"))
        from sqlalchemy.exc import IntegrityError
        import pytest
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestIrisSample:
    def test_create_sample(self, db_session):
        sample = IrisSample(
            sepal_length=5.1, sepal_width=3.5,
            petal_length=1.4, petal_width=0.2,
            species="setosa", source="original",
        )
        db_session.add(sample)
        db_session.commit()

        fetched = db_session.query(IrisSample).first()
        assert fetched.species == "setosa"
        assert fetched.sepal_length == 5.1
        assert fetched.source == "original"
