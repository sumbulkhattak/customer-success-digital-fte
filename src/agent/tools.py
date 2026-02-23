"""Agent tools for the Customer Success Digital FTE.

Uses OpenAI Agents SDK @function_tool decorator for tool definitions.
Each tool has a Pydantic BaseModel for input validation.
"""

import json
import uuid
from typing import Optional
from pydantic import BaseModel, Field
import structlog

from src.database import queries
from src.agent.formatters import format_search_results, format_customer_history, format_for_channel
from src.kafka_client import TOPICS

logger = structlog.get_logger()


# --- Pydantic Input Models ---

class KnowledgeSearchInput(BaseModel):
    """Input for knowledge base search."""
    query: str = Field(description="Search query for the knowledge base")
    limit: int = Field(default=5, description="Maximum number of results to return", ge=1, le=20)


class TicketInput(BaseModel):
    """Input for ticket creation."""
    conversation_id: str = Field(description="UUID of the current conversation")
    customer_id: str = Field(description="UUID of the customer")
    channel: str = Field(description="Channel: email, whatsapp, or web_form")
    subject: str = Field(description="Brief description of the issue")
    category: Optional[str] = Field(default=None, description="Category: password_reset, feature_question, bug_report, billing, feedback, integration, api_help")
    priority: str = Field(default="medium", description="Priority: low, medium, high, urgent")


class EscalationInput(BaseModel):
    """Input for escalation to human agent."""
    conversation_id: str = Field(description="UUID of the conversation to escalate")
    customer_id: str = Field(description="UUID of the customer")
    reason: str = Field(description="Reason for escalation")
    severity: str = Field(default="P3", description="Severity: P1, P2, P3, P4")
    channel: str = Field(description="Original channel")
    context_summary: str = Field(default="", description="Summary of conversation so far")


class ResponseInput(BaseModel):
    """Input for sending a response."""
    conversation_id: str = Field(description="UUID of the conversation")
    customer_id: str = Field(description="UUID of the customer")
    channel: str = Field(description="Channel to respond on: email, whatsapp, web_form")
    response: str = Field(description="The response message content")
    customer_name: str = Field(default="Customer", description="Customer's name for formatting")
    ticket_number: str = Field(default="", description="Ticket reference number")


# --- Tool Functions ---
# These are plain async functions. The OpenAI Agents SDK @function_tool
# decorator will be applied when building the agent. This keeps tools
# testable without the SDK.

async def search_knowledge_base(query: str, limit: int = 5) -> str:
    """Search the product knowledge base for relevant documentation.

    Use this tool to find answers to customer questions about TechCorp Platform
    features, troubleshooting steps, account management, and integrations.
    """
    try:
        results = await queries.search_knowledge_base(query, limit)
        if not results:
            logger.warning("Knowledge base search returned no results", query=query)
            return "No relevant documentation found for this query. Consider escalating if this is the second failed search."

        formatted = format_search_results(results)
        logger.info("Knowledge base searched", query=query, results_count=len(results))
        return formatted
    except Exception as e:
        logger.error("Knowledge base search failed", query=query, error=str(e))
        return f"Error searching knowledge base: {str(e)}. Please try a different search query."


async def create_ticket(
    conversation_id: str,
    customer_id: str,
    channel: str,
    subject: str,
    category: str = None,
    priority: str = "medium"
) -> str:
    """Create a support ticket for the current interaction.

    MUST be called before sending any response to the customer.
    This tracks the interaction and provides a ticket reference number.
    """
    try:
        ticket = await queries.create_ticket(
            conversation_id=uuid.UUID(conversation_id),
            customer_id=uuid.UUID(customer_id),
            channel=channel,
            subject=subject,
            category=category,
            priority=priority,
        )
        ticket_number = ticket["ticket_number"]
        logger.info("Ticket created", ticket_number=ticket_number, channel=channel, category=category)
        return json.dumps({
            "status": "created",
            "ticket_number": ticket_number,
            "ticket_id": str(ticket["id"]),
            "priority": priority,
        })
    except Exception as e:
        logger.error("Ticket creation failed", error=str(e))
        return json.dumps({"status": "error", "message": f"Failed to create ticket: {str(e)}"})


