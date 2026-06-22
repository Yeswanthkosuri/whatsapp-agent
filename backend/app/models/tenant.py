"""Tenant document model."""

from typing import Any

from pydantic import BaseModel, Field


class Tenant(BaseModel):
    tenant_id: str = Field(alias="tenantId")
    name: str
    system_prompt: str = Field(alias="systemPrompt")
    media_library: dict[str, str] = Field(default_factory=dict, alias="mediaLibrary")

    model_config = {"populate_by_name": True}


class TenantUpdate(BaseModel):
    name: str | None = None
    system_prompt: str | None = Field(default=None, alias="systemPrompt")
    media_rules: str | None = Field(default=None, alias="mediaRules")

    model_config = {"populate_by_name": True}


class TenantSettingsResponse(BaseModel):
    tenant_name: str = Field(alias="tenantName")
    system_prompt: str = Field(alias="systemPrompt")
    media_rules: str = Field(alias="mediaRules")

    model_config = {"populate_by_name": True}


class TenantListItem(BaseModel):
    id: str
    name: str
    plan: str = "Growth"
