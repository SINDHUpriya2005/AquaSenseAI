from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.database import db
from app.models.schemas import AnalyticsSummary
from app.utils.deps import get_current_user, object_id_or_404

router = APIRouter(prefix="/analytics", tags=["Analytics"])


async def _assert_owns_purifier(purifier_id: str, current_user: dict) -> dict:
    oid = object_id_or_404(purifier_id, "Purifier")
    doc = await db.purifiers.find_one({"_id": oid, "owner_id": current_user["_id"]})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purifier not found")
    return doc


@router.get("/summary/{purifier_id}", response_model=AnalyticsSummary)
async def get_summary(purifier_id: str, current_user: dict = Depends(get_current_user)):
    purifier = await _assert_owns_purifier(purifier_id, current_user)
    now = datetime.now(timezone.utc)

    latest_prediction = await db.predictions.find_one(
        {"purifier_id": purifier_id}, sort=[("created_at", -1)]
    )

    week_ago = now - timedelta(days=7)
    week_cursor = db.readings.find({"purifier_id": purifier_id, "recorded_at": {"$gte": week_ago}})
    week_readings = [doc async for doc in week_cursor]

    total_readings = await db.readings.count_documents({"purifier_id": purifier_id})

    def _avg(field: str):
        values = [r[field] for r in week_readings if field in r]
        return round(sum(values) / len(values), 2) if values else None

    installation_date = purifier["installation_date"]
    if installation_date.tzinfo is None:
        installation_date = installation_date.replace(tzinfo=timezone.utc)
    days_since_install = max((now - installation_date).days, 0)

    last_change = purifier.get("last_filter_change")
    days_since_filter_change = None
    if last_change:
        if last_change.tzinfo is None:
            last_change = last_change.replace(tzinfo=timezone.utc)
        days_since_filter_change = max((now - last_change).days, 0)

    return AnalyticsSummary(
        purifier_id=purifier_id,
        latest_health_score=latest_prediction["filter_health_score"] if latest_prediction else None,
        latest_remaining_life_days=latest_prediction["remaining_life_days"] if latest_prediction else None,
        alert_level=latest_prediction["alert_level"] if latest_prediction else None,
        avg_tds_7d=_avg("tds_ppm"),
        avg_ph_7d=_avg("ph"),
        avg_turbidity_7d=_avg("turbidity_ntu"),
        total_readings=total_readings,
        days_since_install=days_since_install,
        days_since_filter_change=days_since_filter_change,
    )


@router.get("/overview")
async def get_fleet_overview(current_user: dict = Depends(get_current_user)):
    """
    Aggregated KPIs across every purifier the user owns - powers the
    dashboard's top-level KPI cards.
    """
    purifiers_cursor = db.purifiers.find({"owner_id": current_user["_id"]})
    purifiers = [doc async for doc in purifiers_cursor]

    summaries = []
    for purifier in purifiers:
        pid = str(purifier["_id"])
        latest_prediction = await db.predictions.find_one({"purifier_id": pid}, sort=[("created_at", -1)])
        summaries.append(
            {
                "purifier_id": pid,
                "name": purifier["name"],
                "health_score": latest_prediction["filter_health_score"] if latest_prediction else None,
                "remaining_life_days": latest_prediction["remaining_life_days"] if latest_prediction else None,
                "alert_level": latest_prediction["alert_level"] if latest_prediction else "watch",
            }
        )

    scored = [s for s in summaries if s["health_score"] is not None]
    avg_health = round(sum(s["health_score"] for s in scored) / len(scored), 1) if scored else None

    alert_counts = {"ok": 0, "watch": 0, "warning": 0, "critical": 0}
    for s in summaries:
        alert_counts[s["alert_level"]] = alert_counts.get(s["alert_level"], 0) + 1

    total_readings = await db.readings.count_documents(
        {"purifier_id": {"$in": [str(p["_id"]) for p in purifiers]}}
    )

    return {
        "total_purifiers": len(purifiers),
        "average_health_score": avg_health,
        "alert_counts": alert_counts,
        "purifiers_needing_attention": alert_counts["warning"] + alert_counts["critical"],
        "total_readings_logged": total_readings,
        "purifiers": summaries,
    }
