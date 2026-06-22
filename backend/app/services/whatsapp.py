"""WhatsApp Cloud API integration layer."""

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


def _messages_url() -> str:
    settings = get_settings()
    return f"{GRAPH_API_BASE}/{settings.phone_number_id}/messages"


def _auth_headers() -> dict[str, str]:
    settings = get_settings()
    return {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }


async def _post_message(payload: dict[str, Any]) -> dict[str, Any]:
  """Send a request to the Meta WhatsApp Cloud API messages endpoint."""
  settings = get_settings()
  if not settings.whatsapp_token or not settings.phone_number_id:
    logger.warning("WhatsApp credentials not configured; skipping API call")
    return {"skipped": True, "payload": payload}

  # Meta WhatsApp Cloud API call occurs here:
  # POST https://graph.facebook.com/v21.0/{phone_number_id}/messages
  async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.post(_messages_url(), headers=_auth_headers(), json=payload)
    response.raise_for_status()
    data = response.json()
    logger.info("WhatsApp API response: %s", data)
    return data


async def send_text(to: str, body: str) -> dict[str, Any]:
    """Send a plain text message via WhatsApp Cloud API."""
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    return await _post_message(payload)


async def send_image(to: str, image_url: str, caption: str | None = None) -> dict[str, Any]:
    """Send an image message via WhatsApp Cloud API."""
    image_payload: dict[str, Any] = {"link": image_url}
    if caption:
        image_payload["caption"] = caption
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "image",
        "image": image_payload,
    }
    return await _post_message(payload)


async def send_document(
    to: str,
    document_url: str,
    filename: str | None = None,
    caption: str | None = None,
) -> dict[str, Any]:
    """Send a document (PDF) message via WhatsApp Cloud API."""
    document_payload: dict[str, Any] = {"link": document_url}
    if filename:
        document_payload["filename"] = filename
    if caption:
        document_payload["caption"] = caption
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "document",
        "document": document_payload,
    }
    return await _post_message(payload)


async def send_typing_indicator(to: str, message_id: str | None = None) -> dict[str, Any]:
    """Trigger typing indicator via WhatsApp Cloud API."""
    # Meta supports marking messages as read which shows activity; typing uses read + optional status.
    if message_id:
        return await mark_as_read(message_id)
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id or "",
    }
    settings = get_settings()
    if not settings.whatsapp_token:
        return {"skipped": True}
    url = f"{GRAPH_API_BASE}/{settings.phone_number_id}/messages"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, headers=_auth_headers(), json=payload)
        if response.status_code >= 400:
            logger.warning("Typing indicator fallback: %s", response.text)
            return {"skipped": True}
        return response.json()


async def mark_as_read(message_id: str) -> dict[str, Any]:
    """Mark an inbound message as read via WhatsApp Cloud API."""
    settings = get_settings()
    if not settings.whatsapp_token:
        return {"skipped": True}

    # Meta WhatsApp Cloud API call for marking messages as read:
    # POST https://graph.facebook.com/v21.0/{phone_number_id}/messages
    payload = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(_messages_url(), headers=_auth_headers(), json=payload)
        if response.status_code >= 400:
            logger.warning("Mark as read failed: %s", response.text)
            return {"error": response.text}
        return response.json()


def extract_inbound_message(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Parse WhatsApp webhook payload into a normalized inbound message."""
    try:
        entry = payload.get("entry", [])[0]
        change = entry.get("changes", [])[0]
        value = change.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return None
        message = messages[0]
        msg_type = message.get("type", "text")
        content = ""
        media_id = None
        media_type = None
        caption = None
        mime_type = None
        image_url = None

        if msg_type == "text":
            content = message.get("text", {}).get("body", "")
        elif msg_type == "image":
            media_type = "image"
            image_payload = message.get("image", {})
            caption = image_payload.get("caption")
            content = caption or "Image received"
            media_id = image_payload.get("id")
            mime_type = image_payload.get("mime_type")
            image_url = image_payload.get("link")
        elif msg_type == "document":
            media_type = "document"
            document_payload = message.get("document", {})
            content = document_payload.get("filename", "Document")
            media_id = document_payload.get("id")
            mime_type = document_payload.get("mime_type")

        contact = value.get("contacts", [{}])[0]
        name = contact.get("profile", {}).get("name", "Customer")

        return {
            "message_id": message.get("id"),
            "phone": message.get("from"),
            "name": name,
            "content": content,
            "message_type": msg_type,
            "media_id": media_id,
            "media_type": media_type,
            "caption": caption,
            "media_mime_type": mime_type,
            "image_url": image_url,
            "timestamp": message.get("timestamp"),
        }
    except (IndexError, KeyError, TypeError) as exc:
        logger.error("Failed to parse webhook payload: %s", exc)
        return None
