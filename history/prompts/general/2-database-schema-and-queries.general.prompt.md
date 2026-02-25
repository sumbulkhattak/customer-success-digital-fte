---
id: 2
title: Database Schema and Queries
stage: green
date: 2026-02-23
surface: agent
model: claude-opus-4-6
feature: database
branch: master
user: user
command: task-3-implementation
labels: ["database", "postgresql", "schema", "asyncpg", "queries", "seed"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - src/database/schema.sql
  - src/database/connection.py
  - src/database/queries.py
  - src/database/seed.py
tests:
  - none
---

## Prompt

You are implementing Task 3 of a Customer Success Digital FTE project - a 24/7 AI agent handling support across Email, WhatsApp, and Web Form channels. Create 4 files: src/database/schema.sql (complete PostgreSQL schema with 8 tables), src/database/connection.py (asyncpg pool manager), src/database/queries.py (comprehensive async query functions for CRM operations), src/database/seed.py (seed script for knowledge base and channel configs).

## Response snapshot

Created all 4 database layer files:
1. **schema.sql** - Complete PostgreSQL schema with 8 tables (customers, customer_identifiers, conversations, messages, tickets, knowledge_base, channel_configs, agent_metrics) plus 12 indexes and pgvector extension.
2. **connection.py** - Database connection pool manager using asyncpg with get_db_pool(), init_db(), and close_db() functions.
3. **queries.py** - 13 async query functions: create_customer, find_customer_by_email, find_customer_by_phone, create_conversation, get_active_conversation, create_message, create_ticket, update_ticket_status, get_ticket_by_id, search_knowledge_base, get_customer_history, record_metric, get_channel_metrics.
4. **seed.py** - Seed script that parses product-docs.md into sections, generates mock embeddings, and seeds channel configs for email/whatsapp/web_form.

## Outcome

- Impact: Database layer fully implemented for Customer Success Digital FTE
- Tests: none
- Files: 4 files created (schema.sql, connection.py, queries.py, seed.py)
- Next prompts: Task 4 (Kafka Event Streaming Client), Task 5 (Agent Prompts and Formatters)
- Reflection: Straightforward file creation from provided specifications

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): N/A - no tests defined for this task
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Add unit tests with mock database for query functions
