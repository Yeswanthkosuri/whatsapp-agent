"""Dashboard analytics API routes."""

from fastapi import APIRouter

from app.services.chat_service import (
    count_active_sessions,
    count_messages_by_type,
    count_messages_today,
    list_sessions_by_tenant,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def dashboard_stats(tenant: str) -> dict:
    active = await count_active_sessions(tenant)
    messages_today = await count_messages_today(tenant)
    documents = await count_messages_by_type(tenant, "document")
    images = await count_messages_by_type(tenant, "image")
    sessions = await list_sessions_by_tenant(tenant)
    handover = sum(1 for s in sessions if s.get("status") == "handover")

    return {
        "activeConversations": active,
        "messagesToday": messages_today,
        "documentsSent": documents,
        "imagesSent": images,
        "humanHandover": handover,
    }
