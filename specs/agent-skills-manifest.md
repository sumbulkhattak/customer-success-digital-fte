# Agent Skills Manifest - Customer Success Digital FTE

**Version:** 1.0
**Date:** 2026-02-23
**Agent:** TechCorp Customer Success AI Agent
**Total Skills:** 5

---

## Skill Overview

| # | Skill Name | Primary Function | Criticality |
|---|-----------|-----------------|-------------|
| 1 | Knowledge Retrieval | Find answers in product documentation | Critical |
| 2 | Sentiment Analysis | Detect customer mood and adjust behavior | Critical |
| 3 | Escalation Decision | Determine when and how to hand off to humans | Critical |
| 4 | Channel Adaptation | Format responses per channel requirements | Critical |
| 5 | Customer Identification | Resolve customer identity across channels | Critical |

---

## Skill 1: Knowledge Retrieval

### Description

Searches TechCorp product documentation stored in the PostgreSQL `knowledge_base` table using pgvector semantic similarity. Returns the most relevant documentation sections to answer customer questions about product features, account management, troubleshooting, integrations, and error codes. Falls back to text-based keyword search when semantic results score below the confidence threshold.

### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `query` | string | Yes | The customer's question or search terms, extracted from their message |
| `max_results` | integer | No (default: 3) | Maximum number of KB articles to return |
| `category_filter` | string | No | Optional category constraint (e.g., "troubleshooting", "integrations") |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `results` | array | List of matching KB articles |
| `results[].title` | string | Article title (e.g., "Password Reset", "Slack Integration Setup") |
| `results[].content` | string | Relevant content excerpt (truncated to 500 chars) |
| `results[].relevance_score` | float | Cosine similarity score (0.0 - 1.0) |
| `results[].category` | string | Documentation category |
| `search_method` | string | "semantic" or "text_fallback" |
| `total_matches` | integer | Total number of matches found before limiting |

### Success Criteria

- Returns relevant results for > 85% of documented topics within 500ms
- Semantic search relevance score > 0.5 for top result on known questions
- Text fallback activates automatically when semantic scores are all below 0.5
- Returns empty results gracefully (not an error) when no match is found
- Handles multi-topic queries by returning results across categories

### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Query matches no KB articles | Return empty results array; agent should acknowledge inability to find answer |
| Query is vague or single word | Attempt search; if results score low, ask customer for clarification |
| Query contains typos | Semantic search handles minor typos via embedding similarity; text search uses ILIKE with wildcards |
| Query about undocumented feature | No results returned; after 2 failures, trigger `KB_MISS` escalation |
| Query in non-English language | Translate to English conceptually via embedding space; may have lower accuracy |
| Very long query (500+ chars) | Truncate to first 200 chars for embedding generation; use full text for fallback |

### Implementation Notes

- Embeddings are generated via OpenAI `text-embedding-3-small` model in production
- Mock embeddings use random 1536-dimensional vectors (for flow testing only)
- pgvector index type: IVFFlat with 100 lists for collections > 1000 rows, or exact search for smaller sets
- Knowledge base is seeded from `context/product-docs.md` split into sections by heading

---

## Skill 2: Sentiment Analysis

### Description

Analyzes the emotional tone and sentiment of incoming customer messages to detect frustration, anger, urgency, and satisfaction levels. The sentiment score drives two critical behaviors: (1) triggering escalation when sentiment drops below the 0.3 threshold, and (2) adjusting response tone to match the customer's emotional state (more empathetic for frustrated customers, more upbeat for satisfied ones).

### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `message_text` | string | Yes | The raw customer message text |
| `conversation_history` | array | No | Prior messages in the conversation for trend detection |
| `channel` | string | No | Channel context (WhatsApp messages tend to be more terse, not necessarily angry) |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `sentiment_score` | float | Overall sentiment (0.0 = extremely negative, 1.0 = extremely positive) |
| `sentiment_label` | string | Human-readable label: "very_negative", "negative", "neutral", "positive", "very_positive" |
| `escalation_recommended` | boolean | True if score < 0.3 or profanity detected |
| `profanity_detected` | boolean | True if explicit profanity or obscenities found |
| `urgency_level` | string | "low", "medium", "high", "critical" based on language cues |
| `tone_adjustment` | string | Recommended tone shift: "empathetic", "standard", "upbeat" |
| `confidence` | float | Confidence in sentiment classification (0.0 - 1.0) |

### Success Criteria

- Correctly classifies sentiment polarity on > 80% of test messages
- Detects profanity with > 95% precision (very few false positives)
- Correctly identifies ALL-CAPS aggressive messages as negative sentiment
- Distinguishes between terse WhatsApp messages (neutral) and genuinely angry messages (negative)
- Sentiment trend detection: flags when sentiment degrades across consecutive messages

### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Message is entirely in ALL CAPS | Weight as potentially aggressive; combine with keyword analysis for confirmation |
| Message uses sarcasm ("Great, just great") | May misclassify; rely on context from conversation history |
| Short message ("ok") | Classify as neutral; do not over-interpret brevity |
| Message contains profanity in a non-angry context | Flag profanity as detected but check overall context before escalation |
| Customer is frustrated but polite | Detect negative sentiment (e.g., "frustrated", "disappointed") but note politeness; use empathetic tone |
| Empty or whitespace-only message | Return neutral sentiment with low confidence |
| Mixed sentiment ("love the product but this bug is awful") | Score as mildly negative; extract both positive and negative signals |

### Implementation Notes

- Primary implementation uses TextBlob for basic polarity analysis
- Production upgrade path: fine-tuned sentiment model or OpenAI function call
- Profanity detection uses a curated keyword list (not regex) to reduce false positives
- Channel context matters: WhatsApp users write shorter, more direct messages that are not inherently aggressive
- Sentiment is calculated per-message and aggregated per-conversation for trend analysis

---

## Skill 3: Escalation Decision

### Description

Evaluates whether a customer interaction should be escalated from the AI agent to a human support team member. Uses a rule-based decision engine that checks multiple trigger conditions, classifies severity, and determines the correct routing team. When escalation is triggered, the skill generates a structured handoff document containing full conversation context, customer information, AI actions taken, and recommended next steps.

### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `message_text` | string | Yes | Current customer message |
| `sentiment_score` | float | Yes | From Sentiment Analysis skill |
| `kb_search_failures` | integer | Yes | Count of failed KB searches in this conversation |
| `channel` | string | Yes | Current communication channel |
| `customer_history` | object | No | Prior tickets and escalation history |
| `conversation_messages` | array | No | Full conversation transcript |
| `ticket_id` | string | Yes | Current ticket reference |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `should_escalate` | boolean | Final escalation decision |
| `escalation_flag` | string | Flag type (e.g., `LEGAL_ESCALATION`, `SENTIMENT_ESCALATION`, `KB_MISS`) |
| `severity` | string | P1 (Critical), P2 (High), P3 (Medium), P4 (Low) |
| `routing_team` | string | Target team: "support_lead", "sales", "finance", "security", "engineering", "support_general" |
| `routing_contact` | string | Email address of the routing destination |
| `triggers_matched` | array | List of all triggers that matched (may be multiple) |
| `handoff_document` | string | Structured escalation handoff text with full context |
| `customer_response` | string | Pre-generated empathetic response to send to the customer |
| `estimated_response_time` | string | SLA-based estimate (e.g., "within 15 minutes", "within 4 hours") |

### Success Criteria

- All legal language triggers escalate with 100% recall (no false negatives)
- All explicit human requests are honored immediately (100% compliance)
- Profanity detection triggers escalation with > 95% precision
- Severity classification matches expected P1-P4 level on > 90% of test cases
- Routing directs tickets to the correct team on > 95% of escalated tickets
- Handoff document contains all required fields (ticket ID, customer info, conversation history, AI actions, reason, next steps)
- Escalation rate stays below 20% of total tickets

### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Multiple triggers match simultaneously | Use highest severity; route to primary team; notify secondary teams if multi-team routing applies |
| Legal + refund in same message | Route to Support Lead (primary) AND notify Finance (secondary) |
| Customer says "agent" in a technical context (e.g., "AI agent") | Use surrounding context to distinguish from escalation request; false positive rate < 5% |
| WhatsApp keyword "urgent" in first message | Attempt one AI response first; escalate if keyword repeats in second message |
| Repeat contact but different issue category | Do not trigger REPEAT_CONTACT; only matches when category is similar |
| After-hours P1 escalation | Trigger on-call engineer notification via PagerDuty; send customer acknowledgment with on-call ETA |
| Customer de-escalates after initial anger | If customer explicitly says "never mind" or "it is resolved", do not escalate; confirm resolution |

### Trigger Priority Order

When multiple triggers are detected, severity is determined by the highest-priority trigger:

| Priority | Trigger | Severity | Immediate? |
|----------|---------|----------|-----------|
| 1 | P1 incident (system outage) | P1 - Critical | Yes |
| 2 | Security concern | P1 - Critical | Yes |
| 3 | Legal language | P2 - High | Yes |
| 4 | Profanity / aggressive sentiment | P2 - High | Yes (after empathetic response) |
| 5 | Explicit human request | P3 - Medium | Yes |
| 6 | Refund request | P3 - Medium | After initial response |
| 7 | Pricing question | P3 - Medium | After providing general info |
| 8 | KB search failure (2+) | P3 - Medium | After second failure |
| 9 | WhatsApp escalation keyword | P3 - Medium | Conditional (see rules) |
| 10 | Repeat contact (3+) | P3 - Medium | After verifying history |

### Implementation Notes

- Rule engine evaluates triggers in priority order; stops at first match for severity assignment but continues scanning for all matches
- Handoff document follows the template defined in `context/escalation-rules.md` section 4.1
- Escalation events are published to the `fte.escalations` Kafka topic
- Ticket status is updated to "escalated" in PostgreSQL upon escalation
- Response templates are pre-defined per escalation type (see brand voice guide section 6.6)

---

## Skill 4: Channel Adaptation

### Description

Transforms the AI-generated response into the appropriate format, tone, length, and structure for the target communication channel. This skill ensures that a single logical response is delivered in a way that feels native to each channel: formal and detailed for email, concise and conversational for WhatsApp, and structured with helpful links for web form replies.

### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `raw_response` | string | Yes | The unformatted response text from the AI agent |
| `channel` | string | Yes | Target channel: "email", "whatsapp", "web_form" |
| `customer_name` | string | Yes | Customer's first name for personalization |
| `ticket_id` | string | No | Ticket reference number (required for email and web form) |
| `original_subject` | string | No | Original message subject (for email reply subject line) |
| `sentiment_tone` | string | No | Tone adjustment hint from Sentiment Analysis ("empathetic", "standard", "upbeat") |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `formatted_response` | string or array | Single string for email/web; array of message strings for WhatsApp |
| `subject_line` | string | Email/web form response subject line (null for WhatsApp) |
| `metadata` | object | Channel-specific metadata (e.g., thread_id for Gmail, message_count for WhatsApp) |
| `word_count` | integer | Total word count of formatted response |
| `character_count` | integer | Total character count (critical for WhatsApp) |
| `within_limits` | boolean | Whether the response is within channel length constraints |

### Success Criteria

- Email responses include: greeting with first name, empathetic opening, solution with numbered steps, closing with signature block, ticket reference in subject
- WhatsApp responses stay under 300 characters per message; split into max 3 messages at sentence boundaries
- Web form responses include: ticket reference, solution, help center link, alternative contact methods
- Response tone matches the sentiment adjustment (more empathetic when customer is frustrated)
- No channel receives a response that violates its formatting rules
- Word count stays within bounds: email 150-400, WhatsApp < 300 chars/msg, web 100-300 words

### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Response too long for WhatsApp (> 900 chars total) | Truncate to most important information; add "Would you like more details?" as final message |
| Response too short for email (< 50 words) | Pad with empathetic opening and helpful closing; add relevant KB link |
| Customer name is unknown | Use "there" or omit name: "Hi there!" for WhatsApp, "Hi," for email |
| Ticket ID not available for email | Omit from subject line; mention "a reference number will be assigned shortly" in body |
| Response contains code or technical content | Email: use code formatting; WhatsApp: simplify or suggest "I can email you the detailed steps" |
| Multi-step instructions for WhatsApp | Send steps as numbered list in one message if under 300 chars; split across messages if longer |
| Escalation response formatting | Use pre-defined escalation templates per channel (more detailed for email, concise for WhatsApp) |

### Channel Format Templates

**Email:**
```
Subject: Re: [Original Subject] - TechCorp Support [TICKET-ID]

Hi [First Name],

[Empathetic opening]

[Solution with numbered steps]

[Next steps or follow-up]

Best regards,
TechCorp Support Team
support@techcorp.io | https://support.techcorp.io
```

**WhatsApp:**
```
Message 1: Hi [First Name]! [Brief acknowledgment + solution]
Message 2: [Additional details if needed]
Message 3: [Follow-up question or next step]
```

**Web Form:**
```
Subject: Re: [Original Subject] - Reference #[TICKET-ID]

Hi [First Name],

Thank you for contacting TechCorp Support.

[Solution]

[Helpful links]

If you need further assistance:
- Reply to this email
- Visit our Help Center: https://support.techcorp.io/kb
- Chat with us on WhatsApp: +1-555-832-4267

Best regards,
TechCorp Support Team
```

### Implementation Notes

- Formatters are pure functions in `src/agent/formatters.py` with no side effects
- WhatsApp message splitting algorithm: split at sentence boundaries (period, question mark, exclamation mark) and recombine until under 300 chars per message
- Emojis for WhatsApp: restricted to thumbs up, checkmark, waving hand, lightbulb only
- Tone adjustment modifies opening sentence: empathetic adds "I understand your frustration", upbeat uses "Great news!"
- Brand voice checklist is applied programmatically: verify first name used, negative words avoided, channel length respected

---

## Skill 5: Customer Identification

### Description

Resolves the identity of the customer contacting support across multiple communication channels. Uses email addresses, phone numbers, and WhatsApp identifiers to match incoming messages to existing customer records in the PostgreSQL CRM. Enables conversation continuity when a customer switches channels (e.g., starts on WhatsApp, follows up via email) and provides the agent with cross-channel history for context-aware responses.

### Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | string | Yes | Source channel: "email", "whatsapp", "web_form" |
| `email` | string | Conditional | Customer email (required for email and web form channels) |
| `phone` | string | Conditional | Customer phone number (required for WhatsApp channel) |
| `name` | string | No | Customer name if available |
| `company` | string | No | Company name if detectable from email domain or message content |
| `message_metadata` | object | No | Channel-specific metadata (Gmail thread ID, WhatsApp message SID) |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `customer_id` | string (UUID) | The resolved customer ID from the `customers` table |
| `is_new_customer` | boolean | True if a new customer record was created |
| `customer_record` | object | Full customer record (name, email, company, plan_tier, created_at) |
| `known_identifiers` | array | All known identifiers for this customer (emails, phones) |
| `prior_tickets` | array | Summary of prior tickets (id, subject, status, channel, date) |
| `prior_conversations` | integer | Count of prior conversations across all channels |
| `identity_confidence` | string | "exact_match", "probable_match", "new_customer" |
| `linked_channels` | array | Channels this customer has previously used |

### Success Criteria

