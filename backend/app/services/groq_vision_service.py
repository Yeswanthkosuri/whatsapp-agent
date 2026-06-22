"""Groq vision adapter for image-aware structured responses."""

import base64
import json
import logging
import mimetypes
import re
from pathlib import Path
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

    lower = user_message.lower()
    if any(keyword in lower for keyword in ("catalog", "pdf", "brochure", "invoice")):
        return "document"
    if any(keyword in lower for keyword in ("showroom image", "product image", "repair diagram", "image", "photo", "picture", "see")):
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
            if key not in ("catalog", "invoice", "brochure"):
                return key, url

    return media_key, media_url


def _parse_json_payload(raw: str) -> dict[str, Any]:
    cleaned = raw.strip()
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


def _image_data_url(image_path: str, mime_type: str | None) -> str:
    path = Path(image_path)
    guessed_mime_type, _ = mimetypes.guess_type(path.name)
    resolved_mime_type = mime_type or guessed_mime_type or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{resolved_mime_type};base64,{encoded}"


def _build_messages(
    system_prompt: str,
    user_message: str,
    history: list[dict[str, Any]],
    image_path: str,
    mime_type: str | None,
    media_library: dict[str, str],
    media_rules: str | None,
    caption: str | None,
) -> list[dict[str, Any]]:
    media_keys = ", ".join(media_library.keys()) if media_library else "none"
    rules = (
        "You are a vision-enabled WhatsApp assistant.\n"
        "Analyze the image, answer the user's question, and respond ONLY with valid JSON and no markdown.\n"
        '{"response_type":"text|image|document","content":"message text",'
        '"media_key":"optional key from media library","media_url":"optional direct url"}\n'
        "Rules:\n"
        "- Describe what is visible in the image clearly and concisely.\n"
        "- Use the caption/question as the user's intent when present.\n"
        "- If the user asks for catalog or pdf -> document\n"
        "- If the user asks for showroom image, product image, or repair diagram -> image\n"
        "- Otherwise -> text\n"
        f"Media rules: {media_rules or 'Only send media that exists in the approved media library.'}\n"
        f"Available media library keys: {media_keys}"
    )

    messages: list[dict[str, Any]] = [{"role": "system", "content": f"{system_prompt}\n\n{rules}".strip()}]

    for item in history[-10:]:
        sender = str(item.get("sender", "user")).lower()
        role = "assistant" if sender == "ai" else "user"
        content = str(item.get("content", "")).strip()
        if content:
            messages.append({"role": role, "content": content})

    prompt_text = [
        f"User request: {user_message or 'Analyze this image.'}",
        f"Caption: {caption or 'none'}",
        "Provide a structured answer for the WhatsApp customer.",
    ]

    messages.append(
        {
            "role": "user",
            "content": (
                f"{' '.join(prompt_text)}\n\n"
                f"Image (base64 data URL): {_image_data_url(image_path, mime_type)}"
            ),
        }
    )
    return messages


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
        "content": "I’m unable to analyze the image right now, but I can still help with the message.",
        "media_key": media_key,
        "media_url": media_url,
    }


async def analyze_image(
    system_prompt: str,
    user_message: str,
    history: list[dict[str, Any]],
    image_path: str,
    media_library: dict[str, str],
    media_rules: str | None = None,
    caption: str | None = None,
    mime_type: str | None = None,
) -> dict[str, Any]:
    """Send an image and caption context to Groq Vision and return a structured response."""
    settings = get_settings()
    if not settings.groq_api_key:
        logger.warning("Groq API key is not configured; using vision fallback response")
        return _fallback_response(user_message or caption or "", media_library)

    messages = _build_messages(
        system_prompt=system_prompt,
        user_message=user_message,
        history=history,
        image_path=image_path,
        mime_type=mime_type,
        media_library=media_library,
        media_rules=media_rules,
        caption=caption,
    )

    logger.info(
        "Groq vision request prepared: model=%s history_messages=%d media_keys=%s image_path=%s mime_type=%s caption=%s user_message=%s",
        settings.groq_model,
        len(history[-10:]),
        ", ".join(media_library.keys()) if media_library else "none",
        image_path,
        mime_type,
        caption,
        user_message[:200],
    )
    logger.info("Groq vision request messages: %s", messages)

    try:
        client = _client()
        logger.info("Groq model being used for vision: %s", settings.groq_model)
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        raw_content = response.choices[0].message.content or "{}"
        logger.info("Groq vision raw response: %s", raw_content)

        try:
            parsed = _parse_json_payload(raw_content)
        except Exception:
            logger.exception("Groq vision response was not valid JSON")
            return _fallback_response(user_message or caption or "", media_library)

        response_type = _normalize_response_type(parsed.get("response_type"), user_message or caption or "")
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
            "Groq vision structured response: type=%s media_key=%s media_url=%s content=%s",
            result["response_type"],
            result["media_key"],
            result["media_url"],
            result["content"][:200],
        )
        return result
    except Exception as exc:
        logger.error("Groq vision call failed: %s", exc)
        return _fallback_response(user_message or caption or "", media_library)
