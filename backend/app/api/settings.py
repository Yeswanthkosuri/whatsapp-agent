"""Settings API routes."""

from fastapi import APIRouter, HTTPException

from app.models.tenant import TenantSettingsResponse, TenantUpdate
from app.services.tenant_service import get_tenant_by_id, update_tenant

router = APIRouter(prefix="/settings", tags=["settings"])

DEFAULT_MEDIA_RULES = (
    "Only send images under 5MB. PDF attachments must be from the approved media library."
)


@router.get("/{tenant_id}", response_model=TenantSettingsResponse)
async def get_settings(tenant_id: str) -> TenantSettingsResponse:
    tenant = await get_tenant_by_id(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return TenantSettingsResponse(
        tenantName=tenant.get("name", ""),
        systemPrompt=tenant.get("systemPrompt", ""),
        mediaRules=tenant.get("mediaRules", DEFAULT_MEDIA_RULES),
    )


@router.put("/{tenant_id}")
async def update_settings(tenant_id: str, payload: TenantUpdate) -> dict:
    updates: dict = {}
    if payload.name:
        updates["name"] = payload.name
    if payload.system_prompt:
        updates["systemPrompt"] = payload.system_prompt
    if payload.media_rules:
        updates["mediaRules"] = payload.media_rules

    if not updates:
        return {"ok": True}

    result = await update_tenant(tenant_id, updates)
    if not result:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"ok": True}
