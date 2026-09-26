"""
Pydantic request/response models.

MongoDB documents use string ObjectIds represented as plain `str` fields
named `id` in API responses (converted from Mongo's `_id`) so the frontend
never has to deal with BSON types.
"""
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth / Users
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ---------------------------------------------------------------------------
# Purifiers
# ---------------------------------------------------------------------------
class FilterType(str, Enum):
    RO = "RO"
    UF = "UF"
    RO_UF = "RO+UF"
    ACTIVATED_CARBON = "Activated Carbon"
    UV = "UV"


class PurifierCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    model: str = Field(..., min_length=1, max_length=80)
    filter_type: FilterType = FilterType.RO_UF
    location: Optional[str] = Field(None, max_length=120)
    installation_date: datetime
    rated_filter_life_days: int = Field(365, ge=30, le=3650)
    rated_capacity_liters: float = Field(6000, gt=0)


class PurifierUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    filter_type: Optional[FilterType] = None
    rated_filter_life_days: Optional[int] = None
    rated_capacity_liters: Optional[float] = None
    last_filter_change: Optional[datetime] = None


class PurifierOut(BaseModel):
    id: str
    owner_id: str
    name: str
    model: str
    filter_type: FilterType
    location: Optional[str] = None
    installation_date: datetime
    last_filter_change: Optional[datetime] = None
    rated_filter_life_days: int
    rated_capacity_liters: float
    created_at: datetime


# ---------------------------------------------------------------------------
# Water quality readings
# ---------------------------------------------------------------------------
class ReadingCreate(BaseModel):
    purifier_id: str
    tds_ppm: float = Field(..., ge=0, le=2000, description="Total Dissolved Solids in ppm")
    ph: float = Field(..., ge=0, le=14)
    turbidity_ntu: float = Field(..., ge=0, le=100, description="Turbidity in NTU")
    flow_rate_lpm: float = Field(..., ge=0, le=20, description="Flow rate litres/min")
    daily_usage_liters: float = Field(..., ge=0, le=2000)
    usage_frequency_per_day: int = Field(..., ge=0, le=100)
    water_temperature_c: float = Field(25.0, ge=0, le=60)
    pressure_bar: float = Field(2.5, ge=0, le=10)
    recorded_at: Optional[datetime] = None


class ReadingOut(BaseModel):
    id: str
    purifier_id: str
    tds_ppm: float
    ph: float
    turbidity_ntu: float
    flow_rate_lpm: float
    daily_usage_liters: float
    usage_frequency_per_day: int
    water_temperature_c: float
    pressure_bar: float
    recorded_at: datetime


# ---------------------------------------------------------------------------
# Predictions / analytics
# ---------------------------------------------------------------------------
class AlertLevel(str, Enum):
    OK = "ok"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"


class PredictionOut(BaseModel):
    id: str
    purifier_id: str
    filter_health_score: float = Field(..., ge=0, le=100)
    remaining_life_days: float
    alert_level: AlertLevel
    insights: list[str]
    contributing_factors: dict[str, float]
    created_at: datetime


class AnalyticsSummary(BaseModel):
    purifier_id: str
    latest_health_score: Optional[float] = None
    latest_remaining_life_days: Optional[float] = None
    alert_level: Optional[AlertLevel] = None
    avg_tds_7d: Optional[float] = None
    avg_ph_7d: Optional[float] = None
    avg_turbidity_7d: Optional[float] = None
    total_readings: int
    days_since_install: int
    days_since_filter_change: Optional[int] = None
