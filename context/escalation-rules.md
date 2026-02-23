# TechCorp Customer Success - Escalation Rules

> **Version:** 2.1 | **Last Updated:** 2025-12-15 | **Owner:** Priya Patel, Head of Support

This document defines when and how the AI Customer Success Agent should escalate conversations to human support, which teams to route to, and what information to include in escalation handoffs.

---

## 1. Automatic Escalation Triggers

The AI agent MUST escalate to a human agent when **any** of the following conditions are detected:

### 1.1 Legal Language Detection

**Trigger:** Message contains legal terminology or threats of legal action.

**Keywords to detect:**
- "lawyer", "attorney", "legal", "lawsuit", "litigation"
- "sue", "court", "legal action", "legal counsel"
- "breach of contract", "terms of service violation"
- "regulatory", "compliance violation", "data breach"
- "class action", "damages", "liability"
- "GDPR request", "data subject access request", "right to be forgotten"
- "subpoena", "cease and desist"

**Action:** Immediately escalate to **Support Lead** (Priya Patel) with flag `LEGAL_ESCALATION`. Do NOT make any legal commitments, interpretations, or promises on behalf of TechCorp.

**Response Template:**
> I understand this involves a legal matter, and I want to make sure it receives the appropriate attention. I am routing your request to our support leadership team who can connect you with the right department. You can expect a response from a human team member within [SLA timeframe]. Your reference number is [TICKET-ID].

---

### 1.2 Profanity and Aggressive Language

**Trigger:** Sentiment analysis score falls below **0.3** (on a 0-1 scale where 0 is extremely negative and 1 is extremely positive), OR explicit profanity is detected.

**Profanity indicators:**
- Explicit profanity or obscenities (any language)
- ALL CAPS messages with aggressive tone
- Personal insults directed at support or company
- Threats (e.g., "I will destroy your reputation", "I'll make sure everyone knows")
- Repeated exclamation marks with negative sentiment (e.g., "This is UNACCEPTABLE!!!")

**Action:** Escalate to **Support Lead** with flag `SENTIMENT_ESCALATION`. Respond with empathy first, then escalate.

**Response Template:**
> I sincerely apologize for the frustration you are experiencing. I completely understand your concern, and I want to make sure we resolve this properly. I am connecting you with a senior support member who can give your case the personal attention it deserves. They will reach out to you within [SLA timeframe]. Your reference number is [TICKET-ID].

---

### 1.3 Knowledge Base Search Failure

**Trigger:** The AI agent fails to find a relevant answer in the knowledge base after **2 or more search attempts** for the same query.

**Indicators:**
- Low confidence score on knowledge base retrieval (< 0.5)
- Customer rephrases the same question after initial response
- Response would require speculation or guessing

**Action:** Escalate to **Support Team** with flag `KB_MISS`. Include the search queries attempted and the customer's question verbatim.

**Response Template:**
> That is a great question, and I want to make sure you get an accurate answer. I am going to connect you with a specialist on our team who can help with this specific topic. They will follow up within [SLA timeframe]. In the meantime, you might find our knowledge base helpful: https://support.techcorp.io/kb. Your reference number is [TICKET-ID].

---

### 1.4 Customer Requests Human Agent

**Trigger:** Customer explicitly asks to speak with a human.

**Keywords to detect:**
- "human", "human agent", "real person", "actual person"
- "representative", "rep", "agent"
- "talk to someone", "speak to someone", "connect me"
- "manager", "supervisor", "escalate"
- "not a bot", "stop the bot", "I don't want to talk to a bot"

**Action:** Immediately honor the request. Escalate to **Support Team** (next available human agent) with flag `HUMAN_REQUESTED`.

**Response Template:**
> Of course! I am connecting you with a human team member right now. Our support team is available Monday through Friday, 9:00 AM to 6:00 PM Eastern Time. [If within business hours:] A team member will be with you shortly. [If outside business hours:] Our team will reach out to you first thing during the next business day. Your reference number is [TICKET-ID].

