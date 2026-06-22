"""Media library API routes."""

from datetime import datetime
from typing import Any

from fastapi import APIRouter

from app.services.tenant_service import get_media_library, list_tenants

router = APIRouter(prefix="/media", tags=["media"])


@router.get("")
async def list_media(tenant: str | None = None) -> list[dict[str, Any]]:
    tenants = await list_tenants()
    if tenant:
        tenants = [t for t in tenants if t.get("tenantId") == tenant]

    assets: list[dict[str, Any]] = []
    for t in tenants:
        library = t.get("mediaLibrary", {})
        for key, url in library.items():
            is_doc = key in ("catalog", "invoice", "brochure") or url.endswith(".pdf")
            assets.append(
                {
                    "id": f"{t['tenantId']}_{key}",
                    "type": "document" if is_doc else "image",
                    "name": key,
                    "url": url,
                    "size": "—",
                    "uploadedAt": datetime.utcnow().isoformat(),
                    "tenantId": t["tenantId"],
                }
            )
    return assets
