"""Groq service for structured response generation."""

import json
import logging
import re
from typing import Any

from groq import Groq

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _client() -> Groq:
    settings = get_settings()
    return Groq(api_key=settings.groq_api_key)


def _normalize_response_type(response_type: str | None, user_message: str) -> str:
    if response_type in {"text", "image", "document"}:
        return response_type

    message = user_message.lower()
    if any(keyword in message for keyword in ("catalog", "pdf", "brochure", "invoice")):
        return "document"
    if any(keyword in message for keyword in ("image", "photo", "showroom", "picture", "see")):
        return "image"
    return "text"


def _select_media_asset(
    response_type: str,
    media_library: dict[str, str],
    media_key: str | None,
    media_url: str | None,
) -> tuple[str | None, str | None]:
    if media_key and media_key in media_library:
        return media_key, media_library[media_key]

    if response_type == "document":
        for key, url in media_library.items():
            if key in ("catalog", "invoice", "brochure"):
                return key, url

    if response_type == "image":
        for key, url in media_library.items():
            return key, url

    return media_key, media_url


def _fallback_response(user_message: str, media_library: dict[str, str]) -> dict[str, Any]:
    response_type = _normalize_response_type(None, user_message)
    media_key = None
    media_url = None

    if response_type == "document":
        media_key = next(iter(media_library), None)
        media_url = media_library.get(media_key or "", "")
    elif response_type == "image":
        for key, url in media_library.items():
            media_key = key
            media_url = url
            break

    return {
        "response_type": response_type,
        "content": "I’m having trouble generating a response right now.",
        "media_key": media_key,
        "media_url": media_url,
    }


def _build_messages(
    system_prompt: str,
    user_message: str,
    history: list[dict[str, Any]],
    media_library: dict[str, str],
    media_rules: str | None,
) -> list[dict[str, str]]:
    media_keys = ", ".join(media_library.keys()) if media_library else "none"
    rules = (
        "Respond ONLY with valid JSON and no markdown. Schema:\n"
        '{"response_type":"text|image|document","content":"message text",'
        '"media_key":"optional key from media library","media_url":"optional direct url"}\n'
        "Rules:\n"
        "- If customer asks for catalog or pdf -> document\n"
        "- If customer asks for image/photo/showroom -> image\n"
        "- Otherwise -> text\n"
        f"Media rules: {media_rules or 'Only send media that exists in the approved media library.'}\n"
        f"Available media library keys: {media_keys}"
    )

    messages: list[dict[str, str]] = [
        {"role": "system", "content": f"{system_prompt}\n\n{rules}".strip()},
    ]

    for item in history[-10:]:
        sender = str(item.get("sender", "user")).lower()
        role = "assistant" if sender == "ai" else "user"
        content = str(item.get("content", "")).strip()
        if content:
            messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})
    return messages


def _parse_response_content(raw_content: str) -> dict[str, Any]:
    cleaned = raw_content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


async def generate_structured_response(
    system_prompt: str,
    user_message: str,
    history: list[dict[str, Any]],
    media_library: dict[str, str],
    media_rules: str | None = None,
) -> dict[str, Any]:
    """
    Call Groq Chat Completions to generate a structured response.
    Returns: { response_type, content, media_key, media_url }.
    """
    settings = get_settings()
    if not settings.groq_api_key:
        logger.warning("Groq API key is not configured; using fallback response")
        return _fallback_response(user_message, media_library)

    messages = _build_messages(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        media_library=media_library,
        media_rules=media_rules,
    )

    logger.info(
        "Groq request prepared: model=%s history_messages=%d media_keys=%s user_message=%s",
        settings.groq_model,
        len(history[-10:]),
        ", ".join(media_library.keys()) if media_library else "none",
        user_message[:200],
    )
    logger.info("Groq request messages: %s", messages)

    try:
        client = _client()
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        raw_content = response.choices[0].message.content or "{}"
        logger.info("Groq raw response: %s", raw_content)

        try:
            parsed = _parse_response_content(raw_content)
        except Exception:
            logger.exception("Groq response was not valid JSON")
            return _fallback_response(user_message, media_library)

        response_type = _normalize_response_type(parsed.get("response_type"), user_message)
        media_key, media_url = _select_media_asset(
            response_type=response_type,
            media_library=media_library,
            media_key=parsed.get("media_key"),
            media_url=parsed.get("media_url"),
        )

        result = {
            "response_type": response_type,
            "content": parsed.get("content", ""),
            "media_key": media_key,
            "media_url": media_url,
        }
        logger.info(
            "Groq structured response: type=%s media_key=%s media_url=%s content=%s",
            result["response_type"],
            result["media_key"],
            result["media_url"],
            result["content"][:200],
        )
        logger.info(
            "Final WhatsApp reply prepared: type=%s content=%s media_url=%s",
            result["response_type"],
            result["content"][:200],
            result["media_url"],
        )
        return result
    except Exception as exc:
        logger.error("Groq call failed: %s", exc)
        return _fallback_response(user_message, media_library)
