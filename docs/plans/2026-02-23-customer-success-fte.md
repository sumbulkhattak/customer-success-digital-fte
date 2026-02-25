# Customer Success Digital FTE - Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-grade 24/7 AI Customer Success agent that handles support across Gmail, WhatsApp, and Web Form channels with PostgreSQL CRM, Kafka streaming, and Kubernetes deployment.

**Architecture:** Multi-channel intake (Gmail API, Twilio WhatsApp, Web Form) -> FastAPI webhooks -> Kafka event streaming -> OpenAI Agents SDK worker -> PostgreSQL CRM state -> Channel-specific response delivery. Mock-first approach for all external APIs.

**Tech Stack:** Python 3.11+, FastAPI, OpenAI Agents SDK, PostgreSQL 16 + pgvector, Apache Kafka (aiokafka), Next.js 14 + React, Docker, Kubernetes

---

## Task 1: Project Foundation - .gitignore, requirements.txt, .env.example, config

**Files:**
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `src/config.py`

**Step 1: Create .gitignore**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
dist/
build/

# Environment
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# Node
node_modules/
.next/
out/

# OS
.DS_Store
Thumbs.db

# Docker
docker-compose.override.yml

# Postgres data
pgdata/

# Logs
*.log
logs/
```

**Step 2: Create requirements.txt**

```text
# Core
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic[email]==2.10.4
python-dotenv==1.0.1
httpx==0.28.1

# OpenAI Agents SDK
openai-agents==0.0.7
openai==1.59.5

# Database
asyncpg==0.30.0
pgvector==0.3.6
alembic==1.14.0
sqlalchemy==2.0.36

# Kafka
aiokafka==0.12.0

# Channel integrations
google-api-python-client==2.157.0
google-auth-oauthlib==1.2.1
google-cloud-pubsub==2.27.1
twilio==9.4.0

# MCP Server
mcp==1.2.0

# Utilities
python-multipart==0.0.20
structlog==24.4.0
tenacity==9.0.0
textblob==0.18.0

# Testing
pytest==8.3.4
pytest-asyncio==0.25.0
pytest-cov==6.0.0
httpx==0.28.1
locust==2.32.4
```

**Step 3: Create .env.example**

```env
# Environment
ENVIRONMENT=development
LOG_LEVEL=INFO

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=fte_db
POSTGRES_USER=fte_user
POSTGRES_PASSWORD=fte_password_dev

# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Gmail
GMAIL_CREDENTIALS_PATH=./credentials/gmail.json
GMAIL_PUBSUB_TOPIC=projects/your-project/topics/gmail-push

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# API
API_HOST=0.0.0.0
API_PORT=8000
API_BASE_URL=http://localhost:8000
```

**Step 4: Create src/config.py**

```python
"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # PostgreSQL
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "fte_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "fte_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "fte_password_dev")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    # Gmail
    GMAIL_CREDENTIALS_PATH: str = os.getenv("GMAIL_CREDENTIALS_PATH", "")
    GMAIL_PUBSUB_TOPIC: str = os.getenv("GMAIL_PUBSUB_TOPIC", "")

    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Feature flags (for mock mode)
    USE_MOCK_OPENAI: bool = not os.getenv("OPENAI_API_KEY", "")
    USE_MOCK_GMAIL: bool = not os.getenv("GMAIL_CREDENTIALS_PATH", "")
    USE_MOCK_TWILIO: bool = not os.getenv("TWILIO_ACCOUNT_SID", "")


