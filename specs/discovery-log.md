# Discovery Log - Customer Success Digital FTE

**Date:** 2026-02-23
**Source Data:** 50+ sample tickets across 3 channels, brand voice guide, escalation rules, product documentation
**Purpose:** Document patterns discovered during Stage 1 (Incubation) that inform agent design and behavior

---

## 1. Channel-Specific Communication Patterns

### 1.1 Email Channel (20 sample tickets analyzed)

| Attribute | Observed Pattern |
|-----------|-----------------|
| **Tone** | Formal to semi-formal; professional salutations and sign-offs |
| **Length** | 100-300 words average; some exceed 400 words with multi-part questions |
| **Structure** | Subject line + greeting + problem description + context + closing + signature |
| **Customer Expectation** | Detailed, comprehensive responses with numbered steps |
| **Identity Signals** | Full name, company name, job title, email domain |
| **Urgency Indicators** | Explicit deadline mentions ("due today"), impact statements ("affecting our entire team") |

**Key Insight:** Email customers invest time in composing detailed messages and expect equally thorough responses. They often include multiple sub-questions in a single message (e.g., TICKET-002 asked 4 distinct billing questions plus a feature inquiry).

### 1.2 WhatsApp Channel (15 sample tickets analyzed)

| Attribute | Observed Pattern |
|-----------|-----------------|
| **Tone** | Casual, conversational, sometimes terse |
| **Length** | 10-80 words; rarely exceeds 100 words |
| **Structure** | Direct problem statement, minimal context, no formal greeting |
| **Customer Expectation** | Quick, actionable answers in 1-3 short messages |
| **Identity Signals** | Phone number (primary), first name, sometimes email when asked |
| **Urgency Indicators** | "urgent", "asap", "right now", "help me", rapid follow-up messages |

**Key Insight:** WhatsApp customers expect near-instant responses and become frustrated with long-form replies. Multi-message splitting is necessary for anything beyond a quick answer. Escalation keywords ("human", "agent") appear more frequently here than in other channels.

### 1.3 Web Form Channel (15 sample tickets analyzed)

| Attribute | Observed Pattern |
|-----------|-----------------|
| **Tone** | Semi-formal; structured by form fields |
| **Length** | 50-200 words in the message body |
| **Structure** | Pre-categorized via dropdown (category, priority), subject line, message body |
| **Customer Expectation** | Acknowledgment with ticket ID, response via email within SLA |
| **Identity Signals** | Name, email (required fields), optional phone |
| **Urgency Indicators** | Priority selection (dropdown), language in message body |

**Key Insight:** Web form submissions provide the most structured data upfront (category, priority), which enables faster routing and classification. Customers using web forms tend to be more patient and accept async responses.

---

## 2. Category Distribution Analysis

From the 50+ sample tickets, the following category distribution was observed:

| Category | Count | Percentage | Typical Channel | Resolution Pattern |
|----------|-------|------------|-----------------|-------------------|
| Password Reset | 8 | ~16% | All channels equally | Self-service resolution via KB article |
| Feature Questions | 9 | ~18% | Email, Web Form | KB search; may need plan-specific guidance |
| Bug Reports | 7 | ~14% | Email, WhatsApp | Troubleshooting steps; escalate if P1/P2 |
| Billing / Pricing | 8 | ~16% | Email, Web Form | Partial resolution; pricing always escalates |
| Integration Issues | 6 | ~12% | Email | KB article + step-by-step reconnection |
| API Help | 4 | ~8% | Email | Documentation reference + code examples |
| Feedback / Feature Requests | 4 | ~8% | Web Form | Acknowledge and log; no escalation needed |
| Account / Access Issues | 4 | ~8% | WhatsApp, Email | Identity verification + admin actions |

**Key Findings:**
- Password reset and feature questions together represent ~34% of all tickets -- these are the highest-value automation targets.
- Billing-related tickets almost always require partial or full escalation due to pricing guardrails.
- Bug reports split cleanly: simple bugs resolve with troubleshooting steps, platform-wide bugs require engineering escalation.
- API help requests are exclusively from email channel and tend to come from technical users.

---

