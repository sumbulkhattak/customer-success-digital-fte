---
id: 1
title: Create Context Dossier for Customer Success AI Agent
stage: general
date: 2026-02-23
surface: agent
model: claude-opus-4-6
feature: none
branch: master
user: user
command: task-2-context-dossier
labels: ["context", "knowledge-base", "customer-success", "hackathon"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - context/company-profile.md
  - context/product-docs.md
  - context/sample-tickets.json
  - context/escalation-rules.md
  - context/brand-voice.md
tests:
  - Validated sample-tickets.json has 55 tickets (50+ required)
  - Validated JSON schema completeness for all ticket fields
  - Validated unique ticket IDs (no duplicates)
  - Validated product-docs.md is 909 lines (300+ required)
  - Validated channel distribution: 23 email, 17 WhatsApp, 15 web form
  - Validated escalation scenarios present (legal, profanity, human request)
---

## Prompt

You are implementing Task 2 of a Customer Success Digital FTE project. This is a hackathon project building a 24/7 AI Customer Success agent for "TechCorp" - a SaaS project management platform.

**Your task:** Create the context dossier - all the reference documents the AI agent will use.

Create these 5 files in a `context/` directory:
1. context/company-profile.md - Company profile for TechCorp
2. context/product-docs.md - Detailed product documentation (300+ lines knowledge base)
3. context/sample-tickets.json - 50+ sample tickets (20 email, 15 WhatsApp, 15 web form)
4. context/escalation-rules.md - Escalation rules and routing
5. context/brand-voice.md - Brand voice guide with channel-specific guidelines

## Response snapshot

Created all 5 context dossier files:
- **company-profile.md** (161 lines): TechCorp company overview, pricing tiers, support structure, SLAs, key contacts, compliance info
- **product-docs.md** (909 lines): Comprehensive knowledge base covering getting started, account management, core features, integrations (Slack, GitHub, Jira, Zapier, API), troubleshooting, and 10 error codes (ERR-001 through ERR-010)
- **sample-tickets.json** (55 tickets): 23 email, 17 WhatsApp, 15 web form tickets with realistic customer messages, covering all 7 categories. Includes escalation scenarios: legal threats, profanity, human agent requests, angry customers
- **escalation-rules.md** (349 lines): Automatic triggers (legal, profanity/sentiment, KB miss, human request, WhatsApp keywords, repeat contact), severity levels P1-P4, routing matrix to 7 teams, handoff template, after-hours protocol
- **brand-voice.md** (465 lines): Tone attributes, channel-specific formatting (email/WhatsApp/web form), words to use/avoid, 6 example responses, localization notes, brand voice checklist

## Outcome

- Impact: Created complete knowledge base and reference documents for AI Customer Success agent
- Tests: All validation checks passed (ticket count, schema, line counts, distribution)
- Files: 5 files created in context/ directory
- Next prompts: Task 3 (PostgreSQL Database Schema), Task 5 (Agent Prompts and Formatters)
- Reflection: Comprehensive context dossier enables the AI agent to handle diverse customer inquiries across email, WhatsApp, and web form channels with proper escalation and brand voice

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Manual validation PASS (55 tickets, 909 lines product docs, all schemas valid)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test agent prompt retrieval against these context documents
