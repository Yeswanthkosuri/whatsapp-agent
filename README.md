# Multi-Tenant WhatsApp AI Orchestrator

Production-ready **Multi-Tenant WhatsApp AI Support & Sales Agent SaaS** platform built with FastAPI, MongoDB Atlas, LangGraph, Groq, WhatsApp Cloud API, and a React dashboard.

## Project Overview

This platform enables multiple tenants (businesses) to run AI-powered WhatsApp support and sales agents. Each tenant has its own system prompt, media library, and conversation history. Incoming WhatsApp messages trigger a LangGraph workflow that acknowledges, reasons with Groq, and dispatches text, image, or document responses.

### Key capabilities

- Multi-tenant architecture with tenant switcher in the dashboard
- WhatsApp Cloud API webhook integration (verify + receive)
- LangGraph agent workflow (acknowledge → context → reasoning → dispatcher)
- Groq structured JSON responses (text / image / document)
- Real-time conversation viewer with typing indicators
- Media library and PDF attachment cards
- Campaign management UI
- Tenant settings (system prompt, media rules)
- Docker deployment for frontend + backend + MongoDB

## Architecture Diagram

```mermaid
flowchart TB
    subgraph Client
        WA[WhatsApp User]
        UI[React Dashboard]
    end

    subgraph Platform
        API[FastAPI Backend]
        LG[LangGraph Workflow]
        GROQ[Groq API]
        WAPI[WhatsApp Cloud API]
        DB[(MongoDB Atlas)]
    end

    WA -->|Inbound message| WAPI
    WAPI -->|Webhook POST| API
    API -->|Background task| LG
    LG -->|Fetch tenant + history| DB
    LG -->|Reasoning| GROQ
    LG -->|Send response| WAPI
    LG -->|Persist messages| DB
    UI -->|REST API| API
    API --> DB
```

## Folder Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # REST + webhook routes
│   │   ├── core/          # Config, database
│   │   ├── models/        # Pydantic models
│   │   ├── services/      # WhatsApp, Groq, tenant, chat
│   │   ├── langgraph/     # State, nodes, workflow
│   │   ├── seed/          # Database seeding
│   │   └── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── src/
│   ├── services/          # api.ts, chatService, tenantService
│   ├── hooks/             # useChats, useTenants
│   ├── pages/             # Dashboard, Conversations, etc.
│   ├── routes/            # TanStack Router file routes
│   └── components/        # Reusable UI components
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## LangGraph Flow

1. **acknowledge_node** — Save inbound message, mark as read, trigger typing indicator
2. **context_node** — Fetch tenant config and last 5 messages
3. **reasoning_node** — Call Groq; determine `text`, `image`, or `document`
4. **dispatcher_node** — Send via WhatsApp API, save outbound message

Prompt rules:
- `catalog` / `pdf` → document
- `image` / `photo` / `showroom` → image
- Otherwise → text

## MongoDB Setup

### Atlas (production)

1. Create a cluster at [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create database user and whitelist your IP (or `0.0.0.0/0` for cloud deploy)
3. Copy connection string to `MONGO_URI`:

```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/whatsapp_ai?retryWrites=true&w=majority
```

### Collections

| Collection       | Purpose                          |
|------------------|----------------------------------|
| `tenants`        | Tenant config + media library    |
| `chat_sessions`  | Conversation sessions            |
| `messages`       | Individual messages              |
| `campaigns`      | Broadcast campaigns (UI layer)     |

### Seed data

```bash
cd backend
pip install -r requirements.txt
python -m app.seed.seed_data
```

## Groq Setup

1. Get an API key from [Groq](https://console.groq.com/)
2. Set in `backend/.env`:

```env
GROQ_API_KEY=...
GROQ_MODEL=llama-3.3-70b-versatile
```

## WhatsApp Setup

1. Create a Meta Developer app with WhatsApp product
2. Configure webhook URL: `https://your-domain.com/api/webhooks/whatsapp`
3. Set verify token to match `VERIFY_TOKEN`
4. Subscribe to `messages` field
5. Configure credentials:

```env
WHATSAPP_TOKEN=your_permanent_token
PHONE_NUMBER_ID=your_phone_number_id
VERIFY_TOKEN=your_custom_verify_token
```

## Environment Variables

### Backend (`backend/.env`)

| Variable           | Description                    |
|--------------------|--------------------------------|
| `MONGO_URI`        | MongoDB connection string      |
| `GROQ_API_KEY`   | Groq API key                 |
| `WHATSAPP_TOKEN`   | WhatsApp Cloud API token       |
| `PHONE_NUMBER_ID`  | WhatsApp phone number ID       |
| `VERIFY_TOKEN`     | Webhook verification token     |
| `PORT`             | Server port (default 8000)     |
| `DEFAULT_TENANT_ID`| Default tenant for webhooks    |

### Frontend (`.env`)

| Variable              | Description              |
|-----------------------|--------------------------|
| `VITE_API_BASE_URL`   | FastAPI backend URL      |

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # edit with your values
python -m app.seed.seed_data
uvicorn app.main:app --reload --port 8000
```

Health check: http://localhost:8000/health

### Frontend

```bash
# from project root
cp .env.example .env
bun install   # or npm install
bun run dev   # or npm run dev
```

Dashboard: http://localhost:5173 (or port shown in terminal)

Without `VITE_API_BASE_URL`, the UI uses mock data. With it set to `http://localhost:8000`, the UI connects to the live API.

## Docker Deployment

```bash
# Copy and configure env files
cp backend/.env.example backend/.env
cp .env.example .env

# Build and run all services
docker compose up --build

# Seed database (first run)
docker compose exec backend python -m app.seed.seed_data
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- MongoDB: localhost:27017

## Render Deployment

### Backend (Web Service)

1. Connect repo, set root directory to `backend`
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `backend/.env.example`
5. Use MongoDB Atlas URI (not local Mongo)

### Frontend (Static Site or Web Service)

For TanStack Start SSR on Render, deploy as a Web Service with Docker using the root `Dockerfile`, or build statically if your deployment target supports it.

Set `VITE_API_BASE_URL` to your Render backend URL at build time.

## Vercel Deployment

### Frontend

1. Import project to Vercel
2. Set environment variable: `VITE_API_BASE_URL=https://your-api.onrender.com`
3. Build command: `npm run build` or `bun run build`
4. Deploy

### Backend

Vercel is not ideal for long-running FastAPI + LangGraph workloads. Deploy the backend to Render, Railway, or Fly.io and point the frontend to that URL.

## API Endpoints

| Method | Path                          | Description              |
|--------|-------------------------------|--------------------------|
| GET    | `/health`                     | Health check             |
| GET    | `/api/webhooks/whatsapp`      | Webhook verification     |
| POST   | `/api/webhooks/whatsapp`      | Receive WhatsApp events  |
| GET    | `/tenants`                    | List tenants             |
| GET    | `/conversations?tenant=`      | List conversations       |
| GET    | `/dashboard/stats?tenant=`    | Dashboard analytics      |
| GET    | `/media?tenant=`              | Media library            |
| GET    | `/settings/{tenantId}`        | Tenant settings          |
| PUT    | `/settings/{tenantId}`        | Update tenant settings   |
| GET    | `/campaigns?tenant=`          | List campaigns           |
| POST   | `/campaigns`                  | Create campaign          |

## License

MIT
