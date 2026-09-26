"""
Runtime prediction engine.

Loads the persisted RandomForest models (training them on first run if the
artifacts are missing, so the app always works out of the box) and turns a
purifier's latest reading + metadata into:

  - filter_health_score (0-100)
  - remaining_life_days
  - alert_level (ok / watch / warning / critical)
  - human-readable insights
  - contributing_factors: which signals are pushing health down the most
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from app.ml.dataset import FEATURE_COLUMNS
from app.ml.train_model import ARTIFACT_DIR, train_and_save

_HEALTHY_BASELINE = {
    "tds_ppm": 25.0,
    "ph": 7.2,
    "turbidity_ntu": 0.4,
    "flow_rate_lpm": 2.1,
    "pressure_bar": 1.9,
}

# (label, feature, direction) - direction "high" means values ABOVE baseline
# indicate degradation, "low" means values BELOW baseline indicate it.
_FACTOR_DEFINITIONS = [
    ("TDS rejection", "tds_ppm", "high"),
    ("Turbidity control", "turbidity_ntu", "high"),
    ("Flow rate", "flow_rate_lpm", "low"),
    ("System pressure", "pressure_bar", "high"),
    ("pH stability", "ph", "deviation"),
]


class PredictionEngine:
    _instance: "PredictionEngine | None" = None

    def __init__(self):
        self.health_model = None
        self.life_model = None
        self.feature_columns = FEATURE_COLUMNS
        self._load_or_train()

    @classmethod
    def instance(cls) -> "PredictionEngine":
        if cls._instance is None:
            cls._instance = PredictionEngine()
        return cls._instance

    def _load_or_train(self):
        health_path = ARTIFACT_DIR / "health_model.joblib"
        life_path = ARTIFACT_DIR / "life_model.joblib"
        if not health_path.exists() or not life_path.exists():
            train_and_save()
        self.health_model = joblib.load(health_path)
        self.life_model = joblib.load(life_path)
        cols_path = ARTIFACT_DIR / "feature_columns.joblib"
        if cols_path.exists():
            self.feature_columns = joblib.load(cols_path)

    def build_features(self, purifier: dict, reading: dict) -> pd.DataFrame:
        installation_date = purifier["installation_date"]
        last_change = purifier.get("last_filter_change") or installation_date
        if isinstance(last_change, str):
            last_change = datetime.fromisoformat(last_change)
        if last_change.tzinfo is None:
            last_change = last_change.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        filter_age_days = max((now - last_change).days, 0)

        rated_life = purifier.get("rated_filter_life_days", 365)
        rated_capacity = purifier.get("rated_capacity_liters", 6000)
        daily_usage = reading.get("daily_usage_liters", 0)
        cumulative_liters_processed = daily_usage * max(filter_age_days, 1)

        row = {
            "tds_ppm": reading["tds_ppm"],
            "ph": reading["ph"],
            "turbidity_ntu": reading["turbidity_ntu"],
            "flow_rate_lpm": reading["flow_rate_lpm"],
            "pressure_bar": reading.get("pressure_bar", 2.5),
            "daily_usage_liters": daily_usage,
            "usage_frequency_per_day": reading.get("usage_frequency_per_day", 0),
            "water_temperature_c": reading.get("water_temperature_c", 25.0),
            "filter_age_days": filter_age_days,
            "cumulative_liters_processed": cumulative_liters_processed,
            "rated_filter_life_days": rated_life,
            "rated_capacity_liters": rated_capacity,
        }
        return pd.DataFrame([row], columns=self.feature_columns)

    def predict(self, purifier: dict, reading: dict) -> dict[str, Any]:
        features = self.build_features(purifier, reading)

        health_score = float(self.health_model.predict(features)[0])
        health_score = max(0.0, min(100.0, health_score))

        remaining_life_days = float(self.life_model.predict(features)[0])
        remaining_life_days = max(0.0, remaining_life_days)

        alert_level = self._alert_level(health_score, remaining_life_days)
        contributing_factors = self._contributing_factors(reading)
        insights = self._generate_insights(reading, purifier, health_score, remaining_life_days, contributing_factors)

        return {
            "filter_health_score": round(health_score, 1),
            "remaining_life_days": round(remaining_life_days, 1),
            "alert_level": alert_level,
            "insights": insights,
            "contributing_factors": contributing_factors,
        }

    @staticmethod
    def _alert_level(health_score: float, remaining_life_days: float) -> str:
        if health_score < 35 or remaining_life_days < 10:
            return "critical"
        if health_score < 55 or remaining_life_days < 25:
            return "warning"
        if health_score < 75 or remaining_life_days < 60:
            return "watch"
        return "ok"

    def _contributing_factors(self, reading: dict) -> dict[str, float]:
        """
        Rough, explainable "how far from a healthy baseline" score per signal,
        normalised to sum to 1.0 so the UI can render a breakdown.
        """
        scores = {}
        for label, feature, direction in _FACTOR_DEFINITIONS:
            value = reading.get(feature)
            if value is None:
                continue
            baseline = _HEALTHY_BASELINE[feature]
            if direction == "high":
                delta = max(value - baseline, 0)
                scale = baseline if baseline else 1
            elif direction == "low":
                delta = max(baseline - value, 0)
                scale = baseline if baseline else 1
            else:  # deviation (pH)
                delta = abs(value - baseline)
                scale = 1.0
            scores[label] = delta / scale if scale else delta

        total = sum(scores.values())
        if total <= 0:
            # Everything within healthy range - spread evenly at a low weight
            return {label: round(1 / len(scores), 3) for label in scores} if scores else {}
        return {label: round(v / total, 3) for label, v in scores.items()}

    def _generate_insights(
        self,
        reading: dict,
        purifier: dict,
        health_score: float,
        remaining_life_days: float,
        contributing_factors: dict[str, float],
    ) -> list[str]:
        insights: list[str] = []

        if reading["tds_ppm"] > 80:
            insights.append(
                f"Outlet TDS is {reading['tds_ppm']:.0f} ppm, well above the ~25 ppm baseline for a fresh "
                "membrane - this is the clearest sign the RO membrane is losing rejection capacity."
            )
        if reading["turbidity_ntu"] > 2.0:
            insights.append(
                f"Turbidity reading of {reading['turbidity_ntu']:.1f} NTU suggests the pre-filter or sediment "
                "stage is loading up with particulates."
            )
        if reading["flow_rate_lpm"] < 1.2:
            insights.append(
                f"Flow rate has dropped to {reading['flow_rate_lpm']:.2f} L/min, a classic symptom of a "
                "clogging cartridge restricting water flow."
            )
        if reading.get("pressure_bar", 0) > 3.2:
            insights.append(
                "System pressure is running higher than normal, meaning the pump is compensating for "
                "restriction inside the filter housing."
            )
        if abs(reading["ph"] - 7.2) > 0.8:
            insights.append(
                f"pH has drifted to {reading['ph']:.1f}, outside the typical 6.5-7.8 band for correctly "
                "functioning media."
            )

        if not insights:
            insights.append("All monitored water-quality parameters are within the healthy operating range.")

        if remaining_life_days < 15:
            insights.append(
                f"At current usage, the filter has roughly {remaining_life_days:.0f} days of useful life left "
                "- plan a replacement now to avoid a drop in output quality."
            )
        elif remaining_life_days < 45:
            insights.append(
                f"Estimated {remaining_life_days:.0f} days of remaining life - a good time to order a "
                "replacement cartridge so it arrives before you need it."
            )

        if contributing_factors:
            top_factor = max(contributing_factors, key=contributing_factors.get)
            if contributing_factors[top_factor] > 0.3:
                insights.append(f"{top_factor} is currently the biggest driver of filter degradation.")

        return insights


def get_engine() -> PredictionEngine:
    return PredictionEngine.instance()
