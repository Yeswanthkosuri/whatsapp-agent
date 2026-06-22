"""WhatsApp image download and temporary storage helpers."""

import logging
import mimetypes
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v21.0"
SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}
DEFAULT_MAX_IMAGE_BYTES = 8 * 1024 * 1024
TEMP_MEDIA_DIR = Path(tempfile.gettempdir()) / "whatsapp-agent-media"
TEMP_MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class DownloadedMedia:
    media_id: str
    source_url: str
    local_path: Path
    mime_type: str
    size_bytes: int
    filename: str

    def cleanup(self) -> None:
        try:
            self.local_path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Failed to cleanup temporary media: %s", self.local_path)


def _auth_headers() -> dict[str, str]:
    settings = get_settings()
    return {
        "Authorization": f"Bearer {settings.whatsapp_token}",
        "Content-Type": "application/json",
    }


async def get_media_metadata(media_id: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.whatsapp_token or not settings.phone_number_id:
        raise RuntimeError("WhatsApp credentials are not configured")

    url = f"{GRAPH_API_BASE}/{media_id}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, headers=_auth_headers())
        response.raise_for_status()
        metadata = response.json()
        logger.info("WhatsApp media metadata retrieved: media_id=%s metadata=%s", media_id, metadata)
        return metadata


async def download_whatsapp_media(
    media_id: str,
    max_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
) -> DownloadedMedia:
    metadata = await get_media_metadata(media_id)
    source_url = metadata.get("url")
    mime_type = metadata.get("mime_type") or ""

    if not source_url:
        raise RuntimeError(f"WhatsApp media URL missing for media_id={media_id}")
    if mime_type not in SUPPORTED_IMAGE_MIME_TYPES:
        raise ValueError(f"Unsupported image MIME type: {mime_type or 'unknown'}")

    suffix = mimetypes.guess_extension(mime_type) or ".jpg"
    local_path = TEMP_MEDIA_DIR / f"{media_id}{suffix}"

    content_length = metadata.get("file_size")
    if isinstance(content_length, int) and content_length > max_bytes:
        raise ValueError(f"Image exceeds size limit: {content_length} bytes")

    downloaded_size = 0
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        async with client.stream("GET", source_url, headers=_auth_headers()) as response:
            response.raise_for_status()
            response_mime = response.headers.get("content-type", mime_type).split(";")[0].strip()
            if response_mime not in SUPPORTED_IMAGE_MIME_TYPES:
                raise ValueError(f"Unsupported image MIME type: {response_mime}")

            with local_path.open("wb") as file_handle:
                async for chunk in response.aiter_bytes():
                    downloaded_size += len(chunk)
                    if downloaded_size > max_bytes:
                        file_handle.close()
                        local_path.unlink(missing_ok=True)
                        raise ValueError(f"Image exceeds size limit: {max_bytes} bytes")
                    file_handle.write(chunk)

    filename = local_path.name
    logger.info(
        "WhatsApp media downloaded: media_id=%s path=%s size_bytes=%s mime_type=%s",
        media_id,
        local_path,
        downloaded_size,
        mime_type,
    )
    return DownloadedMedia(
        media_id=media_id,
        source_url=source_url,
        local_path=local_path,
        mime_type=mime_type,
        size_bytes=downloaded_size,
        filename=filename,
    )
