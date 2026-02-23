# Customer Success Digital FTE

> 24/7 AI-powered Customer Success Agent that handles support across Email, WhatsApp, and Web Form channels -- built for CRM Digital FTE Factory Hackathon 5.

![Python 3.11](https://img.shields.io/badge/python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![OpenAI Agents SDK](https://img.shields.io/badge/OpenAI_Agents_SDK-0.0.7-purple)
![License: MIT](https://img.shields.io/badge/license-MIT-yellow)

---

## Overview

Customer Success Digital FTE is a fully autonomous AI support agent that replaces Tier-1 customer support. It receives inbound messages from **Gmail**, **WhatsApp (Twilio)**, and a **Web Form**, processes them through an event-driven pipeline, resolves queries using a pgvector-backed knowledge base, and responds on the original channel -- all without human intervention.

**The problem:** Support teams are overwhelmed, response times are slow, and 24/7 coverage is expensive. This Digital FTE handles the repetitive 80% of tickets autonomously while escalating the complex 20% to human agents.

**Key capabilities:** Omni-channel intake, AI response generation (GPT-4o), semantic knowledge search, automatic ticket creation and categorization, guardrailed escalation, and full mock mode for demos without API keys.

---

## Architecture

```
                     +----------------------+
                     |   Inbound Channels   |
           +---------+----------+-----------+
           |                    |                    |
    Gmail Pub/Sub       Twilio Webhook        Next.js Form
    /webhooks/gmail     /webhooks/whatsapp    /support/submit
           |                    |                    |
           +---------+----------+-----------+
                     v                      v
              +------------+         +------------+
              | Kafka /    |         | PostgreSQL  |
              | InMemory   |         | + pgvector  |
              | Event Bus  |         | CRM Store   |
              +-----+------+         +------+------+
                    v                        |
             +------+-------+               |
             |  Message     |<--------------+
             |  Processor   |  (read/write)
             +------+-------+
                    |
          +---------+---------+
          |                   |
    +-----+------+     +-----+------+
    | OpenAI     |     | Mock       |
    | Agent      |     | Agent      |
    | (GPT-4o)   |     | (Fallback) |
    +-----+------+     +-----+------+
          +---------+---------+
                    v
          +-------------------+        Channel Response
          | 5 Agent Tools     | -----> (Email / WhatsApp / Web)
          +-------------------+
```

---

## Tech Stack

| Layer            | Technology                        | Purpose                              |
|------------------|-----------------------------------|--------------------------------------|
| API Framework    | FastAPI 0.115                     | Webhook endpoints, REST API          |
| AI Agent         | OpenAI Agents SDK 0.0.7 (GPT-4o) | Autonomous agent with tool use       |
| Database         | PostgreSQL 16 + pgvector          | CRM data, knowledge base, vectors   |
| Event Streaming  | Apache Kafka (aiokafka)           | Async message pipeline               |
| Email Channel    | Gmail API + Pub/Sub               | Inbound/outbound email               |
| WhatsApp Channel | Twilio WhatsApp API               | Inbound/outbound messaging           |
| Web Form         | Next.js + Tailwind CSS            | Customer-facing support form         |
| MCP Server       | Model Context Protocol            | Tool exposure for Claude Desktop     |
| Containerization | Docker + docker-compose           | Local development environment        |
| Orchestration    | Kubernetes (k8s manifests)        | Production deployment                |
| Testing          | pytest + Locust                   | Unit, integration, and load testing  |
| Logging          | structlog                         | Structured JSON logging              |

---

## Project Structure

```
customer-success-fte/
|-- src/
|   |-- api/main.py                    # FastAPI app, webhooks, REST endpoints
|   |-- agent/
|   |   |-- customer_success_agent.py  # OpenAI Agent + MockAgent
|   |   |-- prompts.py                # System prompts per channel
|   |   |-- tools.py                  # 5 @function_tool definitions
|   |   +-- formatters.py             # Channel-specific response formatters
|   |-- channels/
|   |   |-- gmail_handler.py          # Gmail Pub/Sub integration
|   |   |-- whatsapp_handler.py       # Twilio WhatsApp integration
|   |   +-- web_form_handler.py       # Web form router + validation
|   |-- database/
|   |   |-- connection.py             # asyncpg connection pool
|   |   |-- queries.py                # All database operations
|   |   |-- schema.sql                # PostgreSQL + pgvector schema
|   |   +-- seed.py                   # Sample data seeder
|   |-- workers/message_processor.py  # Kafka consumer + agent orchestrator
|   |-- kafka_client.py               # Producer/consumer + InMemory fallback
|   |-- mcp_server.py                 # MCP tool server for Claude Desktop
|   +-- config.py                     # Environment-based configuration
|-- web-form/                         # Next.js customer support form
|-- context/                          # Agent knowledge context files
|-- tests/                            # Unit, integration, e2e, load tests
|-- k8s/                              # Kubernetes manifests (9 files)
|-- docker-compose.yml
|-- Dockerfile
|-- requirements.txt
+-- .env.example
```

---

## Quick Start

**Prerequisites:** Docker and Docker Compose, Python 3.11+, Node.js 18+ (optional, for web form).

### 1. Clone and configure

```bash
git clone <repository-url> && cd customer-success-fte
cp .env.example .env
# Edit .env with your API keys, or leave defaults for mock mode
```

### 2. Start all services

```bash
docker-compose up -d
```

This starts **PostgreSQL 16** (port 5432), **Kafka** (port 29092), **FastAPI API** (port 8000), and the **Worker**.

### 3. Seed the database

```bash
docker-compose --profile seed up seed
```

### 4. Verify

```bash
curl http://localhost:8000/health
# Returns: { "status": "healthy", "channels": { "email": "active", ... } }
```

### 5. Web form (optional)

```bash
cd web-form && npm install && npm run dev
# Available at http://localhost:3000
```

---

## Channel Setup

### Gmail
1. Enable Gmail API in Google Cloud, configure Pub/Sub topic
2. Download credentials to `./credentials/gmail.json`
3. Set `GMAIL_CREDENTIALS_PATH` and `GMAIL_PUBSUB_TOPIC` in `.env`
4. Register webhook: `POST https://your-domain/webhooks/gmail`

### WhatsApp (Twilio)
1. Activate Twilio WhatsApp Sandbox
2. Set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER` in `.env`
3. Configure webhook: `POST https://your-domain/webhooks/whatsapp`
4. Status callback: `POST https://your-domain/webhooks/whatsapp/status`

### Web Form
No API keys required. Submits directly to `POST /support/submit`. Deploy the Next.js app from `web-form/` or use the built-in FastAPI endpoint.

---

## API Documentation

Interactive Swagger UI available at `http://localhost:8000/docs`.

| Method | Endpoint                       | Description                              |
|--------|--------------------------------|------------------------------------------|
| GET    | `/health`                      | System health check with component status|
| POST   | `/webhooks/gmail`              | Gmail Pub/Sub push notification handler  |
| POST   | `/webhooks/whatsapp`           | Twilio WhatsApp inbound message webhook  |
| POST   | `/webhooks/whatsapp/status`    | WhatsApp delivery status callback        |
| POST   | `/support/submit`              | Web form support ticket submission       |
| GET    | `/support/ticket/{ticket_id}`  | Look up ticket status by ID              |
| GET    | `/conversations/{id}`          | Get conversation history with messages   |
| GET    | `/customers/lookup`            | Find customer by email or phone          |
| GET    | `/metrics/channels`            | Per-channel performance metrics          |

---

## Agent Design

### 5 Tools

| Tool                    | Purpose                                               |
|-------------------------|-------------------------------------------------------|
| `search_knowledge_base` | Semantic search over product docs using pgvector       |
| `create_ticket`         | Create and categorize a support ticket in the CRM      |
| `get_customer_history`  | Retrieve past interactions across all channels         |
| `escalate_to_human`     | Route conversation to a human agent via Kafka           |
| `send_response`         | Format and deliver response on the original channel     |

### Required Workflow

Every interaction follows a strict 5-step sequence:
1. **Create Ticket** -- track the interaction before anything else
2. **Check History** -- review customer's cross-channel history
3. **Search Knowledge Base** -- find relevant documentation
4. **Formulate Response** -- craft channel-appropriate answer
5. **Send Response** -- deliver via email, WhatsApp, or web

### Guardrails

- Never discuss pricing (escalate to sales), process refunds (escalate to finance), or promise undocumented features
- Never share internal processes or system details
- Always create a ticket before responding

### Escalation Triggers

| Trigger                          | Severity | Action                    |
|----------------------------------|----------|---------------------------|
| Legal language detected          | P2       | Immediate human escalation|
| Profanity / aggressive sentiment | P2       | Immediate human escalation|
| 2+ failed knowledge base searches| P3       | Escalate with context     |
| Customer requests human agent    | P3       | Acknowledge and escalate  |
| Pricing/billing/refund requests  | P3       | Escalate to finance       |
| Security/data concerns           | P2       | Immediate human escalation|

---

## Environment Variables

| Variable                   | Default                  | Description                             |
|----------------------------|--------------------------|-----------------------------------------|
| `ENVIRONMENT`              | `development`            | Runtime environment                     |
| `LOG_LEVEL`                | `INFO`                   | Logging verbosity                       |
| `POSTGRES_HOST`            | `localhost`              | PostgreSQL host                         |
| `POSTGRES_PORT`            | `5432`                   | PostgreSQL port                         |
| `POSTGRES_DB`              | `fte_db`                 | Database name                           |
| `POSTGRES_USER`            | `fte_user`               | Database user                           |
| `POSTGRES_PASSWORD`        | `fte_password_dev`       | Database password                       |
| `OPENAI_API_KEY`           | _(empty = mock mode)_    | OpenAI API key for GPT-4o              |
| `KAFKA_BOOTSTRAP_SERVERS`  | `localhost:9092`         | Kafka broker address                    |
| `GMAIL_CREDENTIALS_PATH`   | _(empty = mock mode)_    | Path to Gmail service account JSON      |
| `GMAIL_PUBSUB_TOPIC`       | _(empty)_                | Google Pub/Sub topic for Gmail push     |
| `TWILIO_ACCOUNT_SID`       | _(empty = mock mode)_    | Twilio account SID                      |
| `TWILIO_AUTH_TOKEN`        | _(empty)_                | Twilio auth token                       |
| `TWILIO_WHATSAPP_NUMBER`   | _(empty)_                | Twilio WhatsApp sender number           |
| `API_HOST`                 | `0.0.0.0`               | API bind host                           |
| `API_PORT`                 | `8000`                   | API bind port                           |
| `API_BASE_URL`             | `http://localhost:8000`  | Public API base URL                     |

---

## Testing

```bash
# Unit and integration tests
pytest                                        # Run all tests
pytest --cov=src --cov-report=term-missing    # With coverage
pytest tests/test_agent.py -v                 # Specific file

# Load tests (Locust)
locust -f tests/load_test.py --host=http://localhost:8000
# Web UI at http://localhost:8089, or headless:
locust -f tests/load_test.py --host=http://localhost:8000 --headless -u 50 -r 10 -t 60s
```

---

## Kubernetes Deployment

Deploy to any Kubernetes cluster using the manifests in `k8s/`:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/deployment-api.yaml
kubectl apply -f k8s/deployment-worker.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml              # Horizontal Pod Autoscaler
```

---

## Mock Mode

The system runs fully without external API keys. Mock implementations activate automatically:

| Service | Mock Trigger                   | Behavior                                         |
|---------|--------------------------------|--------------------------------------------------|
| OpenAI  | `OPENAI_API_KEY` empty         | MockAgent uses keyword matching + knowledge base |
| Gmail   | `GMAIL_CREDENTIALS_PATH` empty | Simulated email processing                       |
| Twilio  | `TWILIO_ACCOUNT_SID` empty     | Simulated WhatsApp handling                      |
| Kafka   | Development environment        | InMemoryEventBus (asyncio queues)                |

The MockAgent follows the same 5-step workflow as the real agent and supports all escalation triggers.

---

## Performance Requirements

| Metric                        | Target   |
|-------------------------------|----------|
| API response time (p95)       | < 500ms  |
| Webhook acknowledgment        | < 200ms  |
| End-to-end message processing | < 30s    |
| Knowledge base search         | < 100ms  |
| Concurrent conversations      | 100+     |
| Uptime SLO                    | 99.5%    |
| Ticket creation               | < 50ms   |
| Escalation routing            | < 1s     |

---

## License

This project was built for CRM Digital FTE Factory -- Hackathon 5.
