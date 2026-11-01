"""Data Pattern Analysis Agent — exploratory data analysis only (no model training)."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd

from app.agents.base import AgentResult, BaseAgent
from app.services.iris_service import df, iris

FEATURES = list(iris.feature_names)
PETAL_WIDTH = "petal width (cm)"


def _fisher_scores(frame: pd.DataFrame) -> dict[str, float]:
    """Between-class / within-class variance ratio per feature."""
    overall = frame[FEATURES].mean()
    between = pd.Series(0.0, index=FEATURES)
    within = pd.Series(0.0, index=FEATURES)
    for _species, group in frame.groupby("species", observed=True):
        n = len(group)
        between += n * (group[FEATURES].mean() - overall) ** 2
        within += ((group[FEATURES] - group[FEATURES].mean()) ** 2).sum()
    return {feature: round(float(between[feature] / within[feature]), 4) for feature in FEATURES}


def _iqr_outliers(frame: pd.DataFrame) -> dict[str, dict[str, Any]]:
    outliers: dict[str, dict[str, Any]] = {}
    for feature in FEATURES:
        q1 = frame[feature].quantile(0.25)
        q3 = frame[feature].quantile(0.75)
        iqr = q3 - q1
        low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = (frame[feature] < low) | (frame[feature] > high)
        outliers[feature] = {
            "count": int(mask.sum()),
            "lower_bound": round(float(low), 2),
            "upper_bound": round(float(high), 2),
        }
    return outliers


@lru_cache(maxsize=1)
def compute_eda() -> dict[str, Any]:
    """Dataset EDA is request-invariant, so compute it once per process."""
    frame = df
    class_distribution = [
        {
            "species": str(species),
            "count": int(count),
            "share": round(float(count) / len(frame), 4),
        }
        for species, count in frame["species"].value_counts().sort_index().items()
    ]
    class_counts = {item["count"] for item in class_distribution}

    feature_stats = {
        feature: {
            "mean": round(float(frame[feature].mean()), 3),
            "std": round(float(frame[feature].std()), 3),
            "min": round(float(frame[feature].min()), 3),
            "q1": round(float(frame[feature].quantile(0.25)), 3),
            "median": round(float(frame[feature].median()), 3),
            "q3": round(float(frame[feature].quantile(0.75)), 3),
            "max": round(float(frame[feature].max()), 3),
        }
        for feature in FEATURES
    }

    species_means = {
        str(species): {feature: round(float(group[feature].mean()), 2) for feature in FEATURES}
        for species, group in frame.groupby("species", observed=True)
    }

    correlations = frame[FEATURES].corr().round(4)
    pairs: list[dict[str, Any]] = []
    for i, first in enumerate(FEATURES):
        for second in FEATURES[i + 1:]:
            pairs.append({
                "feature_a": first,
                "feature_b": second,
                "correlation": float(correlations.loc[first, second]),
            })
    pairs.sort(key=lambda item: abs(item["correlation"]), reverse=True)

    fisher = _fisher_scores(frame)
    ranked_features = sorted(fisher, key=fisher.get, reverse=True)
    outliers = _iqr_outliers(frame)

    # Separability: can a single petal-width threshold isolate setosa?
    setosa_max = float(frame.loc[frame["species"] == "setosa", PETAL_WIDTH].max())
    other_min = float(frame.loc[frame["species"] != "setosa", PETAL_WIDTH].min())
    threshold = round((setosa_max + other_min) / 2, 3)
    predicted = np.where(frame[PETAL_WIDTH] <= threshold, 1, 0)
    actual = np.where(frame["species"] == "setosa", 1, 0)
    threshold_accuracy = round(float((predicted == actual).mean()), 4)

    versicolor = frame.loc[frame["species"] == "versicolor", PETAL_WIDTH]
    virginica = frame.loc[frame["species"] == "virginica", PETAL_WIDTH]
    overlap_low = max(float(versicolor.min()), float(virginica.min()))
    overlap_high = min(float(versicolor.max()), float(virginica.max()))
    in_overlap = (
        ((frame["species"] == "versicolor") | (frame["species"] == "virginica"))
        & (frame[PETAL_WIDTH] >= overlap_low)
        & (frame[PETAL_WIDTH] <= overlap_high)
    )
    overlap_count = int(in_overlap.sum())

    top_feature = ranked_features[0]
    findings = [
        f"{top_feature} is the most discriminative feature (Fisher score {fisher[top_feature]:.3f}).",
        f"Setosa is isolated by a petal-width threshold of {threshold} cm (accuracy {threshold_accuracy * 100:.1f}%).",
        f"Versicolor and virginica overlap in petal width between {overlap_low} and {overlap_high} cm ({overlap_count} samples).",
        f"Strongest correlation: {pairs[0]['feature_a']} vs {pairs[0]['feature_b']} (r={pairs[0]['correlation']:.3f}).",
        (
            f"The dataset is balanced: {next(iter(class_counts))} samples per species."
            if len(class_counts) == 1
            else f"Class sizes are imbalanced: {sorted(class_counts)}."
        ),
    ]

    return {
        "sample_count": int(len(frame)),
        "feature_count": len(FEATURES),
        "class_distribution": class_distribution,
        "feature_stats": feature_stats,
        "species_means": species_means,
        "correlation_matrix": {
            feature: {other: round(float(correlations.loc[feature, other]), 4) for other in FEATURES}
            for feature in FEATURES
        },
        "strongest_correlations": pairs[:5],
        "fisher_scores": fisher,
        "ranked_features": ranked_features,
        "outliers": outliers,
        "separability": {
            "petal_width_threshold_cm": threshold,
            "setosa_vs_rest_accuracy": threshold_accuracy,
            "versicolor_virginica_overlap_range": [overlap_low, overlap_high],
            "overlapping_samples": overlap_count,
        },
        "findings": findings,
    }


class DataPatternAgent(BaseAgent):
    name = "Data Pattern Analysis Agent"
    role = "Exploratory data analysis: distributions, correlations, separability, outliers."
    suggested_model = "GPT-4o-mini / Claude Haiku / Llama 3.x"
    permissions = ("read:iris_dataset", "execute:pandas_analysis")
    allowed_inputs = ("query",)

    def run(self, context: dict[str, Any]) -> AgentResult:
        return AgentResult(
            output=dict(compute_eda()),
            reasoning=(
                "Inspected class balance, per-feature moments, the correlation matrix, "
                "IQR outliers, and a single-threshold separability test. No model was trained."
            ),
        )