async def get_customer_history(customer_id: str, limit: int = 10) -> str:
    """Look up a customer's previous interactions across all channels.

    Use this to understand the customer's history with TechCorp, including
    previous issues, channels used, and any ongoing conversations.
    """
    try:
        history = await queries.get_customer_history(uuid.UUID(customer_id), limit)
        formatted = format_customer_history(history)
        logger.info("Customer history retrieved", customer_id=customer_id, entries=len(history))
        return formatted
    except Exception as e:
        logger.error("Customer history lookup failed", customer_id=customer_id, error=str(e))
        return f"Error retrieving customer history: {str(e)}"


async def escalate_to_human(
    conversation_id: str,
    customer_id: str,
    reason: str,
    severity: str = "P3",
    channel: str = "email",
    context_summary: str = ""
) -> str:
    """Escalate the conversation to a human support agent.

    Use this when:
    - Customer requests a human agent
    - Legal language is detected
    - Customer is very upset (sentiment < 0.3)
    - You cannot find an answer after 2+ searches
    - Pricing, refund, or billing change requests
    - Security or data concerns
    """
    try:
        from src.kafka_client import get_event_bus

        escalation_event = {
            "conversation_id": conversation_id,
            "customer_id": customer_id,
            "reason": reason,
            "severity": severity,
            "channel": channel,
            "context_summary": context_summary,
            "status": "pending",
        }

        event_bus = get_event_bus()
        await event_bus.publish(TOPICS["escalations"], escalation_event, key=conversation_id)

        logger.info("Escalation created", reason=reason, severity=severity, channel=channel)

        # Record escalation metric
        await queries.record_metric(channel, "escalation", 1.0, {"reason": reason, "severity": severity})

        return json.dumps({
            "status": "escalated",
            "severity": severity,
            "reason": reason,
            "message": "A human agent will follow up shortly. The customer has been notified.",
        })
    except Exception as e:
        logger.error("Escalation failed", error=str(e))
        return json.dumps({"status": "error", "message": f"Escalation failed: {str(e)}"})


async def send_response(
    conversation_id: str,
    customer_id: str,
    channel: str,
    response: str,
    customer_name: str = "Customer",
    ticket_number: str = ""
) -> str:
    """Send a formatted response to the customer via their channel.

    The response will be automatically formatted according to the channel:
    - Email: Formal with greeting and signature
    - WhatsApp: Concise and friendly
    - Web Form: Semi-formal with help center link
    """
    try:
        # Format response for channel
        formatted = format_for_channel(response, channel, customer_name, ticket_number)

        # Store the outbound message
        await queries.create_message(
            conversation_id=uuid.UUID(conversation_id),
            sender_type="agent",
            content=formatted,
            channel=channel,
            metadata={"ticket_number": ticket_number},
        )

        # Record response metric
        await queries.record_metric(channel, "response", 1.0, {
            "conversation_id": conversation_id,
            "response_length": len(formatted),
        })

        logger.info("Response sent", channel=channel, conversation_id=conversation_id, length=len(formatted))

        return json.dumps({
            "status": "sent",
            "channel": channel,
            "formatted_length": len(formatted),
            "message": "Response delivered successfully.",
        })
    except Exception as e:
        logger.error("Response delivery failed", channel=channel, error=str(e))
        return json.dumps({"status": "error", "message": f"Failed to send response: {str(e)}"})


# --- Tool Registry ---
# List of all tool functions for easy registration with the agent
TOOLS = [
    search_knowledge_base,
    create_ticket,
    get_customer_history,
    escalate_to_human,
    send_response,
]
