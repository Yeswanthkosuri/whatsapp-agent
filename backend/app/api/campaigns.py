"""Campaign API routes (UI persistence layer)."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from app.core.database import collection

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("")
async def list_campaigns(tenant: str) -> list[dict[str, Any]]:
    cursor = collection("campaigns").find({"tenantId": tenant})
    campaigns: list[dict[str, Any]] = []
    async for doc in cursor:
        doc.pop("_id", None)
        doc["id"] = doc.get("id", str(doc.get("_id", "")))
        campaigns.append(doc)
    return campaigns


@router.post("")
async def create_campaign(payload: dict[str, Any]) -> dict[str, Any]:
    doc = {
        "id": f"cm{int(datetime.utcnow().timestamp())}",
        "name": payload.get("name", ""),
        "tenantId": payload.get("tenantId", ""),
        "audience": payload.get("audience", ""),
        "template": payload.get("template", ""),
        "status": "scheduled",
        "recipients": 0,
    }
    await collection("campaigns").insert_one(doc)
    doc.pop("_id", None)
    return doc