## 3. Escalation Triggers Found in Real Data

### 3.1 Legal Language (detected in 3 tickets)

- TICKET-004: "legal department requires confirmation regarding data residency"
- TICKET-006: "escalating this through our legal department"
- TICKET-014: "breach of contract", "legal counsel"

**Pattern:** Legal language appears primarily in email from enterprise or regulated-industry customers (legal firms, financial services). These always require immediate escalation to Support Lead with `LEGAL_ESCALATION` flag.

### 3.2 Pricing and Refund Requests (detected in 6 tickets)

- TICKET-002: "upgrade from Starter to Professional" (pricing details)
- TICKET-006: "request for refund"
- TICKET-017: "how much does it cost to add more storage?"
- TICKET-029: WhatsApp pricing inquiry

**Pattern:** Any mention of specific pricing numbers, discount requests, or refund processing must escalate. General plan comparison info (features per tier) can be answered, but dollar amounts and custom pricing require Sales or Finance team routing.

### 3.3 Profanity and Aggressive Sentiment (detected in 4 tickets)

- TICKET-010: "this is absolutely RIDICULOUS", "UNACCEPTABLE" (all-caps aggression)
- TICKET-006: threat of negative reviews + legal escalation
- TICKET-022: WhatsApp message with explicit profanity
- TICKET-035: repeated exclamation marks with negative sentiment

**Pattern:** Sentiment below 0.3 threshold consistently co-occurs with: ALL-CAPS words, multiple exclamation marks, personal insults, and threat language. The agent must respond with empathy first, then escalate.

### 3.4 Failed Knowledge Base Searches (detected in 2 scenarios)

- TICKET-013: Question about undocumented API endpoint behavior
- TICKET-041: Niche Jira two-way sync configuration issue

**Pattern:** KB misses cluster around edge cases in integrations and API usage not covered by standard documentation. After 2 failed searches (confidence < 0.5), escalate with `KB_MISS` flag and include search queries attempted.

### 3.5 Explicit Human Requests (detected in 5 tickets)

- TICKET-010: "I want to speak to a real person"
- TICKET-022: "connect me to a human"
- TICKET-027: WhatsApp "agent" keyword
- TICKET-033: "representative please"
- TICKET-040: "stop the bot"

**Pattern:** Human agent requests appear across all channels but are most frequent on WhatsApp. Keywords are well-defined ("human", "agent", "representative", "real person"). Must always be honored immediately without argument.

---

## 4. Response Style Preferences Per Channel

### 4.1 Email Response Style

- **Greeting:** "Hi [First Name]," -- personal, warm
- **Acknowledgment:** 1-2 sentences validating the customer's situation
- **Solution:** Numbered steps with bold UI element names
- **Links:** Include KB article URLs and relevant documentation
- **Closing:** "Best regards, TechCorp Support Team" + contact info block
- **Length Target:** 150-400 words
- **Ticket Reference:** Always include in subject line

### 4.2 WhatsApp Response Style

- **Greeting:** "Hi [First Name]!" -- casual, exclamation mark
- **Solution:** 1-2 short sentences max per message bubble
- **Multi-message:** Break long answers into 2-3 separate messages
- **Emojis:** Sparingly (thumbs up, checkmark only); never laughing, fire, or skull
- **Length Target:** Under 300 characters per message
- **Ticket Reference:** Only when explicitly asked

### 4.3 Web Form Response Style

- **Greeting:** "Hi [First Name]," -- semi-formal
- **Context:** "Thank you for contacting TechCorp Support. I have reviewed your request."
- **Solution:** Clear and direct with helpful links
- **Alternative Channels:** Always mention email, WhatsApp, and KB as follow-up options
- **Length Target:** 100-300 words
- **Ticket Reference:** Always include

---

## 5. Cross-Channel Customer Identification Patterns

### 5.1 Identity Resolution Strategy

Customers contact support through multiple channels. The following identification patterns were observed:

