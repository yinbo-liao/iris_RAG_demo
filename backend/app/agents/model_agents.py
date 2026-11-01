"""Model-training agents: Random Forest, SVM, and XGBoost.

Each agent owns one estimator and returns the same metric contract so the
Evaluation Agent can compare them without model-specific knowledge. The Iris
data is a module-level constant and the agents ignore the user query, so each
estimator is trained once per process and its metrics are reused.
"""

from __future__ import annotations

from typing import Any

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from app.agents.base import AgentResult, BaseAgent
from app.services.iris_service import X, iris, y

TEST_SIZE = 0.25
RANDOM_STATE = 42
CLASS_NAMES = list(iris.target_names)

_MODEL_CACHE: dict[str, dict[str, Any]] = {}


def _train_and_evaluate(model_name: str, estimator: Any, engine: str, params: dict[str, Any]) -> dict[str, Any]:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE
    )

    estimator.fit(X_train, y_train)
    predictions = estimator.predict(X_test)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_test, predictions, labels=range(len(CLASS_NAMES)), zero_division=0
    )
    per_class = {
        name: {
            "precision": round(float(precision[i]), 4),
            "recall": round(float(recall[i]), 4),
            "f1": round(float(f1[i]), 4),
            "support": int(support[i]),
        }
        for i, name in enumerate(CLASS_NAMES)
    }

    cv = cross_val_score(
        estimator,
        X,
        y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE),
        scoring="f1_macro",
    )

    output: dict[str, Any] = {
        "model": model_name,
        "engine": engine,
        "params": params,
        "metrics": {
            "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
            # Macro averages are the unweighted means of the per-class scores.
            "precision": round(float(precision.mean()), 4),
            "recall": round(float(recall.mean()), 4),
            "f1": round(float(f1.mean()), 4),
        },
        "cv_f1_macro": {"mean": round(float(cv.mean()), 4), "std": round(float(cv.std()), 4), "folds": 5},
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=range(len(CLASS_NAMES))).tolist(),
        "classes": CLASS_NAMES,
        "split": {"train": int(len(X_train)), "test": int(len(X_test))},
    }

    if hasattr(estimator, "feature_importances_"):
        output["feature_importances"] = {
            name: round(float(value), 4)
            for name, value in zip(iris.feature_names, estimator.feature_importances_)
        }

    return output


class _ModelAgent(BaseAgent):
    permissions = ("read:iris_dataset", "train:own_classifier")
    allowed_inputs = ("query",)
    model_label = ""

    def run(self, context: dict[str, Any]) -> AgentResult:
        key = type(self).__name__
        if key not in _MODEL_CACHE:
            _MODEL_CACHE[key] = self._fit()
        return AgentResult(
            output=dict(_MODEL_CACHE[key]),
            reasoning=(
                f"Trained {_MODEL_CACHE[key]['engine']} on a stratified "
                f"{int((1 - TEST_SIZE) * 100)}/{int(TEST_SIZE * 100)} split "
                f"(random_state={RANDOM_STATE}) and scored it with macro-averaged metrics "
                "plus 5-fold cross-validation."
            ),
        )

    def _fit(self) -> dict[str, Any]:
        raise NotImplementedError


class RandomForestAgent(_ModelAgent):
    name = "Random Forest Agent"
    role = "Train and evaluate a Random Forest classifier."
    suggested_model = "GPT-4o-mini"
    model_label = "Random Forest"

    def _fit(self) -> dict[str, Any]:
        from sklearn.ensemble import RandomForestClassifier

        params = {"n_estimators": 200, "random_state": RANDOM_STATE, "n_jobs": 1}
        estimator = RandomForestClassifier(**params)
        return _train_and_evaluate(self.model_label, estimator, "sklearn.RandomForestClassifier", params)


class SVMAgent(_ModelAgent):
    name = "SVM Agent"
    role = "Train and evaluate a support-vector classifier."
    suggested_model = "GPT-4o-mini"
    model_label = "SVM"

    def _fit(self) -> dict[str, Any]:
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
        from sklearn.svm import SVC

        params = {"kernel": "rbf", "C": 1.0, "gamma": "scale", "random_state": RANDOM_STATE}
        estimator = Pipeline([("scaler", StandardScaler()), ("svc", SVC(**params))])
        return _train_and_evaluate(self.model_label, estimator, "sklearn.svm.SVC (StandardScaler pipeline)", params)


class XGBoostAgent(_ModelAgent):
    name = "XGBoost Agent"
    role = "Train and evaluate a gradient-boosted tree classifier."
    suggested_model = "GPT-4o-mini"
    model_label = "XGBoost"

    def _fit(self) -> dict[str, Any]:
        try:
            from xgboost import XGBClassifier

            params = {
                "n_estimators": 200,
                "max_depth": 3,
                "learning_rate": 0.1,
                "subsample": 0.9,
                "random_state": RANDOM_STATE,
                "eval_metric": "mlogloss",
                "verbosity": 0,
            }
            estimator = XGBClassifier(**params)
            return _train_and_evaluate(self.model_label, estimator, "xgboost.XGBClassifier", params)
        except ImportError:
            from sklearn.ensemble import HistGradientBoostingClassifier

            params = {"max_iter": 200, "learning_rate": 0.1, "random_state": RANDOM_STATE}
            estimator = HistGradientBoostingClassifier(**params)
            return _train_and_evaluate(
                self.model_label,
                estimator,
                "sklearn.HistGradientBoostingClassifier (xgboost-compatible fallback)",
                params,
            )