---

### 1.5 WhatsApp-Specific Escalation Keywords

**Trigger:** WhatsApp messages containing specific escalation keywords (case-insensitive).

**Keywords:**
- "human"
- "agent"
- "representative"
- "help me"
- "call me"
- "phone"
- "urgent"
- "emergency"

**Action:** For WhatsApp channel, these keywords trigger a softer escalation check. If keyword appears AND customer has sent 3+ messages, escalate to human. If keyword appears in first message, attempt one AI response first, then escalate if keyword is repeated.

---

### 1.6 Repeated Contact (Same Issue)

**Trigger:** Customer contacts support about the same issue **3 or more times** without resolution.

**Detection:**
- Same customer email/phone with similar subject/keywords within 7 days
- Customer mentions "I already contacted you about this" or "this is my third time"
- Ticket history shows 2+ prior tickets with matching category

**Action:** Escalate to **Support Lead** with flag `REPEAT_CONTACT`. Include all prior ticket references.

**Response Template:**
> I can see you have contacted us about this before, and I apologize that it has not been fully resolved yet. I am escalating this to a senior team member who will take personal ownership of your case. You will hear from them within [SLA timeframe]. Your reference number is [TICKET-ID].

---

## 2. Severity Levels

All tickets must be classified into one of four severity levels. Severity determines response time SLA and escalation path.

### P1 - Critical

| Field              | Details                                           |
|--------------------|---------------------------------------------------|
| **Definition**     | System-wide outage, data loss, security breach, or complete inability to access the platform |
| **Impact**         | All or most users on an account are affected       |
| **Examples**       | Platform down, ERR-008 (subscription expired unexpectedly), data disappearing, unauthorized access, full team lockout |
| **Response SLA**   | Acknowledge within **15 minutes**                  |
| **Resolution SLA** | **4 hours**                                        |
| **Escalation**     | Immediately to **Engineering Team** + **Support Lead** |
| **On-Call**        | Triggers after-hours on-call engineer notification |
| **Communication**  | Status updates to customer every **30 minutes**    |

### P2 - High

| Field              | Details                                           |
|--------------------|---------------------------------------------------|
| **Definition**     | Key feature is broken or severely degraded for a specific user or team |
| **Impact**         | One or more users significantly impacted; workaround may exist |
| **Examples**       | Integration completely non-functional, mobile app crashes consistently, Kanban board not loading, unable to create tasks |
| **Response SLA**   | Acknowledge within **1 hour**                      |
| **Resolution SLA** | **24 hours**                                       |
| **Escalation**     | To **Engineering Team** if not resolved within 4 hours |
| **Communication**  | Status updates to customer every **4 hours**       |

### P3 - Medium

| Field              | Details                                           |
|--------------------|---------------------------------------------------|
| **Definition**     | Non-critical feature issue, how-to question, or configuration assistance |
| **Impact**         | Single user affected; functionality is available but inconvenient |
| **Examples**       | How to set up integrations, calendar timezone wrong, 2FA setup help, feature questions, export assistance |
| **Response SLA**   | Acknowledge within **4 hours**                     |
| **Resolution SLA** | **72 hours**                                       |
| **Escalation**     | To **Support Lead** if not resolved within 48 hours |
| **Communication**  | Status updates as meaningful progress is made       |

### P4 - Low

| Field              | Details                                           |
|--------------------|---------------------------------------------------|
| **Definition**     | Feature request, feedback, cosmetic issue, or general inquiry |
| **Impact**         | No operational impact; enhancement or informational |
| **Examples**       | Feature requests, UI improvement suggestions, documentation feedback, general questions about roadmap |
| **Response SLA**   | Acknowledge within **24 hours**                    |
| **Resolution SLA** | Best effort (no formal SLA)                        |
| **Escalation**     | To **Product Team** if feature request has 10+ votes |
| **Communication**  | One-time acknowledgment with follow-up if status changes |

