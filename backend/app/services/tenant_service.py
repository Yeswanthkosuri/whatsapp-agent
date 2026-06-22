"""Tenant CRUD and lookup operations."""

import logging
from typing import Any

from app.core.database import collection

logger = logging.getLogger(__name__)


async def get_tenant_by_id(tenant_id: str) -> dict[str, Any] | None:
    doc = await collection("tenants").find_one({"tenantId": tenant_id})
    if doc:
        doc.pop("_id", None)
    return doc


async def list_tenants() -> list[dict[str, Any]]:
    cursor = collection("tenants").find()
    tenants: list[dict[str, Any]] = []
    async for doc in cursor:
        doc.pop("_id", None)
        tenants.append(doc)
    return tenants


async def update_tenant(tenant_id: str, updates: dict[str, Any]) -> dict[str, Any] | None:
    col = collection("tenants")
    result = await col.update_one({"tenantId": tenant_id}, {"$set": updates})
    if result.matched_count == 0:
        return None
    doc = await col.find_one({"tenantId": tenant_id})
    if doc:
        doc.pop("_id", None)
    return doc


async def get_media_library(tenant_id: str) -> dict[str, str]:
    tenant = await get_tenant_by_id(tenant_id)
    if not tenant:
        return {}
    return tenant.get("mediaLibrary", {})