- Exact match on email or phone resolves to correct customer > 99% of the time
- Cross-channel linking works when customer provides email on WhatsApp
- New customer creation happens only when no matching identifier exists
- Customer history is correctly aggregated across all channels
- Resolution latency < 200ms for indexed lookups
- False positive rate (wrong customer matched) < 0.1%
- Overall cross-channel identification accuracy > 95%

### Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Customer uses personal email on web form, work email on email channel | Two separate customer records unless manually merged; suggest merge to human agent |
| WhatsApp number changes (customer gets new phone) | New identifier created; customer must confirm identity via email to link to existing record |
| Customer email typo on web form | Create new customer record; if customer corrects in follow-up, agent or human can merge |
| Multiple people share a company email (info@company.com) | Treat as single customer record; track by name as secondary differentiator |
| Customer contacts from unrecognized channel after identity established | Ask for email or phone to link to existing record |
| Extremely high volume from same customer (possible spam) | Rate limit detection; flag for review if > 10 tickets in 1 hour |
| Customer explicitly asks to not be identified | Honor request; create anonymous ticket without linking to customer record |

### Identity Resolution Flow

```
1. Extract identifier from inbound message:
   - Email channel: sender email address
   - WhatsApp channel: phone number from Twilio webhook
   - Web form channel: email field from form submission

2. Query customer_identifiers table:
   SELECT c.* FROM customers c
   JOIN customer_identifiers ci ON c.id = ci.customer_id
   WHERE ci.identifier_type = :type
     AND ci.identifier_value = :value

3. If match found:
   - Return existing customer record
   - Load prior tickets and conversations
   - Set identity_confidence = "exact_match"

4. If no match found:
   - Create new customer record
   - Create customer_identifier record
   - Set identity_confidence = "new_customer"
   - Set is_new_customer = true

5. Cross-channel linking (optional):
   - If WhatsApp customer provides email in conversation
   - Check if email matches existing customer
   - If yes: add phone as new identifier for existing customer
   - If no: add email as additional identifier for current customer
```

### Implementation Notes

- All identifier lookups are indexed for sub-millisecond performance
- `customer_identifiers` table supports multiple identifier types: "email", "phone", "whatsapp"
- Phone numbers are normalized to E.164 format before storage and lookup
- Email addresses are lowercased before storage and lookup
- Customer merge (linking two records) is a manual operation by human agents; the AI suggests but does not auto-merge to avoid data corruption
- Conversation continuity: when a customer is identified, the active conversation (if any) is loaded and the new message is appended to the existing thread rather than starting a new conversation

---

## Skill Interaction Map

The 5 skills work together in a defined sequence during message processing:

```
Inbound Message
      |
      v
[Customer Identification] -- Resolve who the customer is
      |
      v
[Sentiment Analysis] -- Assess emotional state of message
      |
      v
[Escalation Decision] -- Check if escalation is needed
      |
      |-- YES --> Generate handoff document
      |           |
      |           v
      |     [Channel Adaptation] -- Format escalation response for channel
      |           |
      |           v
      |     Deliver escalation response + publish to fte.escalations
      |
      |-- NO --> Continue to resolution
              |
              v
        [Knowledge Retrieval] -- Search KB for relevant answer
              |
              v
        Agent generates response using KB results + customer history
              |
              v
        [Channel Adaptation] -- Format response for delivery channel
              |
              v
        Deliver response via channel handler
```

### Skill Dependencies

| Skill | Depends On | Provides To |
|-------|-----------|-------------|
| Customer Identification | Channel metadata | All other skills (customer_id is required) |
| Sentiment Analysis | Raw message text | Escalation Decision, Channel Adaptation |
| Escalation Decision | Sentiment score, KB search results, customer history | Channel Adaptation (for escalation responses) |
| Knowledge Retrieval | Customer query, category context | Agent reasoning (for response generation) |
| Channel Adaptation | Raw response, channel, customer name, sentiment tone | Channel handlers (for delivery) |
