from sqlalchemy import Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.models import Base


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)
    approach = Column(String(50), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    tools_called = Column(JSON, nullable=False, default=list)
    result_data = Column(JSON, nullable=False, default=dict)
    rag_used = Column(String(10), nullable=False, default="no")
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeDoc(Base):
    __tablename__ = "knowledge_docs"

    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class IrisSample(Base):
    __tablename__ = "iris_samples"

    id = Column(Integer, primary_key=True, index=True)
    sepal_length = Column(Float, nullable=False)
    sepal_width = Column(Float, nullable=False)
    petal_length = Column(Float, nullable=False)
    petal_width = Column(Float, nullable=False)
    species = Column(String(50), nullable=False, index=True)
    source = Column(String(50), nullable=False, default="original")
