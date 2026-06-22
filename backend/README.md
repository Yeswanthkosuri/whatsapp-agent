# Backend — Multi-Tenant WhatsApp AI Orchestrator

FastAPI backend for the WhatsApp AI SaaS platform.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.seed.seed_data
uvicorn app.main:app --reload --port 8000
```

## Seed tenants

| Tenant ID | Name              | Media keys        |
|-----------|-------------------|-------------------|
| `tenantA` | Luxury Furniture  | catalog, sofa     |
| `tenantB` | Automotive Care   | invoice, repair   |

## Webhook testing

Verification:
```
GET /api/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=whatsapp_verify_token&hub.challenge=test
```

Use [ngrok](https://ngrok.com/) or similar to expose local port 8000 for Meta webhook configuration.

See the root [README](../README.md) for full documentation.
