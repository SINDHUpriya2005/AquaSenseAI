"""
Seeds the database with a demo account so the dashboard has real-looking
data to show immediately, without needing physical sensors connected.

Usage (from the backend/ directory, with your venv active):
    python -m scripts.seed_demo_data
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.security import hash_password  # noqa: E402
from app.db.database import db  # noqa: E402
from app.ml.predictor import get_engine  # noqa: E402

DEMO_EMAIL = "demo@aquasense.ai"
DEMO_PASSWORD = "Demo@1234"
DAYS_OF_HISTORY = 60


async def seed():
    await db.connect()
    engine = get_engine()

    existing = await db.users.find_one({"email": DEMO_EMAIL})
    if existing:
        user_id = existing["_id"]
        print(f"Demo user already exists ({DEMO_EMAIL}); reusing it and clearing old data.")
        await db.purifiers.delete_many({"owner_id": user_id})
        old_purifier_ids = []
    else:
        result = await db.users.insert_one(
            {
                "name": "Demo Homeowner",
                "email": DEMO_EMAIL,
                "password_hash": hash_password(DEMO_PASSWORD),
                "created_at": datetime.now(timezone.utc),
            }
        )
        user_id = result.inserted_id

    now = datetime.now(timezone.utc)
    installation_date = now - timedelta(days=DAYS_OF_HISTORY + 40)

    purifier_doc = {
        "owner_id": user_id,
        "name": "Kitchen RO+UF Purifier",
        "model": "AquaPure X7",
        "filter_type": "RO+UF",
        "location": "Kitchen counter",
        "installation_date": installation_date,
        "last_filter_change": installation_date,
        "rated_filter_life_days": 180,
        "rated_capacity_liters": 6000,
        "created_at": now,
    }
    purifier_result = await db.purifiers.insert_one(purifier_doc)
    purifier_id = str(purifier_result.inserted_id)
    purifier_doc["_id"] = purifier_result.inserted_id

    rng = np.random.default_rng(7)

    for day_offset in range(DAYS_OF_HISTORY, -1, -1):
        recorded_at = now - timedelta(days=day_offset)
        age_days = (recorded_at - installation_date).days
        life_fraction = min(age_days / purifier_doc["rated_filter_life_days"], 1.3)
        degradation = np.clip(life_fraction + rng.normal(0, 0.03), 0, 1.4)

        usage_frequency = int(rng.integers(6, 22))
        daily_usage = usage_frequency * rng.uniform(2.0, 4.5)

        reading_doc = {
            "purifier_id": purifier_id,
            "tds_ppm": float(np.clip(25 + degradation * 95 + rng.normal(0, 4), 5, 400)),
            "ph": float(np.clip(7.2 - degradation * 0.5 + rng.normal(0, 0.1), 5.8, 8.5)),
            "turbidity_ntu": float(np.clip(0.3 + degradation * 3.2 + rng.normal(0, 0.08), 0.05, 20)),
            "flow_rate_lpm": float(np.clip(2.1 - degradation * 1.1 + rng.normal(0, 0.05), 0.2, 2.6)),
            "daily_usage_liters": float(round(daily_usage, 1)),
            "usage_frequency_per_day": usage_frequency,
            "water_temperature_c": float(round(rng.uniform(18, 30), 1)),
            "pressure_bar": float(np.clip(1.9 + degradation * 1.6 + rng.normal(0, 0.08), 0.8, 6.0)),
            "recorded_at": recorded_at,
        }
        insert_result = await db.readings.insert_one(reading_doc)
        reading_doc["_id"] = insert_result.inserted_id

        # Generate a prediction roughly every 3 days to build a trend line
        if day_offset % 3 == 0:
            prediction = engine.predict(purifier_doc, reading_doc)
            await db.predictions.insert_one(
                {
                    "purifier_id": purifier_id,
                    "filter_health_score": prediction["filter_health_score"],
                    "remaining_life_days": prediction["remaining_life_days"],
                    "alert_level": prediction["alert_level"],
                    "insights": prediction["insights"],
                    "contributing_factors": prediction["contributing_factors"],
                    "created_at": recorded_at,
                }
            )

    await db.disconnect()

    print("Seed complete.")
    print(f"  Login email:    {DEMO_EMAIL}")
    print(f"  Login password: {DEMO_PASSWORD}")
    print(f"  Purifier ID:    {purifier_id}")


if __name__ == "__main__":
    asyncio.run(seed())
