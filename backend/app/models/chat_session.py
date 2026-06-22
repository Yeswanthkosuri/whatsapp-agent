"""Chat session document model."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatSession(BaseModel):
    phone: str
    tenant_id: str = Field(alias="tenantId")
    status: str = "active"
    created_at: datetime = Field(default_factory=datetime.utcnow, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, alias="updatedAt")
    name: str | None = None
    unread: int = 0
    is_typing: bool = Field(default=False, alias="isTyping")

    model_config = {"populate_by_name": True}


class ChatSessionResponse(BaseModel):
    id: str
    phone: str
    name: str
    tenant_id: str = Field(alias="tenantId")
    last_activity: datetime = Field(alias="lastActivity")
    status: str
    unread: int
    messages: list[dict] = Field(default_factory=list)
    is_typing: bool = Field(default=False, alias="isTyping")

    model_config = {"populate_by_name": True}
