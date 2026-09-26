"""
Trains the two regression models AquaSense AI relies on:

  1. filter_health_score  (0-100)
  2. remaining_life_days  (>= 0)

Run directly to (re)train and persist models:

    python -m app.ml.train_model

Artifacts are written to app/ml/artifacts/:
  - health_model.joblib
  - life_model.joblib
  - feature_columns.joblib
  - metrics.json
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from app.ml.dataset import FEATURE_COLUMNS, generate_synthetic_dataset

ARTIFACT_DIR = Path(__file__).parent / "artifacts"


def train_and_save(n_samples: int = 12000, random_state: int = 42) -> dict:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    df = generate_synthetic_dataset(n_samples=n_samples, random_state=random_state)
    X = df[FEATURE_COLUMNS]
    y_health = df["filter_health_score"]
    y_life = df["remaining_life_days"]

    X_train, X_test, y_health_train, y_health_test, y_life_train, y_life_test = train_test_split(
        X, y_health, y_life, test_size=0.2, random_state=random_state
    )

    health_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=3,
        random_state=random_state,
        n_jobs=-1,
    )
    health_model.fit(X_train, y_health_train)

    life_model = RandomForestRegressor(
        n_estimators=300,
        max_depth=14,
        min_samples_leaf=3,
        random_state=random_state,
        n_jobs=-1,
    )
    life_model.fit(X_train, y_life_train)

    health_pred = health_model.predict(X_test)
    life_pred = life_model.predict(X_test)

    metrics = {
        "health_score_mae": float(mean_absolute_error(y_health_test, health_pred)),
        "health_score_r2": float(r2_score(y_health_test, health_pred)),
        "remaining_life_mae_days": float(mean_absolute_error(y_life_test, life_pred)),
        "remaining_life_r2": float(r2_score(y_life_test, life_pred)),
        "n_samples": n_samples,
    }

    joblib.dump(health_model, ARTIFACT_DIR / "health_model.joblib")
    joblib.dump(life_model, ARTIFACT_DIR / "life_model.joblib")
    joblib.dump(FEATURE_COLUMNS, ARTIFACT_DIR / "feature_columns.joblib")
    with open(ARTIFACT_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    return metrics


if __name__ == "__main__":
    result = train_and_save()
    print("Training complete. Metrics:")
    print(json.dumps(result, indent=2))
