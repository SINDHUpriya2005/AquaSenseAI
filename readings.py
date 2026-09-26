from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.database import db
from app.models.schemas import ReadingCreate, ReadingOut
from app.utils.deps import get_current_user, object_id_or_404

router = APIRouter(prefix="/readings", tags=["Water Quality Readings"])


def _serialize(doc: dict) -> ReadingOut:
    return ReadingOut(
        id=str(doc["_id"]),
        purifier_id=doc["purifier_id"],
        tds_ppm=doc["tds_ppm"],
        ph=doc["ph"],
        turbidity_ntu=doc["turbidity_ntu"],
        flow_rate_lpm=doc["flow_rate_lpm"],
        daily_usage_liters=doc["daily_usage_liters"],
        usage_frequency_per_day=doc["usage_frequency_per_day"],
        water_temperature_c=doc["water_temperature_c"],
        pressure_bar=doc["pressure_bar"],
        recorded_at=doc["recorded_at"],
    )


async def _assert_owns_purifier(purifier_id: str, current_user: dict):
    oid = object_id_or_404(purifier_id, "Purifier")
    doc = await db.purifiers.find_one({"_id": oid, "owner_id": current_user["_id"]})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purifier not found")
    return doc


@router.post("", response_model=ReadingOut, status_code=status.HTTP_201_CREATED)
async def add_reading(payload: ReadingCreate, current_user: dict = Depends(get_current_user)):
    await _assert_owns_purifier(payload.purifier_id, current_user)

    doc = payload.model_dump()
    doc["recorded_at"] = payload.recorded_at or datetime.now(timezone.utc)
    result = await db.readings.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("", response_model=list[ReadingOut])
async def list_readings(
    purifier_id: str = Query(...),
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(get_current_user),
):
    await _assert_owns_purifier(purifier_id, current_user)
    cursor = db.readings.find({"purifier_id": purifier_id}).sort("recorded_at", -1).limit(limit)
    docs = [doc async for doc in cursor]
    docs.reverse()
    return [_serialize(doc) for doc in docs]


@router.delete("/{reading_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reading(reading_id: str, current_user: dict = Depends(get_current_user)):
    oid = object_id_or_404(reading_id, "Reading")
    doc = await db.readings.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reading not found")
    await _assert_owns_purifier(doc["purifier_id"], current_user)
    await db.readings.delete_one({"_id": oid})
