# Customer Success Digital FTE - Specification

**Version:** 1.0
**Date:** 2026-02-23
**Status:** Approved
**Owner:** Hackathon Team 05
**Project:** CRM Digital FTE Factory

---

## 1. Purpose

Build a **24/7 AI Customer Success agent** (Digital Full-Time Employee) that autonomously handles customer support inquiries across three communication channels for TechCorp, a SaaS project management platform. The agent resolves common issues from a knowledge base, creates and tracks support tickets, identifies customers across channels, and escalates complex cases to human agents with full context.

**Success Criteria:**
- Resolve > 80% of common inquiries without human intervention
- Maintain consistent brand voice across all channels
- Reduce average response time from hours to seconds
- Provide seamless customer experience across channel switches

---

## 2. Supported Channels

| Channel | Technology | Endpoint | Response Format | Tone |
|---------|-----------|----------|-----------------|------|
| **Email** | Gmail API + Pub/Sub | `POST /webhooks/gmail` | Formal, 150-400 words, greeting + signature + ticket ref | Professional, empathetic |
| **WhatsApp** | Twilio WhatsApp API | `POST /webhooks/whatsapp` | Concise, < 300 chars/msg, max 3 messages per turn | Casual, helpful |
| **Web Form** | Next.js + FastAPI | `POST /support/submit` | Semi-formal, 100-300 words, includes help links | Structured, solution-oriented |

---

## 3. Scope

### 3.1 In-Scope

- **Multi-channel intake:** Receive and process customer messages from Gmail, WhatsApp, and web form submissions
- **Ticket management:** Automatic ticket creation, status tracking, lifecycle management in PostgreSQL CRM
- **Knowledge base search:** Semantic search (pgvector) over TechCorp product documentation with fallback to text search
- **Customer identity resolution:** Cross-channel identification via email and phone number; conversation continuity
- **Escalation engine:** Rule-based escalation with structured handoff to human agents via Kafka events
- **Channel-aware formatting:** Response tone, length, and structure adapted per channel rules
- **Sentiment analysis:** Detect customer mood from message text; trigger escalation on negative sentiment
- **Metrics and observability:** Per-channel response times, resolution rates, escalation rates, accuracy tracking
- **Event streaming:** Kafka-based decoupling of intake, processing, and delivery
- **Mock-first development:** All external services abstracted behind interfaces with mock implementations
- **Containerized deployment:** Docker for local development, Kubernetes for production
- **Web support form:** Standalone Next.js component with form validation, submission, and ticket status checking

### 3.2 Out-of-Scope

| Excluded Item | Rationale |
|--------------|-----------|
| Salesforce / HubSpot CRM integration | PostgreSQL serves as custom CRM; external CRM integration is a post-hackathon concern |
| Real-time chat widget | Web form is asynchronous by design; real-time chat adds significant complexity |
| Production WhatsApp Business account | Twilio Sandbox is sufficient for hackathon demonstration |
| Voice / phone channel | Not included in the three-channel specification |
| Image / media analysis | WhatsApp media attachments are acknowledged but not analyzed |
| Multi-language AI responses | English-only for initial release; localization is a follow-up |
| Customer self-service portal | Out of scope; only the support submission form is built |
| Payment processing | Agent never processes payments or refunds; always escalates to Finance |

---

## 4. Agent Tools

The AI agent has access to exactly 5 tools, each implemented as an OpenAI Agents SDK `@function_tool`:

| # | Tool Name | Description | Inputs | Outputs |
|---|-----------|-------------|--------|---------|
| 1 | `search_knowledge_base` | Semantic search over TechCorp product documentation using pgvector embeddings. Falls back to text search if semantic results score below 0.5. | `query: str`, `max_results: int` (default 3) | List of matching KB articles with title, content excerpt, and relevance score |
| 2 | `create_ticket` | Creates a support ticket in the PostgreSQL CRM with channel source, category, priority, and customer reference. | `subject: str`, `category: str`, `priority: str`, `channel: str`, `customer_id: str`, `message: str` | Ticket ID, creation timestamp, status |
| 3 | `get_customer_history` | Retrieves cross-channel conversation and ticket history for a customer. Used to provide context and detect repeat contacts. | `customer_id: str`, `limit: int` (default 10) | List of prior tickets and conversations with timestamps, channels, and resolution status |
| 4 | `escalate_to_human` | Hands off the conversation to a human agent with full context. Publishes escalation event to Kafka and updates ticket status. | `ticket_id: str`, `reason: str`, `severity: str`, `routing_team: str`, `conversation_summary: str` | Escalation confirmation with estimated response time |
| 5 | `send_response` | Delivers the formatted response through the appropriate channel handler (Gmail, Twilio, or web form email). | `conversation_id: str`, `channel: str`, `message: str`, `customer_id: str` | Delivery status and message ID |

### Tool Execution Order (Required Workflow)

