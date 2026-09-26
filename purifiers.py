from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import db
from app.models.schemas import PurifierCreate, PurifierOut, PurifierUpdate
from app.utils.deps import get_current_user, object_id_or_404

router = APIRouter(prefix="/purifiers", tags=["Purifiers"])


def _serialize(doc: dict) -> PurifierOut:
    return PurifierOut(
        id=str(doc["_id"]),
        owner_id=str(doc["owner_id"]),
        name=doc["name"],
        model=doc["model"],
        filter_type=doc["filter_type"],
        location=doc.get("location"),
        installation_date=doc["installation_date"],
        last_filter_change=doc.get("last_filter_change"),
        rated_filter_life_days=doc["rated_filter_life_days"],
        rated_capacity_liters=doc["rated_capacity_liters"],
        created_at=doc["created_at"],
    )


async def _get_owned_purifier(purifier_id: str, current_user: dict) -> dict:
    oid = object_id_or_404(purifier_id, "Purifier")
    doc = await db.purifiers.find_one({"_id": oid, "owner_id": current_user["_id"]})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purifier not found")
    return doc


@router.post("", response_model=PurifierOut, status_code=status.HTTP_201_CREATED)
async def create_purifier(payload: PurifierCreate, current_user: dict = Depends(get_current_user)):
    doc = payload.model_dump()
    doc["owner_id"] = current_user["_id"]
    doc["last_filter_change"] = payload.installation_date
    doc["created_at"] = datetime.now(timezone.utc)
    result = await db.purifiers.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _serialize(doc)


@router.get("", response_model=list[PurifierOut])
async def list_purifiers(current_user: dict = Depends(get_current_user)):
    cursor = db.purifiers.find({"owner_id": current_user["_id"]}).sort("created_at", -1)
    return [_serialize(doc) async for doc in cursor]


@router.get("/{purifier_id}", response_model=PurifierOut)
async def get_purifier(purifier_id: str, current_user: dict = Depends(get_current_user)):
    doc = await _get_owned_purifier(purifier_id, current_user)
    return _serialize(doc)


@router.patch("/{purifier_id}", response_model=PurifierOut)
async def update_purifier(
    purifier_id: str, payload: PurifierUpdate, current_user: dict = Depends(get_current_user)
):
    doc = await _get_owned_purifier(purifier_id, current_user)
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if updates:
        await db.purifiers.update_one({"_id": doc["_id"]}, {"$set": updates})
        doc = await db.purifiers.find_one({"_id": doc["_id"]})
    return _serialize(doc)


@router.post("/{purifier_id}/replace-filter", response_model=PurifierOut)
async def log_filter_replacement(purifier_id: str, current_user: dict = Depends(get_current_user)):
    """Marks 'today' as the last filter change, resetting the ageing clock."""
    doc = await _get_owned_purifier(purifier_id, current_user)
    now = datetime.now(timezone.utc)
    await db.purifiers.update_one({"_id": doc["_id"]}, {"$set": {"last_filter_change": now}})
    doc = await db.purifiers.find_one({"_id": doc["_id"]})
    return _serialize(doc)


@router.delete("/{purifier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purifier(purifier_id: str, current_user: dict = Depends(get_current_user)):
    doc = await _get_owned_purifier(purifier_id, current_user)
    await db.purifiers.delete_one({"_id": doc["_id"]})
    await db.readings.delete_many({"purifier_id": str(doc["_id"])})
    await db.predictions.delete_many({"purifier_id": str(doc["_id"])})
