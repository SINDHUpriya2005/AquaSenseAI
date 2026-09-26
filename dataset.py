"""
Synthetic dataset generator for filter health / remaining-life prediction.

There is no physical IoT fleet yet, so we bootstrap the ML model with a
physically-plausible simulation of how RO/UF filter cartridges degrade over
their lifetime. The simulation encodes well-known domain relationships:

  - As a membrane/cartridge ages, its ability to reject dissolved solids
    drops, so outlet TDS creeps up relative to a clean-filter baseline.
  - Turbidity removal degrades similarly as the pre-filter clogs.
  - A clogging filter increases restriction, so flow rate drops and the
    pump has to work at a higher pressure to maintain output.
  - Heavier daily usage (liters processed, cycles/day) accelerates ageing.
  - pH drifts slightly as scale/media exhausts, though this is a weaker
    signal than TDS/turbidity/flow.

This keeps the architecture ready to be retrained on real sensor data later
(app/ml/train_model.py accepts any DataFrame with the same feature schema).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FEATURE_COLUMNS = [
    "tds_ppm",
    "ph",
    "turbidity_ntu",
    "flow_rate_lpm",
    "pressure_bar",
    "daily_usage_liters",
    "usage_frequency_per_day",
    "water_temperature_c",
    "filter_age_days",
    "cumulative_liters_processed",
    "rated_filter_life_days",
    "rated_capacity_liters",
]

TARGET_COLUMNS = ["filter_health_score", "remaining_life_days"]


def generate_synthetic_dataset(n_samples: int = 12000, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    rated_filter_life_days = rng.choice([180, 270, 365, 545, 730], size=n_samples)
    rated_capacity_liters = rng.choice([4000, 6000, 8000, 10000, 12000], size=n_samples)

    # Age as a fraction of rated life. Uniform coverage from a brand-new
    # filter through to well past its rated life, so the model sees a
    # balanced spread of healthy, ageing and overdue filters.
    life_fraction = rng.uniform(0.0, 1.25, size=n_samples)
    filter_age_days = np.round(life_fraction * rated_filter_life_days).astype(int)

    usage_frequency_per_day = rng.integers(2, 40, size=n_samples)
    daily_usage_liters = usage_frequency_per_day * rng.uniform(1.5, 6.0, size=n_samples)
    cumulative_liters_processed = daily_usage_liters * filter_age_days * rng.uniform(0.85, 1.1, size=n_samples)

    # Usage intensity relative to what the cartridge is rated for -
    # heavy real-world use accelerates degradation beyond pure calendar age.
    capacity_pressure = cumulative_liters_processed / (rated_capacity_liters * (rated_filter_life_days / 365))
    capacity_pressure = np.clip(capacity_pressure, 0, 1.5)
    degradation = np.clip(0.65 * life_fraction + 0.35 * capacity_pressure, 0, 1.4)
    degradation = np.clip(degradation + rng.normal(0, 0.03, size=n_samples), 0, 1.4)

    # Sensor readings driven by the degradation index -----------------------------------
    baseline_tds = rng.uniform(15, 40, size=n_samples)  # a healthy filter's outlet TDS
    tds_ppm = baseline_tds + degradation * rng.uniform(60, 140, size=n_samples)
    tds_ppm = np.clip(tds_ppm + rng.normal(0, 4, size=n_samples), 5, 600)

    ph = 7.2 - degradation * rng.uniform(0.3, 0.9, size=n_samples) + rng.normal(0, 0.15, size=n_samples)
    ph = np.clip(ph, 5.5, 8.8)

    turbidity_ntu = 0.3 + degradation * rng.uniform(1.5, 5.0, size=n_samples)
    turbidity_ntu = np.clip(turbidity_ntu + rng.normal(0, 0.1, size=n_samples), 0.05, 40)

    flow_rate_lpm = 2.2 - degradation * rng.uniform(0.6, 1.6, size=n_samples)
    flow_rate_lpm = np.clip(flow_rate_lpm + rng.normal(0, 0.08, size=n_samples), 0.1, 3.0)

    pressure_bar = 1.8 + degradation * rng.uniform(0.8, 2.2, size=n_samples)
    pressure_bar = np.clip(pressure_bar + rng.normal(0, 0.1, size=n_samples), 0.5, 8.0)

    water_temperature_c = rng.uniform(15, 35, size=n_samples)

    # Targets -----------------------------------------------------------------------------
    filter_health_score = 100 * (1 - degradation / 1.4)
    filter_health_score = np.clip(filter_health_score + rng.normal(0, 3, size=n_samples), 0, 100)

    remaining_life_days = (rated_filter_life_days - filter_age_days) * (1 - 0.4 * capacity_pressure.clip(0, 1))
    remaining_life_days = np.clip(remaining_life_days + rng.normal(0, 5, size=n_samples), 0, None)

    df = pd.DataFrame(
        {
            "tds_ppm": tds_ppm,
            "ph": ph,
            "turbidity_ntu": turbidity_ntu,
            "flow_rate_lpm": flow_rate_lpm,
            "pressure_bar": pressure_bar,
            "daily_usage_liters": daily_usage_liters,
            "usage_frequency_per_day": usage_frequency_per_day,
            "water_temperature_c": water_temperature_c,
            "filter_age_days": filter_age_days,
            "cumulative_liters_processed": cumulative_liters_processed,
            "rated_filter_life_days": rated_filter_life_days,
            "rated_capacity_liters": rated_capacity_liters,
            "filter_health_score": filter_health_score,
            "remaining_life_days": remaining_life_days,
        }
    )
    return df


if __name__ == "__main__":
    data = generate_synthetic_dataset()
    print(data.describe())
