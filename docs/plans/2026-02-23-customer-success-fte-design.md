# Customer Success Digital FTE - Design Document

**Date:** 2026-02-23
**Project:** CRM Digital FTE Factory - Hackathon 5
**Status:** Approved

## Purpose

Build a 24/7 AI Customer Success employee (Digital FTE) that handles customer support inquiries across Email (Gmail), WhatsApp, and Web Form channels. The system uses PostgreSQL as a custom CRM, OpenAI Agents SDK for AI processing, Kafka for event streaming, and Kubernetes for deployment.

## Architecture

### System Components

```
Channels (Gmail, WhatsApp, Web Form)
    -> FastAPI Webhook/API Endpoints
        -> Kafka Event Streaming
            -> Agent Worker (OpenAI Agents SDK)
                -> PostgreSQL (CRM State)
            -> Channel Response Handlers
```

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend API | FastAPI (Python) | Webhook endpoints, REST API |
| AI Agent | OpenAI Agents SDK | Customer query processing |
| Database/CRM | PostgreSQL 16 + pgvector | Customer data, tickets, knowledge base |
| Event Streaming | Apache Kafka (aiokafka) | Decouple channel intake from processing |
| Web Form | Next.js + React | Standalone support form component |
| Containerization | Docker + docker-compose | Local development |
| Orchestration | Kubernetes | Production deployment |
| Email | Gmail API + Pub/Sub | Email channel integration |
| WhatsApp | Twilio WhatsApp API | WhatsApp channel integration |

### Mock-First Strategy

All external services are abstracted behind interfaces. Mock implementations are provided for development without API keys:

- **OpenAI** -> Keyword-based response generator
- **Gmail API** -> Logs to database
- **Twilio API** -> Logs to database
- **Kafka** -> Real in docker-compose, in-memory fallback

## Database Schema (CRM System)

Core tables:
- `customers` - Unified customer records across channels
- `customer_identifiers` - Cross-channel identity mapping (email, phone, whatsapp)
- `conversations` - Conversation threads with channel tracking
- `messages` - All messages with channel metadata and delivery status
- `tickets` - Support tickets with lifecycle tracking
- `knowledge_base` - Product docs with pgvector embeddings for semantic search
- `channel_configs` - Per-channel settings (response templates, limits)
- `agent_metrics` - Performance tracking per channel

## Agent Design

### Tools (5 required)
1. `search_knowledge_base` - Semantic search over product docs
2. `create_ticket` - Log interaction with channel source
3. `get_customer_history` - Cross-channel history lookup
4. `escalate_to_human` - Hand off with full context
5. `send_response` - Channel-appropriate reply delivery

### Channel-Aware Response Formatting
- **Email**: Formal, detailed, greeting + signature, max 500 words
- **WhatsApp**: Conversational, concise, max 300 chars preferred
- **Web Form**: Semi-formal, balanced detail, max 300 words

### Guardrails
- Never discuss pricing (escalate)
- Never promise undocumented features
- Never process refunds (escalate)
- Always create ticket before responding
- Always check sentiment before closing

### Escalation Triggers
- Legal language detected
- Profanity/aggressive language (sentiment < 0.3)
- 2+ failed knowledge base searches
- Customer requests human help
- WhatsApp keywords: "human", "agent", "representative"

## Channel Integrations

### Gmail
- Gmail API with Pub/Sub push notifications
- Webhook handler at `/webhooks/gmail`
- Reply via Gmail API (same thread)

### WhatsApp
- Twilio WhatsApp API
- Webhook handler at `/webhooks/whatsapp` with signature validation
- Reply via Twilio messages API
- Status callbacks at `/webhooks/whatsapp/status`

### Web Form (Required Build)
- Next.js React component
- Form fields: name, email, subject, category, priority, message
- Client-side validation
- POST to `/support/submit`
- Ticket status checking at `/support/ticket/{id}`
- Success state with ticket ID display

## Kafka Topics

| Topic | Purpose |
|-------|---------|
| `fte.tickets.incoming` | Unified intake from all channels |
| `fte.channels.email.inbound` | Email-specific events |
| `fte.channels.whatsapp.inbound` | WhatsApp-specific events |
| `fte.channels.webform.inbound` | Web form events |
| `fte.escalations` | Escalation events for human agents |
| `fte.metrics` | Performance metrics |
| `fte.dlq` | Dead letter queue for failures |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | Health check with channel status |
| POST | `/webhooks/gmail` | Gmail Pub/Sub notifications |
| POST | `/webhooks/whatsapp` | Twilio WhatsApp messages |
| POST | `/webhooks/whatsapp/status` | WhatsApp delivery status |
| POST | `/support/submit` | Web form submission |
| GET | `/support/ticket/{id}` | Ticket status |
| GET | `/conversations/{id}` | Conversation history |
| GET | `/customers/lookup` | Customer search by email/phone |
| GET | `/metrics/channels` | Per-channel metrics |

## Build Order

1. Context dossier (company docs, sample tickets, brand voice)
2. PostgreSQL database schema + seed data
3. Core agent (OpenAI SDK, tools, prompts, formatters)
4. Channel handlers (Gmail, WhatsApp, Web Form)
5. FastAPI service + Kafka event streaming
6. Next.js Web Support Form
7. Docker, docker-compose, Kubernetes manifests
8. Tests (unit, E2E, load)
9. Specs and documentation

## Performance Requirements

- Response time: <3s processing, <30s delivery
- Accuracy: >85% on test set
- Escalation rate: <20%
- Cross-channel identification: >95%
- Uptime: >99.9%

## Non-Goals

- External CRM integration (Salesforce, HubSpot)
- Full website (only the support form)
- Production WhatsApp Business account (Twilio Sandbox sufficient)
- Real-time chat widget (web form is async)