```
1. create_ticket        -> Always first; ensures auditability
2. get_customer_history  -> Check for repeat contacts and context
3. search_knowledge_base -> Find relevant documentation
4. [Agent reasoning]     -> Formulate response or decide to escalate
5. send_response         -> Deliver channel-formatted response
   OR escalate_to_human  -> Hand off with full context
```

---

## 5. Performance Requirements

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| AI processing time | < 3 seconds | Time from message receipt to response generation |
| End-to-end delivery | < 30 seconds | Time from message receipt to customer receiving response |
| Resolution accuracy | > 85% | Percentage of first-response resolutions validated against test set |
| Escalation rate | < 20% | Percentage of tickets requiring human handoff |
| Cross-channel identification | > 95% | Correct customer matching when same person uses multiple channels |
| System uptime | > 99.9% | Monthly availability measured via health check endpoint |
| KB search latency | < 500 milliseconds | pgvector query execution time |
| Ticket creation latency | < 300 milliseconds | Database INSERT round-trip |
| Sentiment classification accuracy | > 80% | Correct polarity detection on labeled test set |
| Category classification accuracy | > 90% | Correct category assignment validated against sample tickets |

---

## 6. Guardrails (Hard Constraints)

The agent MUST adhere to these non-negotiable rules in every interaction:

### 6.1 Never Do

| Rule | Trigger | Required Action |
|------|---------|-----------------|
| **Never discuss pricing** | Customer asks about specific costs, discounts, or custom pricing | Provide general plan feature comparison; escalate to Sales for dollar amounts |
| **Never promise features** | Customer asks about unreleased or undocumented features | Acknowledge the request as feedback; never commit to timelines or features |
| **Never process refunds** | Customer requests a refund or billing adjustment | Acknowledge the request empathetically; escalate to Finance team |
| **Never make legal commitments** | Customer mentions legal terms, compliance, or contracts | Provide factual public info only; escalate to Support Lead |
| **Never disparage competitors** | Customer compares TechCorp to a competitor | Focus on TechCorp features and strengths; never criticize competitors |
| **Never share internal information** | Customer asks about internal processes, employee details, or system architecture | Redirect to public documentation and official channels |

### 6.2 Always Do

| Rule | Implementation |
|------|---------------|
| **Always create a ticket** | Ticket creation is the first step before any response; ensures auditability |
| **Always check sentiment** | Sentiment analysis runs on every inbound message; negative sentiment triggers escalation review |
| **Always check customer history** | Prior ticket and conversation history is loaded before generating a response |
| **Always format per channel** | Responses pass through channel-specific formatters before delivery |
| **Always include ticket reference** | Email and web form responses include ticket ID; WhatsApp only when asked |
| **Always use brand voice** | Responses adhere to the TechCorp Brand Voice Guide (friendly, professional, empathetic, solution-oriented) |

---

## 7. Escalation Triggers

| # | Trigger | Detection Method | Escalation Flag | Route To |
|---|---------|-----------------|-----------------|----------|
| 1 | **Legal language** | Keyword detection: "lawyer", "attorney", "lawsuit", "legal action", "breach of contract", "GDPR request", "subpoena" | `LEGAL_ESCALATION` | Support Lead (Priya Patel) |
| 2 | **Profanity / aggressive language** | Sentiment score < 0.3 OR explicit profanity detected | `SENTIMENT_ESCALATION` | Support Lead (Priya Patel) |
| 3 | **2+ failed KB searches** | Knowledge base returns confidence < 0.5 on two consecutive searches for the same query | `KB_MISS` | Support Team |
| 4 | **Customer requests human** | Keywords: "human", "real person", "representative", "agent", "talk to someone", "manager", "supervisor" | `HUMAN_REQUESTED` | Support Team (next available) |
| 5 | **WhatsApp escalation keywords** | WhatsApp-specific keywords: "human", "agent", "representative", "help me", "call me", "urgent", "emergency" | `WHATSAPP_ESCALATION` | Support Team |
| 6 | **Pricing questions** | Customer asks about specific costs, discounts, enterprise pricing | `SALES_INQUIRY` | Sales Team (Rachel Thompson) |
| 7 | **Refund requests** | Customer explicitly requests money back | `REFUND_REQUEST` | Finance Team (Lisa Wang) |
| 8 | **Repeat contact (3+)** | Same customer, same issue category, within 7 days, 3+ tickets | `REPEAT_CONTACT` | Support Lead (Priya Patel) |
| 9 | **Security concerns** | Keywords: "data breach", "unauthorized access", "vulnerability", "security" | `SECURITY_ESCALATION` | Security Team (Alex Rivera) |
| 10 | **P1 severity** | System-wide outage, data loss, complete platform inaccessibility | `P1_CRITICAL` | Engineering + Support Lead |

---

## 8. System Architecture

