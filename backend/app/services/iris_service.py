"""
Iris RAG core service — dataset loading and the TF-IDF vector store
used by the RAG knowledge agent.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════

iris = load_iris()
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)

X = iris.data
y = iris.target

logger.info("Iris dataset loaded: %d samples, %d features", len(df), len(iris.feature_names))


# ══════════════════════════════════════════════════════════════════════
# Knowledge base (RAG documents)
# ══════════════════════════════════════════════════════════════════════

KNOWLEDGE_DOCS: list[dict[str, str]] = [
    {
        "doc_id": "setosa_overview",
        "title": "Iris Setosa — Species Overview",
        "content": (
            "Iris setosa is one of three Iris species in Fisher's 1936 dataset. "
            "It is the most easily distinguishable species due to its small petal size. "
            "Setosa typically has petals less than 2 cm long and less than 0.8 cm wide. "
            "Sepal length averages 5.0 cm with sepal width around 3.4 cm. "
            "It is native to Alaska, Canada, and northeastern Asia."
        ),
        "category": "species",
    },
    {
        "doc_id": "versicolor_overview",
        "title": "Iris Versicolor — Species Overview",
        "content": (
            "Iris versicolor is a medium-sized Iris species found throughout eastern North America. "
            "Petals typically range from 3.0-5.1 cm in length and 1.0-1.8 cm in width. "
            "Sepal length averages 5.9 cm and sepal width averages 2.8 cm. "
            "It has distinctive blue to purple flowers and is commonly known as the blue flag iris."
        ),
        "category": "species",
    },
    {
        "doc_id": "virginica_overview",
        "title": "Iris Virginica — Species Overview",
        "content": (
            "Iris virginica is the largest of the three species in the dataset. "
            "Petals average 5.5 cm in length and 2.0 cm in width — much larger than the other two. "
            "Sepal length averages 6.6 cm with sepal width around 3.0 cm. "
            "It is found across the southeastern United States in wetlands and along streams."
        ),
        "category": "species",
    },
    {
        "doc_id": "classification_guide",
        "title": "Iris Classification Rules of Thumb",
        "content": (
            "Petiole width (petal_width) is the single best feature for classification. "
            "If petal width < 0.8 cm, the flower is almost certainly setosa. "
            "If petal width is between 1.0-1.7 cm, it is likely versicolor. "
            "If petal width > 1.7 cm, it is likely virginica. "
            "Petal length is the second most discriminative feature. "
            "Sepal measurements alone are not reliable for classification."
        ),
        "category": "guide",
    },
    {
        "doc_id": "measurement_guide",
        "title": "Understanding Iris Measurements",
        "content": (
            "Each Iris flower is characterized by four measurements in centimeters: "
            "sepal length, sepal width, petal length, and petal width. "
            "Sepals are the outer, typically green leaf-like structures that protect the flower bud. "
            "Petals are the inner, usually colorful structures. "
            "For Iris flowers, there are 3 petals and 3 sepals per flower — "
            "but the dataset uses an average of each from 50 samples per species. "
            "Measurements range from 4.3-7.9 cm for sepals and 0.1-2.5 cm for petal width."
        ),
        "category": "guide",
    },
    {
        "doc_id": "habitat_guide",
        "title": "Iris Species Habitats and Growing Conditions",
        "content": (
            "Iris setosa thrives in cooler northern climates and can tolerate partial shade. "
            "Iris versicolor prefers moist, acidic soils along pond edges and marshes. "
            "Iris virginica requires full sun and rich, consistently moist soil. "
            "All three species are perennials and bloom in late spring to early summer. "
            "The Gaspé Peninsula in Quebec is noted as having all three species in close proximity."
        ),
        "category": "guide",
    },
]

# ══════════════════════════════════════════════════════════════════════
# Vector store
# ══════════════════════════════════════════════════════════════════════

class VectorStore:
    """In-memory TF-IDF vector store with cosine similarity search."""

    def __init__(self, documents: list[dict[str, str]]):
        self.documents = documents
        self.docs_content = [d["content"] for d in documents]
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        self.doc_vectors = self.vectorizer.fit_transform(self.docs_content)

    def search(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        query_vec = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vec, self.doc_vectors).flatten()
        ranked_indices = np.argsort(similarities)[::-1]

        results: list[dict[str, Any]] = []
        for idx in ranked_indices[:top_k]:
            score = float(similarities[idx])
            if score <= 0.01:
                continue
            doc = self.documents[idx]
            results.append({
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "content": doc["content"],
                "score": round(score, 4),
            })
        return results


vector_store = VectorStore(KNOWLEDGE_DOCS)


def rebuild_vector_store(documents: list[dict[str, str]]) -> VectorStore:
    """Replace the module-level vector store so retrieval reflects DB-backed docs."""
    global vector_store
    if documents:
        vector_store = VectorStore(documents)
    return vector_store
