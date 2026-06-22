"""WhatsApp webhook endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, Response

from app.core.config import get_settings
from app.langgraph.workflow import run_agent_workflow
from app.services.image_service import download_whatsapp_media
from app.services.whatsapp import extract_inbound_message, send_text, send_typing_indicator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


async def process_inbound_message(
    tenant_id: str,
    inbound: dict[str, Any],
) -> None:
    """Background task: run LangGraph workflow asynchronously."""
    phone = inbound.get("phone", "")
    message = inbound.get("content", "")
    message_id = inbound.get("message_id")
    message_type = inbound.get("message_type")
    media_id = inbound.get("media_id")
    media_mime_type = inbound.get("media_mime_type")
    caption = inbound.get("caption")
    image_url = inbound.get("image_url")
    customer_name = inbound.get("name")

    downloaded_media = None
    try:
        logger.info(
            "Scheduling workflow execution: tenant_id=%s phone=%s message_id=%s message_type=%s media_id=%s caption=%s",
            tenant_id,
            phone,
            message_id,
            message_type,
            media_id,
            caption,
        )
        if message_id:
            await send_typing_indicator(phone, message_id)

        if message_type == "image" and media_id:
            downloaded_media = await download_whatsapp_media(media_id)
            image_url = downloaded_media.source_url
            media_mime_type = downloaded_media.mime_type
            logger.info(
                "WhatsApp image downloaded: tenant_id=%s phone=%s media_id=%s mime_type=%s bytes=%s path=%s",
                tenant_id,
                phone,
                media_id,
                downloaded_media.mime_type,
                downloaded_media.size_bytes,
                downloaded_media.local_path,
            )

        await run_agent_workflow(
            tenant_id=tenant_id,
            phone=phone,
            message=message,
            message_id=message_id,
            customer_name=customer_name,
            message_type=message_type,
            media_id=media_id,
            media_mime_type=media_mime_type,
            caption=caption,
            image_url=image_url,
            image_path=str(downloaded_media.local_path) if downloaded_media else None,
        )
        logger.info(
            "Workflow finished for tenant_id=%s phone=%s message_type=%s media_id=%s",
            tenant_id,
            phone,
            message_type,
            media_id,
        )
    except Exception as exc:
        logger.exception("Workflow failed for %s: %s", phone, exc)
        if message_type == "image" and media_id:
            await send_text(
                phone,
                "Sorry, I couldn’t analyze that image right now. Please send a JPG or PNG image.",
            )
    finally:
        if downloaded_media:
            downloaded_media.cleanup()
            logger.info(
                "Cleaned up temporary media for tenant_id=%s phone=%s media_id=%s",
                tenant_id,
                phone,
                media_id,
            )


@router.get("/whatsapp")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
) -> Response:
    """Meta webhook verification handshake."""
    settings = get_settings()
    if hub_mode == "subscribe" and hub_verify_token == settings.verify_token:
        logger.info("Webhook verified successfully")
        return Response(content=hub_challenge or "", media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/whatsapp")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    """
    Receive inbound WhatsApp messages.
    Returns immediately; LangGraph runs in a background task.
    """
    payload = await request.json()
    logger.info("Webhook received: %s", payload.get("object"))

    inbound = extract_inbound_message(payload)
    if not inbound:
        return {"status": "ignored"}

    settings = get_settings()
    tenant_id = settings.default_tenant_id

    background_tasks.add_task(
        process_inbound_message,
        tenant_id,
        inbound,
    )
    logger.info(
        "Webhook message accepted: tenant_id=%s phone=%s message_type=%s media_id=%s image_url=%s caption=%s message_id=%s content=%s",
        tenant_id,
        inbound["phone"],
        inbound.get("message_type"),
        inbound.get("media_id"),
        inbound.get("image_url"),
        inbound.get("caption"),
        inbound.get("message_id"),
        inbound["content"][:200],
    )

    return {"status": "received"}
