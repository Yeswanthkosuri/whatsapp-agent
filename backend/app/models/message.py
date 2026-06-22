"""Message document model."""

from datetime import datetime

from pydantic import BaseModel, Field


class Message(BaseModel):
    session_id: str = Field(alias="sessionId")
    sender: str
    content: str
    media_url: str | None = Field(default=None, alias="mediaUrl")
    media_type: str | None = Field(default=None, alias="mediaType")
    message_type: str | None = Field(default=None, alias="messageType")
    media_id: str | None = Field(default=None, alias="mediaId")
    caption: str | None = None
    image_url: str | None = Field(default=None, alias="imageUrl")
    media_mime_type: str | None = Field(default=None, alias="mediaMimeType")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
