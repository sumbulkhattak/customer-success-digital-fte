# Transition Checklist: Stage 1 (Incubation) to Stage 2 (Production)

**Date:** 2026-02-23
**Purpose:** Track readiness for transitioning from Claude-assisted design and prototyping (Stage 1) to production deployment with OpenAI Agents SDK (Stage 2)
**Project:** Customer Success Digital FTE

---

## Overview

Stage 1 (Incubation with Claude) focuses on discovering requirements, designing the system, generating code artifacts, and validating patterns against sample data. Stage 2 (Production with OpenAI Agents SDK) takes the validated designs and deploys them as a production-grade service.

This checklist ensures nothing is missed during the handoff.

---

## Phase 1: Discovery and Requirements

### 1.1 Sample Data Analysis

- [x] Collected 50+ sample tickets across all 3 channels (email, WhatsApp, web form)
- [x] Analyzed channel-specific communication patterns (tone, length, structure)
- [x] Identified category distribution (password reset, billing, bugs, features, integrations, API, feedback)
- [x] Documented common resolution patterns per category
- [x] Cataloged edge cases from real ticket scenarios
- [x] Mapped customer identity signals per channel (email, phone, name, company)

### 1.2 Requirement Crystallization

- [x] Defined in-scope and out-of-scope boundaries
- [x] Documented 5 agent tools with inputs, outputs, and success criteria
- [x] Established performance targets (< 3s processing, > 85% accuracy, < 20% escalation)
- [x] Defined guardrails (never discuss pricing, never promise features, never process refunds)
- [x] Documented 10 escalation trigger categories with detection methods and routing
- [x] Specified channel-aware response formatting rules

---

## Phase 2: System Prompt and Agent Design

### 2.1 System Prompt

- [x] Working system prompt with TechCorp context (company, product, plans)
- [x] Channel awareness instructions embedded in prompt
- [x] Required workflow defined (ticket -> history -> KB search -> respond or escalate)
- [x] Hard constraints expressed as explicit rules (never/always)
- [x] Brand voice guidelines integrated (friendly, professional, empathetic, solution-oriented)
- [x] Error handling instructions for unknown questions and failed searches

### 2.2 Channel-Aware Formatting

- [x] Email formatter: greeting, acknowledgment, numbered steps, signature block, ticket ref
- [x] WhatsApp formatter: concise messages, < 300 chars, message splitting logic, minimal emojis
- [x] Web form formatter: semi-formal, includes help links and alternative contact methods
- [x] Response length enforcement per channel (email 150-400 words, WhatsApp < 300 chars, web 100-300 words)

### 2.3 Edge Cases Identified

- [x] Empty message handling (prompt for clarification)
- [x] Non-English message handling (respond in same language if supported)
- [x] Duplicate submission detection (deduplicate by customer + subject within time window)
- [x] Pricing disguised as feature question (detect pricing intent, escalate)
- [x] Multi-trigger scenarios (legal + refund = multi-team routing)
- [x] After-hours P1 handling (on-call engineer notification)
- [x] Media attachments on WhatsApp (acknowledge but do not analyze)
- [x] Repeat contact detection (3+ contacts for same issue within 7 days)

---

## Phase 3: Response Patterns and Validation

### 3.1 Response Patterns Validated

- [x] Password reset resolution (spam folder, whitelist, incognito, manual reset)
- [x] Feature question handling (plan-specific guidance with KB article links)
- [x] Bug report triage (troubleshooting steps, severity classification, escalation if P1/P2)
- [x] Billing inquiry response (general plan info, escalate for specific pricing)
- [x] Integration troubleshooting (reconnection steps, OAuth token refresh)
- [x] API help responses (documentation references, code examples, rate limit guidance)
- [x] Feedback acknowledgment (log as ticket, thank customer, no commitment)
- [x] Escalation responses (empathy first, explain handoff, provide ticket ID, set expectations)

### 3.2 Escalation Rules Documented and Tested

- [x] Legal language detection keywords defined and tested against sample tickets
- [x] Profanity/sentiment threshold (< 0.3) tested against aggressive ticket samples
- [x] KB miss detection (2+ failed searches, confidence < 0.5) logic defined
- [x] Human request keyword list defined and tested across channels
- [x] WhatsApp-specific escalation keywords documented
- [x] Pricing escalation routing to Sales team verified
- [x] Refund escalation routing to Finance team verified
- [x] Security concern escalation routing to Security team verified
- [x] P1 severity escalation with on-call notification defined
- [x] Repeat contact detection logic (3+ tickets, same category, 7-day window) defined
- [x] Escalation handoff template with all required fields documented
- [x] Multi-team routing scenarios (legal + billing, security + engineering) defined

---

## Phase 4: Performance and Knowledge Base

### 4.1 Performance Baseline Established

- [x] Response time targets defined: < 3s processing, < 30s end-to-end delivery
- [x] KB search latency target: < 500ms with pgvector
- [x] Customer ID resolution target: < 200ms with indexed lookup
- [x] Ticket creation target: < 300ms
- [x] Accuracy target: > 85% resolution on first response
- [x] Escalation rate target: < 20% of total tickets
- [x] Cross-channel ID accuracy target: > 95%

### 4.2 Knowledge Base Populated and Searchable

- [x] Product documentation loaded into `knowledge_base` table
- [x] Documentation split into searchable sections (getting started, account management, features, integrations, troubleshooting, error codes, FAQ)
- [x] pgvector extension enabled for semantic search
- [x] Mock embedding generation for development (random vectors)
- [x] Text-based fallback search implemented for when semantic search scores low
- [x] Relevance scoring threshold defined (0.5 minimum for confident responses)

### 4.3 Cross-Channel Identity Resolution Working