```
                    +------------------+
                    |   Gmail API      |
                    |   (Pub/Sub)      |
                    +--------+---------+
                             |
                    +--------+---------+
                    |  Twilio WhatsApp |
                    |   Webhook        |
                    +--------+---------+
                             |
                    +--------+---------+
                    |  Next.js Web     |
                    |  Support Form    |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   FastAPI        |
                    |   Webhook Router |
                    +--------+---------+
                             |
                    +--------v---------+
                    |   Apache Kafka   |
                    |   Event Bus      |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Message         |
                    |  Processor       |
                    |  (Agent Worker)  |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v--------+
     | PostgreSQL  |  | OpenAI      |  | Channel     |
     | CRM + KB   |  | Agents SDK  |  | Handlers    |
     | (pgvector)  |  | (GPT-4o)   |  | (Gmail,     |
     +-------------+  +-------------+  |  Twilio)    |
                                       +-------------+
```

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend API | FastAPI | 0.115.6 |
| AI Agent | OpenAI Agents SDK | 0.0.7 |
| Database | PostgreSQL + pgvector | 16 |
| Event Streaming | Apache Kafka (aiokafka) | 0.12.0 |
| Web Form | Next.js + React | 14 |
| Containerization | Docker + docker-compose | Latest |
| Orchestration | Kubernetes | 1.28+ |
| Email Channel | Gmail API + Pub/Sub | v1 |
| WhatsApp Channel | Twilio WhatsApp API | Latest |

---

## 9. Data Model (Core Tables)

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `customers` | Unified customer records | id, name, email, company, plan_tier, created_at |
| `customer_identifiers` | Cross-channel identity mapping | id, customer_id, identifier_type, identifier_value |
| `conversations` | Conversation threads | id, customer_id, channel, status, started_at |
| `messages` | All messages with metadata | id, conversation_id, direction, content, channel, delivery_status |
| `tickets` | Support tickets with lifecycle | id, customer_id, conversation_id, subject, category, priority, status |
| `knowledge_base` | Product docs with embeddings | id, title, content, category, embedding (vector), updated_at |
| `channel_configs` | Per-channel settings | id, channel_name, response_template, max_length, tone |
| `agent_metrics` | Performance tracking | id, channel, response_time_ms, resolved, escalated, timestamp |

---

## 10. Kafka Event Topics

| Topic | Publisher | Consumer | Payload |
|-------|----------|----------|---------|
| `fte.tickets.incoming` | Webhook handlers | Message Processor | Unified ticket event with channel metadata |
| `fte.channels.email.inbound` | Gmail handler | Message Processor | Email-specific event (thread ID, headers) |
| `fte.channels.whatsapp.inbound` | WhatsApp handler | Message Processor | WhatsApp event (phone, message SID) |
| `fte.channels.webform.inbound` | Web form handler | Message Processor | Form submission (all fields) |
| `fte.escalations` | Message Processor | Escalation handler | Escalation handoff with full context |
| `fte.metrics` | Message Processor | Metrics collector | Performance data point |
| `fte.dlq` | Any producer | DLQ handler | Failed events for manual review |

---

## 11. API Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| `GET` | `/health` | Health check with component status | None |
| `POST` | `/webhooks/gmail` | Gmail Pub/Sub push notifications | Google verification |
| `POST` | `/webhooks/whatsapp` | Twilio WhatsApp incoming messages | Twilio signature |
| `POST` | `/webhooks/whatsapp/status` | WhatsApp delivery status callbacks | Twilio signature |
| `POST` | `/support/submit` | Web form submission | None (public) |
| `GET` | `/support/ticket/{id}` | Ticket status lookup | None (public) |
| `GET` | `/conversations/{id}` | Conversation history | Internal |
| `GET` | `/customers/lookup` | Customer search by email/phone | Internal |
| `GET` | `/metrics/channels` | Per-channel performance metrics | Internal |

---

## 12. Deployment Configuration

### Local Development
- `docker-compose.yml` with PostgreSQL, Kafka, Zookeeper, FastAPI, Worker services
- Mock mode enabled by default (no API keys required)
- Web form runs separately via `npm run dev` in `web-form/` directory

### Production (Kubernetes)
- Namespace: `customer-success-fte`
- API Deployment: 3 replicas, HPA scaling to 20
- Worker Deployment: 3 replicas, HPA scaling to 30
- PostgreSQL: StatefulSet with persistent volume
- Ingress with TLS termination
- ConfigMap for non-sensitive config; Secrets for API keys

---

## 13. Acceptance Criteria

- [ ] Agent processes sample tickets from all 3 channels with > 85% accuracy
- [ ] Channel-specific formatting produces correct tone and length per channel
- [ ] Escalation triggers fire correctly for all 10 trigger categories
- [ ] Cross-channel customer identification resolves > 95% of test cases
- [ ] Ticket lifecycle (create, update, resolve, escalate) works end-to-end
- [ ] KB semantic search returns relevant results for documented topics
- [ ] Metrics endpoint reports per-channel response times and resolution rates
- [ ] Docker Compose brings up full stack with `docker-compose up`
- [ ] Kubernetes manifests deploy successfully with health checks passing
- [ ] Web form validates input, submits to API, and displays ticket ID