settings = Settings()
```

**Step 5: Create empty __init__.py files**

Create: `src/__init__.py`, `src/agent/__init__.py`, `src/channels/__init__.py`, `src/workers/__init__.py`, `src/api/__init__.py`, `src/database/__init__.py`, `tests/__init__.py`

**Step 6: Commit**

```bash
git add .gitignore requirements.txt .env.example src/ tests/__init__.py
git commit -m "feat: project foundation - config, dependencies, .gitignore"
```

---

## Task 2: Context Dossier - Company Profile, Product Docs, Sample Tickets

**Files:**
- Create: `context/company-profile.md`
- Create: `context/product-docs.md`
- Create: `context/sample-tickets.json`
- Create: `context/escalation-rules.md`
- Create: `context/brand-voice.md`

**Step 1: Create context/company-profile.md**

TechCorp SaaS company profile including: company name, product (TechCorp Platform - a project management SaaS), target market (SMBs), pricing tiers (Starter $29/mo, Professional $79/mo, Enterprise custom), team size, support hours promise, SLA.

**Step 2: Create context/product-docs.md**

Product documentation covering: Getting Started guide, Account Management (password reset, profile updates, billing), Features (projects, tasks, team collaboration, reporting, API), Integrations (Slack, GitHub, Jira), Troubleshooting (common errors, connectivity issues). This becomes the knowledge base.

**Step 3: Create context/sample-tickets.json**

50+ sample tickets across all 3 channels with varied categories:
- 20 email tickets (longer, formal)
- 15 WhatsApp tickets (short, casual)
- 15 web form tickets (medium length)
- Categories: password reset, feature questions, bug reports, billing, feedback, integrations, API help
- Include escalation scenarios: pricing questions, angry customers, legal mentions

**Step 4: Create context/escalation-rules.md**

Escalation rules document defining triggers, severity levels, routing.

**Step 5: Create context/brand-voice.md**

Brand voice guide: friendly but professional, empathetic, solution-oriented, channel-appropriate tone guidelines.

**Step 6: Commit**

```bash
git add context/
git commit -m "feat: context dossier - company profile, docs, sample tickets"
```

---

## Task 3: PostgreSQL Database Schema

**Files:**
- Create: `src/database/schema.sql`
- Create: `src/database/seed.py`
- Create: `src/database/connection.py`
- Create: `src/database/queries.py`

**Step 1: Create src/database/schema.sql**

Complete schema with all tables: `customers`, `customer_identifiers`, `conversations`, `messages`, `tickets`, `knowledge_base` (with pgvector), `channel_configs`, `agent_metrics`. Include all indexes. Use `gen_random_uuid()` for PKs, `TIMESTAMP WITH TIME ZONE` for dates, `JSONB` for metadata.

**Step 2: Create src/database/connection.py**

asyncpg connection pool manager with `get_db_pool()`, `init_db()` (runs schema.sql), and `close_db()`.

**Step 3: Create src/database/queries.py**

Async query functions: `create_customer()`, `find_customer_by_email()`, `find_customer_by_phone()`, `create_conversation()`, `get_active_conversation()`, `create_message()`, `create_ticket()`, `update_ticket_status()`, `get_ticket_by_id()`, `search_knowledge_base()`, `get_customer_history()`, `record_metric()`, `get_channel_metrics()`.

**Step 4: Create src/database/seed.py**

Seed script that: loads product-docs.md, splits into sections, generates embeddings (mock: random vectors), inserts into knowledge_base table. Also seeds channel_configs for email/whatsapp/web_form.

**Step 5: Commit**

```bash
git add src/database/
git commit -m "feat: PostgreSQL CRM schema, connection pool, query functions"
```

---

## Task 4: Kafka Event Streaming Client

**Files:**
- Create: `src/kafka_client.py`

**Step 1: Create src/kafka_client.py**

Kafka producer/consumer with topic definitions. Include `FTEKafkaProducer` (with `start()`, `stop()`, `publish()`), `FTEKafkaConsumer` (with `start()`, `stop()`, `consume()`). Define all topics in `TOPICS` dict. Add `InMemoryEventBus` as fallback when Kafka is unavailable (for local dev without Kafka).

**Step 2: Commit**

```bash
git add src/kafka_client.py
git commit -m "feat: Kafka client with in-memory fallback"
```

---

## Task 5: Agent Prompts and Formatters

**Files:**
- Create: `src/agent/prompts.py`
- Create: `src/agent/formatters.py`

**Step 1: Create src/agent/prompts.py**

`CUSTOMER_SUCCESS_SYSTEM_PROMPT` - Full system prompt with: purpose, channel awareness rules, required workflow (create ticket -> check history -> search KB -> send response), hard constraints (never discuss pricing, never promise features), escalation triggers, response quality standards, context variables.

**Step 2: Create src/agent/formatters.py**

`format_for_channel(response, channel)` - Email: formal with greeting/signature/ticket ref. WhatsApp: concise with emoji footer. Web: semi-formal with help link.

`format_search_results(results)` - Format knowledge base results with titles and relevance scores.

`format_customer_history(history)` - Format cross-channel history for agent context.

**Step 3: Commit**

```bash
git add src/agent/prompts.py src/agent/formatters.py
git commit -m "feat: agent prompts and channel-aware formatters"
```

---

## Task 6: Agent Tools (@function_tool definitions)

**Files:**
- Create: `src/agent/tools.py`

**Step 1: Create src/agent/tools.py**

5 tools with Pydantic input models and proper error handling:

1. `search_knowledge_base(KnowledgeSearchInput)` - Semantic search via pgvector
2. `create_ticket(TicketInput)` - Create ticket with channel tracking
3. `get_customer_history(customer_id: str)` - Cross-channel history
4. `escalate_to_human(EscalationInput)` - Escalate with reason, publish Kafka event
5. `send_response(ResponseInput)` - Send via appropriate channel handler

Each tool: Pydantic BaseModel for input, try/except with graceful fallback messages, structured logging, database operations via queries.py.

**Step 2: Commit**

```bash
git add src/agent/tools.py
git commit -m "feat: agent tools with Pydantic validation and error handling"
```

---

## Task 7: Customer Success Agent (OpenAI Agents SDK)

**Files:**
- Create: `src/agent/customer_success_agent.py`

**Step 1: Create src/agent/customer_success_agent.py**

Agent definition using OpenAI Agents SDK `Agent()` class with: name, model (gpt-4o), instructions (from prompts.py), tools list. Include `MockAgent` class that handles queries via keyword matching against knowledge base for development without OpenAI API key. Factory function `get_agent()` that returns real or mock based on config.

**Step 2: Commit**

```bash
git add src/agent/customer_success_agent.py
git commit -m "feat: customer success agent with mock fallback"
```

---

## Task 8: Channel Handlers - Gmail

**Files:**
- Create: `src/channels/gmail_handler.py`

**Step 1: Create src/channels/gmail_handler.py**

`GmailHandler` class with: `setup_push_notifications()`, `process_notification()`, `get_message()`, `send_reply()`, `_extract_body()`, `_extract_email()`. Plus `MockGmailHandler` that logs to database instead of calling Gmail API. Factory function `get_gmail_handler()`.

**Step 2: Commit**

```bash
git add src/channels/gmail_handler.py
git commit -m "feat: Gmail handler with mock implementation"
```

---

## Task 9: Channel Handlers - WhatsApp (Twilio)

**Files:**
- Create: `src/channels/whatsapp_handler.py`

**Step 1: Create src/channels/whatsapp_handler.py**

`WhatsAppHandler` class with: `validate_webhook()`, `process_webhook()`, `send_message()`, `format_response()` (split long messages). Plus `MockWhatsAppHandler`. Factory function `get_whatsapp_handler()`.

**Step 2: Commit**

```bash
git add src/channels/whatsapp_handler.py
git commit -m "feat: WhatsApp/Twilio handler with mock implementation"
```

---

## Task 10: Channel Handlers - Web Form

**Files:**
- Create: `src/channels/web_form_handler.py`

**Step 1: Create src/channels/web_form_handler.py**

FastAPI `APIRouter` with prefix `/support`. Pydantic models: `SupportFormSubmission` (with validators for name, email, subject, category, message), `SupportFormResponse`. Endpoints: `POST /support/submit`, `GET /support/ticket/{ticket_id}`. Publishes to Kafka on submission.

**Step 2: Commit**

```bash
git add src/channels/web_form_handler.py
git commit -m "feat: web form handler with validation and ticket tracking"
```

---

## Task 11: Unified Message Processor (Kafka Worker)

**Files:**
- Create: `src/workers/message_processor.py`

**Step 1: Create src/workers/message_processor.py**

`UnifiedMessageProcessor` class that: consumes from `fte.tickets.incoming`, resolves customer identity across channels, gets/creates conversation, stores inbound message, loads history, runs agent, stores outbound message, publishes metrics. Includes `resolve_customer()` for cross-channel ID, `get_or_create_conversation()`, `handle_error()` with apology responses.

**Step 2: Commit**

```bash
git add src/workers/message_processor.py
git commit -m "feat: unified message processor with cross-channel support"
```

---

## Task 12: FastAPI Application

**Files:**
- Create: `src/api/main.py`

**Step 1: Create src/api/main.py**

FastAPI app with: CORS middleware, web_form_router included, startup/shutdown events (init DB pool, Kafka producer), health check endpoint, Gmail webhook `POST /webhooks/gmail`, WhatsApp webhook `POST /webhooks/whatsapp`, WhatsApp status `POST /webhooks/whatsapp/status`, conversation history `GET /conversations/{id}`, customer lookup `GET /customers/lookup`, channel metrics `GET /metrics/channels`.

**Step 2: Commit**

```bash
git add src/api/main.py
git commit -m "feat: FastAPI service with all channel endpoints"
```

---

## Task 13: MCP Server

**Files:**
- Create: `src/mcp_server.py`

**Step 1: Create src/mcp_server.py**

MCP server exposing 5+ tools: `search_knowledge_base`, `create_ticket`, `get_customer_history`, `escalate_to_human`, `send_response`. Uses the same underlying functions as the agent tools.

**Step 2: Commit**

```bash
git add src/mcp_server.py
git commit -m "feat: MCP server with customer success tools"
```

---

## Task 14: Docker and docker-compose

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

**Step 1: Create Dockerfile**

Multi-stage Python 3.11 Dockerfile. Install requirements, copy src/, expose 8000, CMD uvicorn.

**Step 2: Create docker-compose.yml**

Services: `postgres` (16 + pgvector), `kafka` + `zookeeper`, `api` (FastAPI), `worker` (message_processor). Volumes for postgres data. Environment from .env file.

**Step 3: Commit**

```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: Docker and docker-compose for local development"
```

---

## Task 15: Next.js Web Support Form

**Files:**
- Create: `web-form/package.json`
- Create: `web-form/next.config.js`
- Create: `web-form/tailwind.config.js`
- Create: `web-form/postcss.config.js`
- Create: `web-form/src/app/layout.tsx`
- Create: `web-form/src/app/page.tsx`
- Create: `web-form/src/app/globals.css`
- Create: `web-form/src/components/SupportForm.tsx`
- Create: `web-form/src/components/TicketStatus.tsx`

**Step 1: Initialize Next.js project**

package.json with next, react, react-dom, tailwindcss, typescript dependencies.

**Step 2: Create SupportForm.tsx**

Full React component with: form fields (name, email, subject, category dropdown, priority dropdown, message textarea), client-side validation, submit handler with fetch to API, loading state, success state with ticket ID, error display, character counter. Styled with Tailwind CSS.

**Step 3: Create TicketStatus.tsx**

Component that polls `/support/ticket/{id}` and displays ticket status, conversation history.

**Step 4: Create page.tsx**

Main page rendering SupportForm with configurable API endpoint.

**Step 5: Commit**

```bash
git add web-form/
git commit -m "feat: Next.js web support form with validation and status tracking"
```

---

## Task 16: Kubernetes Manifests

**Files:**
- Create: `k8s/namespace.yaml`
- Create: `k8s/configmap.yaml`
- Create: `k8s/secrets.yaml`
- Create: `k8s/deployment-api.yaml`
- Create: `k8s/deployment-worker.yaml`
- Create: `k8s/service.yaml`
- Create: `k8s/ingress.yaml`
- Create: `k8s/hpa.yaml`
- Create: `k8s/postgres.yaml`

**Step 1: Create all K8s manifests**

Namespace `customer-success-fte`, ConfigMap with env vars, Secrets for API keys, API Deployment (3 replicas), Worker Deployment (3 replicas), Service, Ingress with TLS, HPA (autoscale to 20/30), PostgreSQL StatefulSet.

**Step 2: Commit**

```bash
git add k8s/
git commit -m "feat: Kubernetes deployment manifests with HPA"
```

---

## Task 17: Specs and Discovery Documents

**Files:**
- Create: `specs/discovery-log.md`
- Create: `specs/customer-success-fte-spec.md`
- Create: `specs/transition-checklist.md`
- Create: `specs/agent-skills-manifest.md`

**Step 1: Create discovery-log.md**

Document patterns discovered from sample tickets: channel-specific patterns, common categories, escalation triggers, response style preferences.

**Step 2: Create customer-success-fte-spec.md**

Crystallized spec per hackathon template: purpose, supported channels table, in-scope/out-of-scope, tools table, performance requirements, guardrails.

**Step 3: Create transition-checklist.md**

Checklist mapping incubation -> production: discovered requirements, working prompts, edge cases, response patterns, escalation rules, performance baseline.

**Step 4: Create agent-skills-manifest.md**

5 skills: Knowledge Retrieval, Sentiment Analysis, Escalation Decision, Channel Adaptation, Customer Identification.

**Step 5: Commit**

```bash
git add specs/
git commit -m "feat: hackathon specs - discovery log, spec, transition checklist, skills"
```

---

## Task 18: Test Suites

**Files:**
- Create: `tests/test_agent.py`
- Create: `tests/test_channels.py`
- Create: `tests/test_e2e.py`
- Create: `tests/test_database.py`
- Create: `tests/load_test.py`
- Create: `pytest.ini`

**Step 1: Create pytest.ini**

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

**Step 2: Create test_agent.py**

Tests: empty message handling, pricing escalation, angry customer escalation, channel response length (email vs WhatsApp), tool execution order.

**Step 3: Create test_channels.py**

Tests: web form submission validation, Gmail webhook processing, WhatsApp webhook processing, cross-channel customer identification.

**Step 4: Create test_e2e.py**

Tests: full flow web form -> ticket -> agent response, ticket status retrieval, channel metrics endpoint, customer lookup.

**Step 5: Create test_database.py**

Tests: customer CRUD, conversation creation, message storage, knowledge base search.

**Step 6: Create load_test.py**

Locust load test: WebFormUser (weight 3), HealthCheckUser (weight 1).

**Step 7: Commit**

```bash
git add tests/ pytest.ini
git commit -m "feat: test suites - agent, channels, e2e, database, load"
```

---

## Task 19: Documentation

**Files:**
- Create: `README.md`

**Step 1: Create README.md**

Project overview, architecture diagram (ASCII), quick start guide (docker-compose up), API documentation, channel setup guides (Gmail, Twilio), deployment guide, environment variables reference.

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: README with setup guide and API documentation"
```

