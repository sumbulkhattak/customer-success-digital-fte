"""Customer Success Agent using OpenAI Agents SDK with mock fallback."""

import json
import uuid
from typing import Optional
import structlog

from src.config import settings
from src.agent.prompts import get_system_prompt
from src.agent.tools import (
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
    TOOLS,
)

logger = structlog.get_logger()


class MockAgent:
    """Mock agent for development without OpenAI API key.

    Uses keyword matching against the knowledge base to generate responses.
    Follows the same workflow as the real agent: ticket -> history -> search -> respond.
    """

    ESCALATION_KEYWORDS = [
        "lawsuit", "attorney", "legal action", "liability", "lawyer",
        "refund", "money back", "pricing", "cost", "price",
        "human", "agent", "representative", "real person",
    ]

    PROFANITY_INDICATORS = [
        "terrible", "worst", "hate", "stupid", "useless", "garbage", "trash",
    ]

    CATEGORY_KEYWORDS = {
        "password_reset": ["password", "reset", "login", "can't log in", "locked out", "forgot"],
        "billing": ["bill", "invoice", "charge", "payment", "subscription", "plan", "upgrade", "downgrade"],
        "bug_report": ["bug", "error", "broken", "not working", "crash", "issue", "glitch"],
        "feature_question": ["how to", "how do", "can i", "feature", "where is", "setting"],
        "integration": ["slack", "github", "jira", "zapier", "integrate", "integration", "connect"],
        "api_help": ["api", "endpoint", "webhook", "token", "rate limit", "authentication"],
        "feedback": ["suggestion", "feedback", "improve", "wish", "would be nice"],
    }

    async def run(
        self,
        message: str,
        channel: str,
        customer_name: str = "Customer",
        customer_id: str = None,
        conversation_id: str = None,
    ) -> dict:
        """Process a customer message and return a response."""
        logger.info(
            "MockAgent processing message",
            channel=channel,
            message_length=len(message),
        )

        # Generate IDs if not provided
        if not customer_id:
            customer_id = str(uuid.uuid4())
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        # Check for escalation triggers
        message_lower = message.lower()

        # Check profanity/anger
        anger_score = sum(1 for word in self.PROFANITY_INDICATORS if word in message_lower)
        if anger_score >= 2:
            return await self._handle_escalation(
                conversation_id, customer_id, channel, customer_name,
                message, "Aggressive/upset customer detected", "P2"
            )

        # Check escalation keywords
        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in message_lower:
                reason = f"Escalation keyword detected: '{keyword}'"
                severity = "P2" if keyword in ("lawsuit", "attorney", "legal action", "liability", "lawyer") else "P3"
                return await self._handle_escalation(
                    conversation_id, customer_id, channel, customer_name,
                    message, reason, severity
                )

        # Detect category
        category = self._detect_category(message_lower)

        # Step 1: Create ticket
        ticket_result = await create_ticket(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            subject=message[:100],
            category=category,
            priority=self._detect_priority(message_lower),
        )
        ticket_data = json.loads(ticket_result)
        ticket_number = ticket_data.get("ticket_number", "N/A")

        # Step 2: Get customer history
        history = await get_customer_history(customer_id)

        # Step 3: Search knowledge base
        kb_results = await search_knowledge_base(message, limit=3)

        # Step 4: Generate response based on KB results
        if "No relevant documentation found" in kb_results:
            response_text = (
                "I've searched our documentation but couldn't find a specific answer to your question. "
                "I've created a ticket for our team to look into this further. "
                "A team member will follow up with you shortly."
            )
        else:
            # Extract key info from KB results for the response
            response_text = self._generate_response(message, kb_results, category)

        # Step 5: Send response
        await send_response(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            response=response_text,
            customer_name=customer_name,
            ticket_number=ticket_number,
        )

        return {
            "status": "completed",
            "ticket_number": ticket_number,
            "category": category,
            "escalated": False,
            "response": response_text,
            "channel": channel,
        }

    async def _handle_escalation(
        self, conversation_id, customer_id, channel, customer_name, message, reason, severity
    ) -> dict:
        """Handle escalation flow."""
        # Create ticket first
        ticket_result = await create_ticket(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            subject=f"[ESCALATION] {message[:80]}",
            category="escalation",
            priority="high",
        )
        ticket_data = json.loads(ticket_result)
        ticket_number = ticket_data.get("ticket_number", "N/A")

        # Escalate
        await escalate_to_human(
            conversation_id=conversation_id,
            customer_id=customer_id,
            reason=reason,
            severity=severity,
            channel=channel,
            context_summary=message[:500],
        )

        # Send acknowledgment
        escalation_response = (
            "I understand your concern and I want to make sure you get the best help possible. "
            "I've escalated your request to our specialized team. "
            "A human agent will be in touch with you shortly."
        )
        await send_response(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            response=escalation_response,
            customer_name=customer_name,
            ticket_number=ticket_number,
        )

        return {
            "status": "escalated",
            "ticket_number": ticket_number,
            "reason": reason,
            "severity": severity,
            "escalated": True,
            "response": escalation_response,
            "channel": channel,
        }

    def _detect_category(self, message_lower: str) -> str:
        """Detect ticket category from message content."""
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return "feature_question"  # default

    def _detect_priority(self, message_lower: str) -> str:
        """Detect priority from message urgency indicators."""
        urgent_words = ["urgent", "asap", "immediately", "emergency", "critical", "down", "blocked"]
        high_words = ["important", "soon", "quickly", "broken"]

        if any(w in message_lower for w in urgent_words):
            return "urgent"
        if any(w in message_lower for w in high_words):
            return "high"
        return "medium"

    def _generate_response(self, message: str, kb_results: str, category: str) -> str:
        """Generate a helpful response based on KB search results."""
        # Default responses by category
        category_responses = {
            "password_reset": (
                "To reset your password, please follow these steps:\n"
                "1. Go to the TechCorp login page\n"
                "2. Click 'Forgot Password'\n"
                "3. Enter your registered email address\n"
                "4. Check your email for the reset link (check spam folder too)\n"
                "5. Click the link and set a new password\n\n"
                "If you're still having trouble, our team can help reset it manually."
            ),
            "billing": (
                "I can see you have a billing-related question. For your security, "
                "billing changes need to be handled by our accounts team. "
                "I've flagged your request and someone will assist you shortly."
            ),
            "bug_report": (
                "Thank you for reporting this issue. I've logged it for our engineering team. "
                "In the meantime, you might try:\n"
                "1. Clearing your browser cache and cookies\n"
                "2. Trying a different browser\n"
                "3. Disabling browser extensions\n\n"
                "Our team will investigate and follow up with you."
            ),
            "integration": (
                "I found some information about integrations in our docs. "
                "For integration setup and troubleshooting, please visit our "
                "Integration Guide in the Help Center. If you need specific help, "
                "our team will follow up with detailed instructions."
            ),
            "api_help": (
                "For API-related questions, I recommend checking our API documentation "
                "at https://api.techcorp.com/docs. Common topics include authentication, "
                "rate limits, and webhook configuration. "
                "If you need further assistance, our developer support team can help."
            ),
            "feedback": (
                "Thank you for your feedback! We really appreciate hearing from our users. "
                "I've logged your suggestion for our product team to review. "
                "Your input helps us make TechCorp better for everyone."
            ),
        }

        response = category_responses.get(
            category,
            "Thank you for reaching out. I've reviewed our documentation and "
            "created a ticket for your request. Our team will look into this "
            "and get back to you with a detailed answer."
        )
        return response


