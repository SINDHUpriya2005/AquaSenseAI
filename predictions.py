from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.database import db
from app.ml.predictor import get_engine
from app.models.schemas import PredictionOut
from app.utils.deps import get_current_user, object_id_or_404

router = APIRouter(prefix="/predictions", tags=["AI Predictions"])


def _serialize(doc: dict) -> PredictionOut:
    return PredictionOut(
        id=str(doc["_id"]),
        purifier_id=doc["purifier_id"],
        filter_health_score=doc["filter_health_score"],
        remaining_life_days=doc["remaining_life_days"],
        alert_level=doc["alert_level"],
        insights=doc["insights"],
        contributing_factors=doc["contributing_factors"],
        created_at=doc["created_at"],
    )


async def _assert_owns_purifier(purifier_id: str, current_user: dict) -> dict:
    oid = object_id_or_404(purifier_id, "Purifier")
    doc = await db.purifiers.find_one({"_id": oid, "owner_id": current_user["_id"]})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purifier not found")
    return doc


@router.post("/run/{purifier_id}", response_model=PredictionOut, status_code=status.HTTP_201_CREATED)
async def run_prediction(purifier_id: str, current_user: dict = Depends(get_current_user)):
    """
    Runs the AI model against the purifier's most recent water-quality
    reading and persists the resulting health / remaining-life prediction.
    """
    purifier = await _assert_owns_purifier(purifier_id, current_user)

    latest_reading = await db.readings.find_one(
        {"purifier_id": purifier_id}, sort=[("recorded_at", -1)]
    )
    if not latest_reading:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No water-quality readings found for this purifier yet. Add a reading first.",
        )

    engine = get_engine()
    result = engine.predict(purifier, latest_reading)

    doc = {
        "purifier_id": purifier_id,
        "filter_health_score": result["filter_health_score"],
        "remaining_life_days": result["remaining_life_days"],
        "alert_level": result["alert_level"],
        "insights": result["insights"],
        "contributing_factors": result["contributing_factors"],
        "created_at": datetime.now(timezone.utc),
    }
    inserted = await db.predictions.insert_one(doc)
    doc["_id"] = inserted.inserted_id
    return _serialize(doc)


@router.get("/latest/{purifier_id}", response_model=PredictionOut)
async def get_latest_prediction(purifier_id: str, current_user: dict = Depends(get_current_user)):
    await _assert_owns_purifier(purifier_id, current_user)
    doc = await db.predictions.find_one({"purifier_id": purifier_id}, sort=[("created_at", -1)])
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No predictions yet for this purifier")
    return _serialize(doc)


@router.get("/history/{purifier_id}", response_model=list[PredictionOut])
async def get_prediction_history(
    purifier_id: str,
    limit: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
):
    await _assert_owns_purifier(purifier_id, current_user)
    cursor = db.predictions.find({"purifier_id": purifier_id}).sort("created_at", -1).limit(limit)
    docs = [doc async for doc in cursor]
    docs.reverse()
    return [_serialize(doc) for doc in docs]
