"""Chat session and message persistence helpers."""

import logging
from datetime import datetime
from typing import Any

from bson import ObjectId

from app.core.database import collection

logger = logging.getLogger(__name__)


def _oid_str(doc: dict[str, Any]) -> dict[str, Any]:
    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        doc.pop("_id", None)
    return doc


async def get_or_create_session(phone: str, tenant_id: str, name: str | None = None) -> dict[str, Any]:
    sessions = collection("chat_sessions")
    existing = await sessions.find_one({"phone": phone, "tenantId": tenant_id})
    if existing:
        return _oid_str(existing)

    now = datetime.utcnow()
    doc = {
        "phone": phone,
        "tenantId": tenant_id,
        "status": "active",
        "name": name or "Customer",
        "unread": 0,
        "isTyping": False,
        "createdAt": now,
        "updatedAt": now,
    }
    result = await sessions.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _oid_str(doc)


async def save_message(
    session_id: str,
    sender: str,
    content: str,
    media_url: str | None = None,
    media_type: str | None = None,
    message_type: str | None = None,
    media_id: str | None = None,
    caption: str | None = None,
    image_url: str | None = None,
    media_mime_type: str | None = None,
) -> dict[str, Any]:
    now = datetime.utcnow()
    doc = {
        "sessionId": session_id,
        "sender": sender,
        "content": content,
        "mediaUrl": media_url,
        "mediaType": media_type,
        "messageType": message_type,
        "mediaId": media_id,
        "caption": caption,
        "imageUrl": image_url,
        "mediaMimeType": media_mime_type,
        "timestamp": now,
    }
    result = await collection("messages").insert_one(doc)
    doc["_id"] = result.inserted_id

    await collection("chat_sessions").update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"updatedAt": now, "isTyping": False}},
    )
    return _oid_str(doc)


async def get_last_messages(session_id: str, limit: int = 5) -> list[dict[str, Any]]:
    cursor = collection("messages").find({"sessionId": session_id}).sort("timestamp", -1).limit(limit)
    messages: list[dict[str, Any]] = []
    async for doc in cursor:
        messages.append(_oid_str(doc))
    return list(reversed(messages))


async def set_session_typing(session_id: str, is_typing: bool) -> None:
    await collection("chat_sessions").update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"isTyping": is_typing, "updatedAt": datetime.utcnow()}},
    )


async def list_sessions_by_tenant(tenant_id: str) -> list[dict[str, Any]]:
    cursor = collection("chat_sessions").find({"tenantId": tenant_id}).sort("updatedAt", -1)
    sessions: list[dict[str, Any]] = []
    async for doc in cursor:
        sessions.append(_oid_str(doc))
    return sessions


async def get_session_with_messages(session_id: str) -> dict[str, Any] | None:
    try:
        doc = await collection("chat_sessions").find_one({"_id": ObjectId(session_id)})
    except Exception:
        return None
    if not doc:
        return None
    session = _oid_str(doc)
    messages = await get_last_messages(session_id, limit=100)
    session["messages"] = messages
    return session


async def count_active_sessions(tenant_id: str) -> int:
    return await collection("chat_sessions").count_documents({"tenantId": tenant_id, "status": "active"})


async def count_messages_today(tenant_id: str) -> int:
    start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    session_ids = []
    cursor = collection("chat_sessions").find({"tenantId": tenant_id})
    async for s in cursor:
        session_ids.append(str(s["_id"]))
    if not session_ids:
        return 0
    return await collection("messages").count_documents(
        {"sessionId": {"$in": session_ids}, "timestamp": {"$gte": start}}
    )


async def count_messages_by_type(tenant_id: str, media_type: str) -> int:
    session_ids = []
    cursor = collection("chat_sessions").find({"tenantId": tenant_id})
    async for s in cursor:
        session_ids.append(str(s["_id"]))
    if not session_ids:
        return 0
    return await collection("messages").count_documents(
        {"sessionId": {"$in": session_ids}, "mediaType": media_type, "sender": "ai"}
    )
