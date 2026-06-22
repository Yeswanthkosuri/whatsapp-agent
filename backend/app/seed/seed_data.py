"""Database seeding script."""

import asyncio
import logging

from app.core.config import get_settings
from app.core.database import close_db, connect_db, collection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SEED_TENANTS = [
    {
        "tenantId": "tenantA",
        "name": "Luxury Furniture",
        "systemPrompt": "You are a luxury furniture assistant.",
        "mediaLibrary": {
            "catalog": "https://example.com/catalog.pdf",
            "sofa": "https://picsum.photos/400",
        },
        "mediaRules": "Only send images under 5MB. PDF attachments must be from the approved media library.",
    },
    {
        "tenantId": "tenantB",
        "name": "Automotive Care",
        "systemPrompt": "You are an automotive care assistant.",
        "mediaLibrary": {
            "invoice": "https://example.com/invoice.pdf",
            "repair": "https://picsum.photos/500",
        },
        "mediaRules": "Only send images under 5MB. PDF attachments must be from the approved media library.",
    },
]

SEED_CAMPAIGNS = [
    {
        "id": "cm1",
        "name": "Spring Collection Launch",
        "tenantId": "tenantA",
        "audience": "All customers",
        "template": "spring_sale_v2",
        "status": "sent",
        "recipients": 1240,
    },
    {
        "id": "cm2",
        "name": "Service Reminder",
        "tenantId": "tenantB",
        "audience": "Upcoming this week",
        "template": "service_followup",
        "status": "scheduled",
        "recipients": 312,
    },
]


async def seed() -> None:
    settings = get_settings()
    await connect_db()
    tenants_col = collection("tenants")

    for tenant in SEED_TENANTS:
        await tenants_col.update_one(
            {"tenantId": tenant["tenantId"]},
            {"$set": tenant},
            upsert=True,
        )
        logger.info("Seeded tenant: %s", tenant["tenantId"])

    campaigns_col = collection("campaigns")
    for campaign in SEED_CAMPAIGNS:
        await campaigns_col.update_one(
            {"id": campaign["id"]},
            {"$set": campaign},
            upsert=True,
        )
        logger.info("Seeded campaign: %s", campaign["id"])

    logger.info("Seed complete for database: %s", settings.mongo_db_name)
    await close_db()


if __name__ == "__main__":
    asyncio.run(seed())
