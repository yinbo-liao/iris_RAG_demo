"""
Iris RAG Core Service — data loading, model training, vector store,
tool registry, and both query-processing approaches.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════
# Data loading & model training
# ══════════════════════════════════════════════════════════════════════

iris = load_iris()
df = pd.DataFrame(data=iris.data, columns=iris.feature_names)
df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)

X = iris.data
y = iris.target

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_scaled, y)

logger.info("Iris dataset loaded: %d samples, %d features", len(df), len(iris.feature_names))
logger.info("RandomForest trained — classes: %s", iris.target_names.tolist())


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

# ══════════════════════════════════════════════════════════════════════
# Tool registry
# ══════════════════════════════════════════════════════════════════════

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "name": "predict_species",
        "description": "Predict the Iris species from four flower measurements using a trained RandomForest classifier.",
        "parameters": {
            "type": "object",
            "properties": {
                "sepal_length": {"type": "number", "description": "Sepal length in cm"},
                "sepal_width": {"type": "number", "description": "Sepal width in cm"},
                "petal_length": {"type": "number", "description": "Petal length in cm"},
                "petal_width": {"type": "number", "description": "Petal width in cm"},
            },
            "required": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
        },
    },
    {
        "name": "get_species_stats",
        "description": "Get statistical summary (mean, std, min, max, median) for a specific Iris species.",
        "parameters": {
            "type": "object",
            "properties": {
                "species": {
                    "type": "string",
                    "enum": ["setosa", "versicolor", "virginica"],
                    "description": "Species name to query",
                },
            },
            "required": ["species"],
        },
    },
    {
        "name": "filter_flowers",
        "description": "Filter Iris flowers by measurement ranges and/or species.",
        "parameters": {
            "type": "object",
            "properties": {
                "feature": {
                    "type": "string",
                    "enum": ["sepal_length", "sepal_width", "petal_length", "petal_width"],
                    "description": "Feature to filter on",
                },
                "min_val": {"type": "number", "description": "Minimum value"},
                "max_val": {"type": "number", "description": "Maximum value"},
                "species": {
                    "type": "string",
                    "enum": ["setosa", "versicolor", "virginica"],
                    "description": "Optional species filter",
                },
            },
            "required": [],
        },
    },
    {
        "name": "compare_species",
        "description": "Compare statistical differences between two Iris species side-by-side.",
        "parameters": {
            "type": "object",
            "properties": {
                "species1": {
                    "type": "string",
                    "enum": ["setosa", "versicolor", "virginica"],
                    "description": "First species",
                },
                "species2": {
                    "type": "string",
                    "enum": ["setosa", "versicolor", "virginica"],
                    "description": "Second species",
                },
            },
            "required": ["species1", "species2"],
        },
    },
    {
        "name": "retrieve_knowledge",
        "description": "Search the knowledge base using TF-IDF vector similarity for relevant Iris information.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for knowledge retrieval"},
                "top_k": {"type": "integer", "description": "Number of results (default 3)", "default": 3},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_all_species",
        "description": "Get a summary list of all three Iris species with sample counts and key measurements.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
]

# ══════════════════════════════════════════════════════════════════════
# Individual tool implementations
# ══════════════════════════════════════════════════════════════════════

def _predict_species(sepal_length: float, sepal_width: float, petal_length: float, petal_width: float) -> dict[str, Any]:
    sample = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    sample_scaled = scaler.transform(sample)
    pred_idx = int(model.predict(sample_scaled)[0])
    proba = model.predict_proba(sample_scaled)[0].tolist()
    confidence = round(float(max(proba)) * 100, 2)
    return {
        "predicted_species": iris.target_names[pred_idx],
        "confidence": confidence,
        "probabilities": {
            name: round(p * 100, 2)
            for name, p in zip(iris.target_names, proba)
        },
        "input_measurements": {
            "sepal_length": sepal_length,
            "sepal_width": sepal_width,
            "petal_length": petal_length,
            "petal_width": petal_width,
        },
    }


def _get_species_stats(species: str) -> dict[str, Any]:
    subset = df[df["species"] == species]
    if subset.empty:
        return {"error": f"Species '{species}' not found"}
    features = ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"]
    stats: dict[str, Any] = {}
    for f in features:
        col = subset[f]
        stats[f] = {
            "mean": round(float(col.mean()), 2),
            "std": round(float(col.std()), 2),
            "min": round(float(col.min()), 2),
            "max": round(float(col.max()), 2),
            "median": round(float(col.median()), 2),
        }
    return {"species": species, "sample_count": len(subset), "statistics": stats}


def _filter_flowers(
    feature: Optional[str] = None,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    species: Optional[str] = None,
) -> dict[str, Any]:
    filtered = df.copy()
    if species:
        filtered = filtered[filtered["species"] == species]
    if feature and min_val is not None:
        filtered = filtered[filtered[feature] >= min_val]
    if feature and max_val is not None:
        filtered = filtered[filtered[feature] <= max_val]
    return {
        "count": len(filtered),
        "samples": filtered.head(10).to_dict(orient="records"),
        "filters_applied": {
            "feature": feature,
            "min_val": min_val,
            "max_val": max_val,
            "species": species,
        },
    }


def _compare_species(species1: str, species2: str) -> dict[str, Any]:
    s1 = df[df["species"] == species1]
    s2 = df[df["species"] == species2]
    if s1.empty or s2.empty:
        return {"error": "One or both species not found"}
    features = ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"]
    comparison: dict[str, Any] = {}
    for f in features:
        comparison[f] = {
            species1: {"mean": round(float(s1[f].mean()), 2), "std": round(float(s1[f].std()), 2)},
            species2: {"mean": round(float(s2[f].mean()), 2), "std": round(float(s2[f].std()), 2)},
            "difference": round(float(s2[f].mean() - s1[f].mean()), 2),
        }
    return {
        "species1": {"name": species1, "count": len(s1)},
        "species2": {"name": species2, "count": len(s2)},
        "comparison": comparison,
    }


def _retrieve_knowledge(query: str, top_k: int = 3) -> dict[str, Any]:
    results = vector_store.search(query, top_k)
    return {"query": query, "results_count": len(results), "results": results}


def _get_all_species() -> dict[str, Any]:
    summaries = []
    for name in iris.target_names:
        subset = df[df["species"] == name]
        summaries.append({
            "species": name,
            "sample_count": len(subset),
            "avg_petal_length": round(float(subset["petal length (cm)"].mean()), 2),
            "avg_petal_width": round(float(subset["petal width (cm)"].mean()), 2),
        })
    return {"species_list": summaries}


TOOL_MAP = {
    "predict_species": _predict_species,
    "get_species_stats": _get_species_stats,
    "filter_flowers": _filter_flowers,
    "compare_species": _compare_species,
    "retrieve_knowledge": _retrieve_knowledge,
    "get_all_species": _get_all_species,
}

# ══════════════════════════════════════════════════════════════════════
# Query pattern matching
# ══════════════════════════════════════════════════════════════════════

_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(\d+\.?\d*)\s*[,;\s]+"), "predict_species"),
    (re.compile(r"\b(predict|classify|identify)\b", re.I), "predict_species"),
    (re.compile(r"\bstats?\b.*\b(setosa|versicolor|virginica)\b|\b(setosa|versicolor|virginica)\b.*\bstats?\b", re.I), "get_species_stats"),
    (re.compile(r"\b(compare|vs\.?|versus|difference)\b.*\b(setosa|versicolor|virginica)\b.*\b(setosa|versicolor|virginica)\b", re.I), "compare_species"),
    (re.compile(r"\b(filter|find|show)\b", re.I), "filter_flowers"),
    (re.compile(r"\b(all|list|every|summary)\b.*\bspecies\b|\bspecies\b.*\b(all|list|every|summary)\b", re.I), "get_all_species"),
]


def _extract_numbers(text: str) -> list[float]:
    """Extract floating-point numbers from text."""
    return [float(m) for m in re.findall(r"(\d+\.?\d*)", text)]


def _extract_species(text: str) -> list[str]:
    """Extract Iris species names from text."""
    found: list[str] = []
    for name in iris.target_names:
        if name in text.lower():
            found.append(name)
    return found


def _decide_tools(query: str) -> list[str]:
    """Return tool names matched by regex patterns."""
    matched: list[str] = []
    for pattern, tool_name in _PATTERNS:
        if pattern.search(query) and tool_name not in matched:
            matched.append(tool_name)
    if not matched:
        matched.append("retrieve_knowledge")
    return matched


def _exec_tool(name: str, query: str) -> dict[str, Any]:
    """Execute a single tool, extracting parameters from the query."""
    numbers = _extract_numbers(query)
    species_list = _extract_species(query)

    try:
        if name == "predict_species" and len(numbers) >= 4:
            return {"tool": name, "result": _predict_species(numbers[0], numbers[1], numbers[2], numbers[3])}
        if name == "get_species_stats" and species_list:
            return {"tool": name, "result": _get_species_stats(species_list[0])}
        if name == "compare_species" and len(species_list) >= 2:
            return {"tool": name, "result": _compare_species(species_list[0], species_list[1])}
        if name == "filter_flowers":
            kwargs: dict[str, Any] = {}
            if species_list:
                kwargs["species"] = species_list[0]
            if len(numbers) >= 2:
                kwargs["min_val"] = min(numbers[:2])
                kwargs["max_val"] = max(numbers[:2])
            return {"tool": name, "result": _filter_flowers(**kwargs) if kwargs else _filter_flowers()}
        if name == "get_all_species":
            return {"tool": name, "result": _get_all_species()}
        if name == "retrieve_knowledge":
            return {"tool": name, "result": _retrieve_knowledge(query)}
    except Exception as exc:
        logger.exception("Tool %s failed", name)
        return {"tool": name, "result": {"error": str(exc)}}

    return {"tool": name, "result": {"error": f"Insufficient parameters for {name}"}}


# ══════════════════════════════════════════════════════════════════════
# Processors
# ══════════════════════════════════════════════════════════════════════

class FunctionCallProcessor:
    """Process a query using a SINGLE function call (deterministic)."""

    def process(self, query: str) -> dict[str, Any]:
        tools = _decide_tools(query)
        primary = tools[0]
        result = _exec_tool(primary, query)

        return {
            "approach": "function_call",
            "approach_label": "Function Call",
            "tools_called": [primary],
            "rag_used": False,
            "result": result["result"],
            "explanation": f"Matched pattern → executed **{primary}** tool with parameters extracted from the query.",
            "query": query,
        }


class CombinedToolsProcessor:
    """Process a query using MULTIPLE tools + RAG + synthesis."""

    def process(self, query: str) -> dict[str, Any]:
        # 1) Always retrieve knowledge
        knowledge_results = vector_store.search(query, top_k=3)
        knowledge = [
            {"doc_id": r["doc_id"], "title": r["title"], "content": r["content"], "score": r["score"]}
            for r in knowledge_results
        ]

        # 2) Decide computation tools
        tool_names = _decide_tools(query)
        # Ensure we include relevant tools beyond the primary one
        if "retrieve_knowledge" in tool_names:
            tool_names.remove("retrieve_knowledge")
        if not tool_names:
            tool_names = ["get_all_species"]

        # 3) Execute all matched computation tools
        results = [_exec_tool(name, query) for name in tool_names]

        # 4) Synthesize
        synthesis = self._synthesize(query, knowledge, results, tool_names)

        return {
            "approach": "combined_tools",
            "approach_label": "Combined Tools (RAG + Functions)",
            "tools_called": tool_names,
            "rag_used": True,
            "results": results,
            "knowledge": knowledge,
            "synthesis": synthesis,
            "explanation": (
                f"Retrieved {len(knowledge)} knowledge documents, "
                f"executed {len(tool_names)} tool(s): {', '.join(tool_names)}, "
                f"and synthesized a comprehensive answer."
            ),
            "query": query,
        }

    def _synthesize(
        self,
        query: str,
        knowledge: list[dict[str, Any]],
        results: list[dict[str, Any]],
        tool_names: list[str],
    ) -> str:
        parts: list[str] = []

        if knowledge:
            parts.append("### 📚 Retrieved Knowledge\n")
            for k in knowledge:
                parts.append(f"- **{k['title']}** (relevance: {k['score']:.2f})\n  {k['content'][:200]}...\n")

        if results:
            parts.append("### 🔧 Tool Results\n")
            for r in results:
                tool = r["tool"]
                res = r.get("result", {})
                parts.append(f"**{tool}**: {self._summarise_result(tool, res)}\n")

        parts.insert(0, f"### 🤖 AI Synthesis for: \"{query}\"\n")
        parts.append(
            "\n---\n"
            "*This synthesis combines semantic knowledge retrieved from the vector store "
            "with computational results from multiple tools to provide a comprehensive answer.*"
        )
        return "\n".join(parts)

    @staticmethod
    def _summarise_result(tool: str, result: dict[str, Any]) -> str:
        if tool == "predict_species":
            pred = result.get("predicted_species", "?")
            conf = result.get("confidence", 0)
            return f"Predicted **{pred}** with {conf}% confidence."
        if tool == "get_species_stats":
            sp = result.get("species", "?")
            cnt = result.get("sample_count", 0)
            return f"Statistics for **{sp}** ({cnt} samples)."
        if tool == "compare_species":
            s1 = result.get("species1", {}).get("name", "?")
            s2 = result.get("species2", {}).get("name", "?")
            return f"Compared **{s1}** vs **{s2}** across 4 features."
        if tool == "filter_flowers":
            cnt = result.get("count", 0)
            return f"Found **{cnt}** matching flowers."
        if tool == "get_all_species":
            return f"Returned summary for {len(result.get('species_list', []))} species."
        if tool == "retrieve_knowledge":
            return f"Retrieved {result.get('results_count', 0)} documents."
        return str(result)


function_call_processor = FunctionCallProcessor()
combined_tools_processor = CombinedToolsProcessor()