---

## 3. Routing Rules

Based on ticket category and content, route escalations to the appropriate team.

### 3.1 Routing Matrix

| Trigger / Category            | Route To              | Contact                          | Flag                    |
|-------------------------------|-----------------------|----------------------------------|-------------------------|
| **Pricing questions**         | Sales Team            | rachel.thompson@techcorp.io      | `SALES_INQUIRY`         |
| **Enterprise inquiries**      | Sales Team            | rachel.thompson@techcorp.io      | `ENTERPRISE_INQUIRY`    |
| **Discount requests**         | Sales Team            | rachel.thompson@techcorp.io      | `DISCOUNT_REQUEST`      |
| **Refund requests**           | Finance Team          | billing@techcorp.io              | `REFUND_REQUEST`        |
| **Billing disputes**          | Finance Team          | billing@techcorp.io              | `BILLING_DISPUTE`       |
| **Double charges**            | Finance Team          | billing@techcorp.io              | `BILLING_ERROR`         |
| **Security concerns**         | Security Team         | security@techcorp.io             | `SECURITY_ESCALATION`   |
| **Data breach reports**       | Security Team         | security@techcorp.io             | `SECURITY_CRITICAL`     |
| **Vulnerability reports**     | Security Team         | security@techcorp.io             | `SECURITY_VULN`         |
| **Bug reports (P1/P2)**       | Engineering Team      | david.kim@techcorp.io            | `ENGINEERING_BUG`       |
| **Performance issues**        | Engineering Team      | david.kim@techcorp.io            | `ENGINEERING_PERF`      |
| **Data loss reports**         | Engineering Team      | david.kim@techcorp.io            | `ENGINEERING_DATALOSS`  |
| **Legal threats/mentions**    | Support Lead          | priya.patel@techcorp.io          | `LEGAL_ESCALATION`      |
| **Angry customers (low sentiment)** | Support Lead   | priya.patel@techcorp.io          | `SENTIMENT_ESCALATION`  |
| **Repeat unresolved issues**  | Support Lead          | priya.patel@techcorp.io          | `REPEAT_CONTACT`        |
| **Human agent requests**      | Support Team (general)| support@techcorp.io              | `HUMAN_REQUESTED`       |
| **General support**           | Support Lead          | priya.patel@techcorp.io          | `GENERAL_ESCALATION`    |
| **Compliance/audit requests** | Security + Support    | security@techcorp.io             | `COMPLIANCE_REQUEST`    |
| **Feature requests (10+ votes)** | Product Team      | product@techcorp.io              | `FEATURE_REQUEST`       |

### 3.2 Multi-Team Routing

Some escalations require notification to multiple teams:

| Scenario                        | Primary Route    | Also Notify        |
|---------------------------------|------------------|---------------------|
| Security breach + data loss     | Security Team    | Engineering Team    |
| Legal + billing dispute         | Support Lead     | Finance Team        |
| Bug affecting Enterprise client | Engineering Team | Account Manager     |
| Angry customer + refund request | Support Lead     | Finance Team        |

---

## 4. Escalation Response Template

When escalating, the AI agent MUST include the following structured handoff information for the human agent.

### 4.1 Escalation Handoff Format