- [x] `customer_identifiers` table with type-based lookup (email, phone, whatsapp)
- [x] Email-based identification from Gmail and web form channels
- [x] Phone-based identification from WhatsApp channel
- [x] Cross-linking logic (WhatsApp user provides email -> merge identifiers)
- [x] Conversation continuity across channel switches
- [x] Customer history aggregation across all channels

---

## Phase 5: Implementation and Testing

### 5.1 Mock Implementations Tested

- [x] MockAgent: keyword-based response generation without OpenAI API
- [x] MockGmailHandler: logs email operations to database
- [x] MockWhatsAppHandler: logs WhatsApp operations to database
- [x] InMemoryEventBus: Kafka fallback for local development without Kafka
- [x] Mock embedding generation for knowledge base seeding
- [x] Factory functions (`get_agent()`, `get_gmail_handler()`, `get_whatsapp_handler()`) switch between real and mock based on config

### 5.2 Production Configuration Ready

- [ ] Kubernetes namespace `customer-success-fte` manifests created
- [ ] API Deployment (3 replicas) with health checks and resource limits
- [ ] Worker Deployment (3 replicas) with Kafka consumer configuration
- [ ] PostgreSQL StatefulSet with persistent volume claims
- [ ] HPA configured (API: 3-20 replicas, Worker: 3-30 replicas, 70% CPU target)
- [ ] Ingress with TLS termination configured
- [ ] ConfigMap with all non-sensitive environment variables
- [ ] Secrets manifest with placeholder API keys
- [ ] Docker multi-stage build optimized for production image size

### 5.3 API Endpoints Documented and Tested

- [ ] `GET /health` returns component status (db, kafka, channels)
- [ ] `POST /webhooks/gmail` processes Gmail Pub/Sub notifications
- [ ] `POST /webhooks/whatsapp` validates Twilio signature and processes messages
- [ ] `POST /webhooks/whatsapp/status` handles delivery status callbacks
- [ ] `POST /support/submit` validates form input and creates ticket
- [ ] `GET /support/ticket/{id}` returns ticket status and conversation
- [ ] `GET /conversations/{id}` returns full conversation history
- [ ] `GET /customers/lookup` resolves customer by email or phone
- [ ] `GET /metrics/channels` returns per-channel performance data

---

## Phase 6: Observability and Error Handling

### 6.1 Metrics Collection Active

- [ ] `agent_metrics` table records per-interaction performance data
- [ ] Kafka `fte.metrics` topic publishes real-time metric events
- [ ] Per-channel metrics: response time, resolution rate, escalation rate
- [ ] Per-category metrics: volume, resolution time, escalation frequency
- [ ] Sentiment distribution tracking across channels
- [ ] `/metrics/channels` endpoint aggregates and returns metrics

### 6.2 Error Handling and DLQ Configured

- [ ] Kafka dead-letter queue (`fte.dlq`) captures failed message processing
- [ ] DLQ events include original message, error details, retry count
- [ ] Maximum 3 retries with exponential backoff before DLQ
- [ ] Channel handler failures produce graceful apology responses
- [ ] Database connection failures trigger circuit breaker pattern
- [ ] Structured logging (structlog) with correlation IDs per request
- [ ] Health check endpoint reports degraded status when components fail

---

## Phase 7: Final Validation

### 7.1 End-to-End Flow Verification

- [ ] Email: Gmail webhook -> Kafka -> Agent -> Gmail reply (full round-trip)
- [ ] WhatsApp: Twilio webhook -> Kafka -> Agent -> Twilio reply (full round-trip)
- [ ] Web form: Next.js submit -> API -> Kafka -> Agent -> email reply (full round-trip)
- [ ] Escalation: trigger detected -> escalation event published -> ticket updated
- [ ] Cross-channel: customer contacts via WhatsApp, then email -> unified history

### 7.2 Test Coverage

- [ ] Unit tests: agent tools, formatters, channel handlers
- [ ] Integration tests: database operations, Kafka produce/consume
- [ ] E2E tests: full flow from webhook to response delivery
- [ ] Load tests: Locust with 50+ concurrent users
- [ ] Sample ticket accuracy test: run all 50+ sample tickets through agent

### 7.3 Documentation Complete

- [ ] README with architecture overview and quick start guide
- [ ] API endpoint documentation with request/response examples
- [ ] Channel setup guides (Gmail API, Twilio, Next.js form)
- [ ] Environment variables reference
- [ ] Deployment guide (Docker Compose + Kubernetes)
- [ ] Spec documents (discovery log, spec, transition checklist, skills manifest)

---

## Transition Sign-Off

| Checkpoint | Owner | Status | Date |
|-----------|-------|--------|------|
| Discovery complete | Design team | Done | 2026-02-23 |
| Spec approved | Product owner | Done | 2026-02-23 |
| System prompt validated | Agent team | Done | 2026-02-23 |
| Code artifacts generated | Engineering | Done | 2026-02-23 |
| Mock tests passing | QA | Pending | - |
| Production config ready | DevOps | Pending | - |
| E2E validation passed | QA | Pending | - |
| Documentation complete | Technical writer | Pending | - |

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| OpenAI API latency exceeds 3s target | Response time SLA breach | Medium | Implement timeout with fallback to mock agent for degraded responses |
| Kafka consumer lag under load | Message processing delays | Medium | HPA scales workers to 30; tune consumer batch sizes |
| pgvector search quality with mock embeddings | Low resolution accuracy in dev | High | Use real OpenAI embeddings in staging; mock is for flow testing only |
| WhatsApp Twilio sandbox rate limits | Message delivery failures in demo | Low | Queue outbound messages; respect Twilio rate limits |
| Cross-channel ID false positive | Wrong customer matched to conversation | Low | Require exact match on email/phone; secondary verification for ambiguous matches |
