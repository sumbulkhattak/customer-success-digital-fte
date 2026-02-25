---
id: 3
title: Kafka Event Streaming Client
stage: general
date: 2026-02-23
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: user
command: create kafka_client.py
labels: ["kafka", "event-bus", "streaming", "async"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/kafka_client.py
tests:
  - none
---

## Prompt

You are implementing Task 4 of a Customer Success Digital FTE project.

**Working directory:** C:\Users\LAPTOP WORLD\Desktop\Hackathon-05

**Existing:** `src/config.py` has `settings.KAFKA_BOOTSTRAP_SERVERS`

Create this file:

## src/kafka_client.py

A Kafka client module with:

1. **TOPICS dict** - All topic definitions:
   - `fte.tickets.incoming` - Unified intake from all channels
   - `fte.channels.email.inbound` - Email events
   - `fte.channels.whatsapp.inbound` - WhatsApp events
   - `fte.channels.webform.inbound` - Web form events
   - `fte.escalations` - Escalation events
   - `fte.metrics` - Performance metrics
   - `fte.dlq` - Dead letter queue

2. **FTEKafkaProducer** class
3. **FTEKafkaConsumer** class
4. **InMemoryEventBus** class (fallback when Kafka unavailable)
5. **Factory function** `get_event_bus()`

Include proper error handling, structlog logging, JSON serialization/deserialization. Use aiokafka for the real Kafka client. The InMemoryEventBus should use `asyncio.Queue` per topic and `asyncio.Task` for consuming.

## Response snapshot

Created `src/kafka_client.py` with all five components:
- **TOPICS dict**: 7 topic definitions (tickets_incoming, email_inbound, whatsapp_inbound, webform_inbound, escalations, metrics, dlq)
- **FTEKafkaProducer**: async producer with start/stop/publish using AIOKafkaProducer, JSON serialisation
- **FTEKafkaConsumer**: async consumer with start/stop/consume using AIOKafkaConsumer, JSON deserialisation
- **InMemoryEventBus**: fallback using asyncio.Queue per topic and asyncio.Task for consumption loops
- **get_event_bus()**: factory function returning Kafka or InMemory based on settings

All classes use structlog for logging and include proper error handling with exception logging. The module follows the same coding conventions as existing files (e.g., `src/database/connection.py`).

## Outcome

- Impact: Core event streaming infrastructure for the FTE system
- Tests: none (implementation only per task spec)
- Files: src/kafka_client.py created
- Next prompts: Task 5 (Agent Prompts and Formatters), Task 8-10 (channel handlers that use kafka_client)
- Reflection: Module follows existing project patterns; InMemoryEventBus ensures local dev works without Kafka

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): syntax validation PASS
- Prompt variant (if applicable): none
- Next experiment (smallest change to try): add unit tests for InMemoryEventBus
