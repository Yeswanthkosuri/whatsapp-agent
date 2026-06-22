"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.campaigns import router as campaigns_router
from app.api.conversations import router as conversations_router
from app.api.dashboard import router as dashboard_router
from app.api.media import router as media_router
from app.api.settings import router as settings_router
from app.api.tenants import router as tenants_router
from app.api.webhook import router as webhook_router
from app.core.config import get_settings
from app.core.database import close_db, connect_db, ping_db

settings = get_settings()
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_db()
    logger.info("Application started")
    yield
    await close_db()
    logger.info("Application shutdown")


app = FastAPI(
    title="Multi-Tenant WhatsApp AI Orchestrator",
    description="Production-ready WhatsApp AI Support & Sales Agent SaaS API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(tenants_router)
app.include_router(conversations_router)
app.include_router(dashboard_router)
app.include_router(settings_router)
app.include_router(media_router)
app.include_router(campaigns_router)


@app.get("/health")
async def health() -> dict:
    db_ok = await ping_db()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "connected" if db_ok else "disconnected",
        "service": "whatsapp-ai-orchestrator",
    }