class SmartAgent:
    """Hybrid agent: code-driven workflow + LLM-generated responses.

    Uses the same workflow as MockAgent (ticket creation, KB search, etc.)
    but sends context to the Groq/OpenAI LLM to generate natural,
    context-aware responses instead of using templates.

    Supports multiple AI providers via OpenAI-compatible API:
    - OpenAI (default): gpt-4o
    - Groq (free): llama-3.3-70b-versatile
    - Google Gemini (free): gemini-2.0-flash
    """

    ESCALATION_KEYWORDS = MockAgent.ESCALATION_KEYWORDS
    PROFANITY_INDICATORS = MockAgent.PROFANITY_INDICATORS
    CATEGORY_KEYWORDS = MockAgent.CATEGORY_KEYWORDS

    def __init__(self):
        """Initialize the LLM client for the configured AI provider."""
        from openai import AsyncOpenAI

        base_url = settings.effective_base_url
        self._model = settings.effective_model

        client_kwargs = {"api_key": settings.OPENAI_API_KEY}
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = AsyncOpenAI(**client_kwargs)
        logger.info(
            "SmartAgent initialized",
            provider=settings.AI_PROVIDER,
            model=self._model,
            base_url=base_url or "default",
        )

    async def run(
        self,
        message: str,
        channel: str,
        customer_name: str = "Customer",
        customer_id: str = None,
        conversation_id: str = None,
    ) -> dict:
        """Process a customer message with code-driven workflow + LLM response."""
        logger.info(
            "SmartAgent processing message",
            channel=channel,
            message_length=len(message),
        )

        if not customer_id:
            customer_id = str(uuid.uuid4())
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        message_lower = message.lower()

        # Check for escalation triggers
        anger_score = sum(1 for word in self.PROFANITY_INDICATORS if word in message_lower)
        if anger_score >= 2:
            return await self._handle_escalation(
                conversation_id, customer_id, channel, customer_name,
                message, "Aggressive/upset customer detected", "P2"
            )

        for keyword in self.ESCALATION_KEYWORDS:
            if keyword in message_lower:
                reason = f"Escalation keyword detected: '{keyword}'"
                severity = "P2" if keyword in ("lawsuit", "attorney", "legal action", "liability", "lawyer") else "P3"
                return await self._handle_escalation(
                    conversation_id, customer_id, channel, customer_name,
                    message, reason, severity
                )

        # Detect category and priority
        category = self._detect_category(message_lower)
        priority = self._detect_priority(message_lower)

        # Step 1: Create ticket
        ticket_result = await create_ticket(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            subject=message[:100],
            category=category,
            priority=priority,
        )
        ticket_data = json.loads(ticket_result)
        ticket_number = ticket_data.get("ticket_number", "N/A")

        # Step 2: Get customer history
        history = await get_customer_history(customer_id)

        # Step 3: Search knowledge base
        kb_results = await search_knowledge_base(message, limit=3)

        # Step 4: Generate AI response using LLM
        response_text = await self._generate_ai_response(
            message=message,
            channel=channel,
            customer_name=customer_name,
            ticket_number=ticket_number,
            kb_results=kb_results,
            history=history,
            category=category,
        )

        # Step 5: Send response
        await send_response(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            response=response_text,
            customer_name=customer_name,
            ticket_number=ticket_number,
        )

        return {
            "status": "completed",
            "ticket_number": ticket_number,
            "category": category,
            "escalated": False,
            "response": response_text,
            "channel": channel,
        }

    async def _generate_ai_response(
        self,
        message: str,
        channel: str,
        customer_name: str,
        ticket_number: str,
        kb_results: str,
        history: str,
        category: str,
    ) -> str:
        """Call the LLM to generate a natural, context-aware response."""
        system_prompt = get_system_prompt(channel, customer_name, "")

        user_prompt = (
            f"Customer message: {message}\n\n"
            f"Ticket number: {ticket_number}\n"
            f"Category: {category}\n\n"
            f"Knowledge base results:\n{kb_results}\n\n"
            f"Customer history:\n{history}\n\n"
            f"Generate a helpful, empathetic response for the customer. "
            f"Include the ticket number {ticket_number} in your response. "
            f"Base your answer on the knowledge base results above."
        )

        try:
            completion = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=600,
                temperature=0.7,
            )
            response = completion.choices[0].message.content
            logger.info("LLM response generated", model=self._model, tokens=completion.usage.total_tokens)
            return response
        except Exception as e:
            logger.error("LLM response generation failed", error=str(e))
            # Fall back to template response
            return self._fallback_response(message, kb_results, category, ticket_number, customer_name)

    def _fallback_response(self, message, kb_results, category, ticket_number, customer_name):
        """Template fallback if LLM call fails."""
        return (
            f"Hi {customer_name},\n\n"
            f"Thank you for reaching out. I've created ticket {ticket_number} for your request.\n\n"
            f"I've reviewed our documentation and our team will follow up with a detailed answer shortly.\n\n"
            f"Best regards,\nTechCorp Support Team"
        )

    async def _handle_escalation(
        self, conversation_id, customer_id, channel, customer_name, message, reason, severity
    ) -> dict:
        """Handle escalation flow."""
        ticket_result = await create_ticket(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            subject=f"[ESCALATION] {message[:80]}",
            category="escalation",
            priority="high",
        )
        ticket_data = json.loads(ticket_result)
        ticket_number = ticket_data.get("ticket_number", "N/A")

        await escalate_to_human(
            conversation_id=conversation_id,
            customer_id=customer_id,
            reason=reason,
            severity=severity,
            channel=channel,
            context_summary=message[:500],
        )

        escalation_response = (
            "I understand your concern and I want to make sure you get the best help possible. "
            "I've escalated your request to our specialized team. "
            "A human agent will be in touch with you shortly."
        )
        await send_response(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel=channel,
            response=escalation_response,
            customer_name=customer_name,
            ticket_number=ticket_number,
        )

        return {
            "status": "escalated",
            "ticket_number": ticket_number,
            "reason": reason,
            "severity": severity,
            "escalated": True,
            "response": escalation_response,
            "channel": channel,
        }

    def _detect_category(self, message_lower: str) -> str:
        """Detect ticket category from message content."""
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[category] = score
        return max(scores, key=scores.get) if scores else "feature_question"

    def _detect_priority(self, message_lower: str) -> str:
        """Detect priority from message urgency indicators."""
        urgent_words = ["urgent", "asap", "immediately", "emergency", "critical", "down", "blocked"]
        high_words = ["important", "soon", "quickly", "broken"]
        if any(w in message_lower for w in urgent_words):
            return "urgent"
        if any(w in message_lower for w in high_words):
            return "high"
        return "medium"


def get_agent():
    """Factory function: returns SmartAgent (LLM) or MockAgent (template) based on config.

    Supports free providers:
    - Set AI_PROVIDER=groq + OPENAI_API_KEY=<groq-key> for free Groq
    - Set AI_PROVIDER=gemini + OPENAI_API_KEY=<gemini-key> for free Gemini
    - Set OPENAI_API_KEY=<openai-key> for OpenAI (paid)
    - Leave OPENAI_API_KEY empty for MockAgent (no API needed)
    """
    if settings.USE_MOCK_OPENAI:
        logger.info("Using MockAgent (no API key configured)")
        return MockAgent()
    else:
        logger.info(
            "Using SmartAgent",
            provider=settings.AI_PROVIDER,
            model=settings.effective_model,
        )
        return SmartAgent()
