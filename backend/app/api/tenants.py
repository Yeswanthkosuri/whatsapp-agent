"""Tenant API routes."""

from fastapi import APIRouter

from app.models.tenant import TenantListItem
from app.services.tenant_service import list_tenants

router = APIRouter(prefix="/tenants", tags=["tenants"])

PLAN_MAP = {"tenantA": "Growth", "tenantB": "Scale"}


@router.get("", response_model=list[TenantListItem])
async def get_tenants() -> list[TenantListItem]:
    tenants = await list_tenants()
    return [
        TenantListItem(
            id=t["tenantId"],
            name=t["name"],
            plan=PLAN_MAP.get(t["tenantId"], "Growth"),
        )
        for t in tenants
    ]
