"""Conversation API routes."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

from app.services.chat_service import get_session_with_messages, list_sessions_by_tenant

router = APIRouter(prefix="/conversations", tags=["conversations"])


def _map_message(msg: dict[str, Any]) -> dict[str, Any]:
    media_type = msg.get("mediaType")
    message_type = msg.get("messageType") or ("image" if media_type == "image" else "pdf" if media_type == "document" else "text")
    msg_type = "text"
    if message_type == "image" or media_type == "image":
        msg_type = "image"
    elif message_type == "document" or media_type == "document" or media_type == "pdf":
        msg_type = "pdf"

    sender = msg.get("sender", "user")
    from_role = "user" if sender == "user" else "ai" if sender == "ai" else "agent"

    meta: dict[str, Any] = {}
    media_url = msg.get("mediaUrl") or msg.get("imageUrl")
    if media_url:
        if msg_type == "image":
            meta["url"] = media_url
            if msg.get("mediaId"):
                meta["mediaId"] = msg["mediaId"]
            if msg.get("caption"):
                meta["caption"] = msg["caption"]
            if msg.get("mediaMimeType"):
                meta["mimeType"] = msg["mediaMimeType"]
        elif msg_type == "pdf":
            meta["filename"] = msg.get("content", "document.pdf")
            meta["size"] = "—"
            meta["url"] = media_url

    return {
        "id": msg.get("id", ""),
        "from": from_role,
        "type": msg_type,
        "content": msg.get("content", ""),
        "meta": meta if meta else None,
        "timestamp": msg.get("timestamp", datetime.utcnow()).isoformat()
        if isinstance(msg.get("timestamp"), datetime)
        else str(msg.get("timestamp", "")),
    }


def _map_session(session: dict[str, Any], messages: list[dict[str, Any]]) -> dict[str, Any]:
    updated = session.get("updatedAt", datetime.utcnow())
    return {
        "id": session.get("id", ""),
        "phone": session.get("phone", ""),
        "name": session.get("name", "Customer"),
        "tenantId": session.get("tenantId", ""),
        "lastActivity": updated.isoformat() if isinstance(updated, datetime) else str(updated),
        "status": session.get("status", "active"),
        "unread": session.get("unread", 0),
        "isTyping": session.get("isTyping", False),
        "messages": [_map_message(m) for m in messages],
    }


@router.get("")
async def list_conversations(tenant: str) -> list[dict[str, Any]]:
    sessions = await list_sessions_by_tenant(tenant)
    result = []
    for session in sessions:
        full = await get_session_with_messages(session["id"])
        if full:
            result.append(_map_session(full, full.get("messages", [])))
    return result


@router.get("/{session_id}")
async def get_conversation(session_id: str) -> dict[str, Any]:
    session = await get_session_with_messages(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return _map_session(session, session.get("messages", []))