```
=== ESCALATION HANDOFF ===

Ticket ID:        [TICKET-ID]
Escalation Flag:  [FLAG from routing rules]
Severity:         [P1/P2/P3/P4]
Timestamp:        [ISO 8601 timestamp]

--- CUSTOMER INFO ---
Name:             [Customer name]
Email:            [Customer email]
Phone:            [Customer phone, if available]
Company:          [Company name, if known]
Plan:             [Starter/Professional/Enterprise, if known]
Channel:          [email/whatsapp/web_form]

--- ISSUE SUMMARY ---
Category:         [password_reset/feature_question/bug_report/billing/feedback/integration/api_help]
Subject:          [One-line summary]
Description:      [2-3 sentence summary of the issue]

--- CONVERSATION HISTORY ---
[Full conversation transcript between AI and customer]

--- AI ACTIONS TAKEN ---
- [List of actions the AI already attempted]
- [Knowledge base articles referenced]
- [Solutions suggested]

--- ESCALATION REASON ---
[Why this is being escalated - specific trigger matched]

--- RECOMMENDED NEXT STEPS ---
1. [Suggested action for human agent]
2. [Additional steps if applicable]
3. [Any time-sensitive elements]

--- CUSTOMER SENTIMENT ---
Score: [0.0 - 1.0]
Notes: [Brief sentiment assessment]

=== END HANDOFF ===
```

### 4.2 Channel-Specific Escalation Notes

**Email Escalations:**
- Full email thread is included in handoff
- Human agent should respond via email within the SLA
- Use email signature block in response
- CC relevant internal stakeholders if P1/P2

**WhatsApp Escalations:**
- Conversation transcript included
- Human agent should respond via WhatsApp if within business hours
- If outside hours, send a WhatsApp message acknowledging and follow up during business hours
- Keep WhatsApp responses concise (under 300 characters per message)

**Web Form Escalations:**
- Original form submission included
- Human agent should respond via email to the customer's submitted email
- Include the ticket reference number in the subject line

---

## 5. Escalation SLA Monitoring

### 5.1 Internal SLA for Escalation Handling

| Metric                                    | Target                    |
|-------------------------------------------|---------------------------|
| Time from AI escalation to human pickup   | < 15 minutes (P1), < 1 hour (P2), < 4 hours (P3/P4) |
| Customer notification of escalation       | Immediate (AI sends)       |
| First human response after pickup         | < 30 minutes (P1), < 2 hours (P2) |
| Escalation resolution rate within SLA     | > 90%                      |

### 5.2 Escalation Metrics to Track

- Total escalations per day/week/month
- Escalation rate (escalated / total tickets)
- Escalation by trigger type (legal, sentiment, KB miss, human request)
- Average time to human pickup
- Escalation resolution time
- Customer satisfaction after escalation (CSAT)
- Repeat escalation rate (same customer, same issue)

---

## 6. De-Escalation Guidelines

The AI agent should attempt de-escalation before escalating when appropriate (does NOT apply to legal, security, or explicit human requests).

### 6.1 De-Escalation Steps

1. **Acknowledge** the customer's frustration explicitly
2. **Apologize** sincerely for the inconvenience
3. **Clarify** the specific issue (ask targeted questions)
4. **Offer** a concrete solution or next step
5. **Confirm** if the customer is satisfied with the proposed resolution

### 6.2 When NOT to Attempt De-Escalation

- Legal language detected (always escalate immediately)
- Security concerns (always escalate immediately)
- Customer explicitly requests human (always honor immediately)
- P1 severity (always escalate immediately)
- Profanity in 2+ consecutive messages (escalate after first empathetic response)

---

## 7. After-Hours Protocol

### 7.1 Business Hours Definition

- **Business Hours:** Monday - Friday, 9:00 AM - 6:00 PM EST (UTC-5)
- **After Hours:** All other times including weekends and US federal holidays

### 7.2 After-Hours Handling

| Severity | After-Hours Action                                  |
|----------|-----------------------------------------------------|
| P1       | Trigger on-call engineer notification via PagerDuty  |
| P2       | Queue for first-thing morning handling; send acknowledgment |
| P3       | Queue for business hours; send acknowledgment with ETA |
| P4       | Queue for business hours; send acknowledgment        |

### 7.3 After-Hours Response Template

> Thank you for reaching out. Our human support team is available Monday through Friday, 9:00 AM to 6:00 PM Eastern Time. Your request has been logged with reference number [TICKET-ID] and will be addressed as a priority when our team is back online. [For P1:] Given the urgency of your issue, I have also notified our on-call engineering team for immediate attention.
