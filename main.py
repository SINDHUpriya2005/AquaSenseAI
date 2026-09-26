"""
AquaSense AI - Intelligent Water Purifier Filter Prognostics System
FastAPI application entry point.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import db
from app.ml.predictor import get_engine
from app.routers import analytics, auth, predictions, purifiers, readings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    get_engine()  # warm up / train the ML models once at boot
    yield
    # Shutdown
    await db.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered prognostics for water purifier filter health and remaining useful life.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(purifiers.router, prefix=settings.API_V1_PREFIX)
app.include_router(readings.router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
async def root():
    return {"service": settings.APP_NAME, "status": "online"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
