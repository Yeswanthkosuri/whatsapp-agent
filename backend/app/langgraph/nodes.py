"""LangGraph workflow nodes."""

import logging
from typing import Any

from app.langgraph.state import AgentState
from app.services.chat_service import (
    get_last_messages,
    get_or_create_session,
    save_message,
    set_session_typing,
)
from app.services.groq_vision_service import analyze_image
from app.services.openai_service import generate_structured_response
from app.services.tenant_service import get_tenant_by_id
from app.services.whatsapp import mark_as_read, send_document, send_image, send_text, send_typing_indicator

logger = logging.getLogger(__name__)


async def acknowledge_node(state: AgentState) -> dict[str, Any]:
    """Save inbound message, mark as read, and trigger typing indicator."""
    tenant_id = state.get("tenant_id", "")
    phone = state.get("phone", "")
    message = state.get("message", "")
    message_id = state.get("message_id")
    customer_name = state.get("customer_name")

    session = await get_or_create_session(phone, tenant_id, customer_name)
    session_id = session["id"]

    await save_message(
        session_id=session_id,
        sender="user",
        content=message,
        media_url=state.get("media_url"),
        media_type=state.get("response_type"),
    )

    if message_id:
        await mark_as_read(message_id)
    await send_typing_indicator(phone, message_id)
    await set_session_typing(session_id, True)

    return {"session_id": session_id}


async def context_node(state: AgentState) -> dict[str, Any]:
    """Fetch tenant configuration and recent conversation history."""
    tenant_id = state.get("tenant_id", "")
    session_id = state.get("session_id")

    tenant = await get_tenant_by_id(tenant_id)
    if not tenant:
        return {"error": f"Tenant {tenant_id} not found", "tenant": {}}

    history: list[dict[str, Any]] = []
    if session_id:
        history = await get_last_messages(session_id, limit=5)

    return {"tenant": tenant, "history": history}


async def reasoning_node(state: AgentState) -> dict[str, Any]:
    """Call Groq to generate the outbound response."""

    tenant = state.get("tenant", {}) or {}
    history = state.get("history", []) or []
    system_prompt = tenant.get("systemPrompt", "")
    media_library = tenant.get("mediaLibrary", {}) or {}
    media_rules = tenant.get("mediaRules")
    message_type = state.get("message_type", "text")
    caption = state.get("caption")
    image_path = state.get("image_path")
    image_url = state.get("image_url")
    logger.info(
        "Reasoning node input: tenant_id=%s message_type=%s media_id=%s image_url=%s caption=%s image_path=%s",
        state.get("tenant_id", ""),
        message_type,
        state.get("media_id"),
        image_url,
        caption,
        image_path,
    )

    if message_type == "image" and image_path:
        result = await analyze_image(
            system_prompt=system_prompt,
            user_message=caption or state.get("message", ""),
            history=history,
            image_path=image_path,
            media_library=media_library,
            media_rules=media_rules,
            caption=caption,
            mime_type=state.get("media_mime_type"),
        )
    else:
        result = await generate_structured_response(
            system_prompt=system_prompt,
            user_message=state.get("message", ""),
            history=history,
            media_library=media_library,
            media_rules=media_rules,
        )
    return result


async def dispatcher_node(state: AgentState) -> dict[str, Any]:
    """Send outbound message via WhatsApp and persist to database."""
    phone = state.get("phone", "")
    session_id = state.get("session_id")
    response_type = state.get("response_type", "text")
    content = state.get("content", "")
    media_url = state.get("media_url")

    media_type: str | None = None

    try:
        if response_type == "image" and media_url:
            await send_image(phone, media_url, caption=content)
            media_type = "image"
        elif response_type == "document" and media_url:
            filename = media_url.split("/")[-1] or "document.pdf"
            await send_document(phone, media_url, filename=filename, caption=content)
            media_type = "document"
        else:
            await send_text(phone, content)
            response_type = "text"
    except Exception as exc:
        logger.error("Failed to send WhatsApp message: %s", exc)
        await send_text(phone, content or "I’m having trouble sending a reply right now.")
        response_type = "text"
        media_type = None
        media_url = None

    if session_id:
        await save_message(
            session_id=session_id,
            sender="ai",
            content=content,
            media_url=media_url,
            media_type=media_type or response_type if response_type != "text" else None,
        )
        await set_session_typing(session_id, False)

    return {"response_type": response_type, "media_url": media_url, "content": content}