| Identifier | Primary Channel | Uniqueness | Notes |
|-----------|----------------|------------|-------|
| Email address | Email, Web Form | High | Most reliable cross-channel identifier |
| Phone number | WhatsApp | High | WhatsApp number = phone number; reliable |
| Full name | All channels | Low | Not unique; use as secondary signal |
| Company domain | Email | Medium | Email domain clusters identify same org |
| Ticket history | All | High | Prior ticket references enable continuity |

### 5.2 Resolution Flow

1. **WhatsApp inbound:** Extract phone number -> query `customer_identifiers` table -> match to customer record
2. **Email inbound:** Extract sender email -> query `customer_identifiers` table -> match to customer record
3. **Web form inbound:** Use submitted email -> query `customer_identifiers` table -> match or create new customer
4. **Cross-reference:** When a WhatsApp user provides their email, link the phone identifier to the existing email-based customer record

### 5.3 Observed Multi-Channel Journeys

- Customer submits web form -> follows up via email (same email links them)
- Customer emails support -> follows up on WhatsApp (needs to provide email to link)
- Customer on WhatsApp -> escalated -> human responds via email (ticket links them)

---

## 6. Performance Insights and Response Time Targets

### 6.1 Processing Benchmarks

| Metric | Target | Rationale |
|--------|--------|-----------|
| AI processing time | < 3 seconds | KB search + agent inference + formatting |
| End-to-end delivery | < 30 seconds | Processing + channel API latency |
| KB search latency | < 500ms | pgvector semantic search with index |
| Customer ID resolution | < 200ms | Indexed lookup on email/phone |
| Ticket creation | < 300ms | Single INSERT with RETURNING |

### 6.2 Accuracy Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Resolution accuracy | > 85% | Correct resolution on first response |
| Escalation rate | < 20% | % tickets requiring human handoff |
| Cross-channel ID accuracy | > 95% | Correct customer matching across channels |
| Category classification | > 90% | Correct ticket category assignment |
| Sentiment detection | > 80% | Correct sentiment polarity classification |

### 6.3 Discovered Bottlenecks

- **KB search quality:** Semantic search accuracy depends heavily on embedding quality. Mock embeddings (random vectors) are insufficient for real testing; production needs OpenAI embeddings.
- **WhatsApp message splitting:** Messages over 300 characters need intelligent splitting at sentence boundaries, not arbitrary truncation.
- **Escalation handoff completeness:** The handoff template must include full conversation history; partial handoffs waste human agent time.

---

## 7. Edge Cases Catalog

| ID | Scenario | Channel | Expected Behavior |
|----|----------|---------|-------------------|
| EC-01 | Customer sends empty message | WhatsApp | Prompt for clarification |
| EC-02 | Message in non-English language | All | Respond in same language if supported; else English |
| EC-03 | Customer sends same ticket twice | Web Form | Deduplicate; acknowledge and reference first ticket |
| EC-04 | Pricing question disguised as feature question | Email | Detect pricing intent; escalate to sales |
| EC-05 | Customer threatens legal action AND requests refund | Email | Multi-team escalation (Support Lead + Finance) |
| EC-06 | WhatsApp media attachment (image/video) | WhatsApp | Acknowledge receipt; note that image analysis is out of scope |
| EC-07 | After-hours P1 escalation | All | Queue for on-call engineer; immediate acknowledgment |
| EC-08 | Customer contacts 3+ times for same issue | All | Trigger REPEAT_CONTACT escalation |
| EC-09 | API rate limit question from Starter plan user | Email | Explain limits; suggest upgrade for higher limits |
| EC-10 | Customer asks about competitor comparison | All | Redirect to features; never disparage competitors |

---

## 8. Summary of Key Design Decisions from Discovery

1. **Channel-first formatting:** All responses must be formatted per channel rules before delivery. A single response template does not work across channels.
2. **Ticket-before-response:** Every interaction creates a ticket first, ensuring auditability even if the response fails to deliver.
3. **Escalation is non-negotiable:** Legal, profanity, and human-request triggers bypass all de-escalation logic.
4. **Cross-channel identity is a first-class concern:** The `customer_identifiers` table with type-based lookup is essential for conversation continuity.
5. **Mock-first development:** All external services (OpenAI, Gmail, Twilio) have mock implementations, enabling full-flow testing without API keys.