---

## Execution Order Summary

| # | Task | Priority | Dependencies |
|---|------|----------|-------------|
| 1 | Project Foundation | Critical | None |
| 2 | Context Dossier | Critical | None |
| 3 | Database Schema | Critical | Task 1 |
| 4 | Kafka Client | Critical | Task 1 |
| 5 | Agent Prompts/Formatters | Critical | Task 2 |
| 6 | Agent Tools | Critical | Tasks 3, 5 |
| 7 | Customer Success Agent | Critical | Tasks 5, 6 |
| 8 | Gmail Handler | High | Task 1 |
| 9 | WhatsApp Handler | High | Task 1 |
| 10 | Web Form Handler | Critical | Tasks 3, 4 |
| 11 | Message Processor | Critical | Tasks 4, 6, 7, 8, 9 |
| 12 | FastAPI Application | Critical | Tasks 8, 9, 10 |
| 13 | MCP Server | High | Task 6 |
| 14 | Docker/Compose | Critical | Tasks 3, 12 |
| 15 | Web Support Form (Next.js) | Critical | Task 10 |
| 16 | Kubernetes Manifests | High | Task 14 |
| 17 | Specs/Discovery Docs | High | Tasks 2, 7 |
| 18 | Test Suites | High | Tasks 7, 12 |
| 19 | Documentation | Medium | All |
