"""LangGraph workflow state definition."""

from typing import Annotated, Any, Literal

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    tenant_id: str
    phone: str
    message: str
    message_type: Literal["text", "image", "document"]
    message_id: str | None
    customer_name: str | None
    session_id: str | None
    history: list[dict[str, Any]]
    response_type: Literal["text", "image", "document"]
    media_url: str | None
    media_id: str | None
    media_mime_type: str | None
    caption: str | None
    image_url: str | None
    image_path: str | None
    content: str | None
    media_key: str | None
    tenant: dict[str, Any]
    error: str | None
