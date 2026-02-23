"""Web form channel handler with FastAPI router."""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
import structlog

from src.database import queries
from src.kafka_client import TOPICS, get_event_bus

logger = structlog.get_logger()

router = APIRouter(prefix="/support", tags=["support"])


# --- Pydantic Models ---

class SupportFormSubmission(BaseModel):
    """Web form submission with validation."""

    name: str = Field(min_length=2, max_length=100, description="Customer name")
    email: str = Field(description="Customer email address")
    subject: str = Field(min_length=5, max_length=200, description="Issue subject")
    category: str = Field(description="Issue category")
    priority: str = Field(default="medium", description="Issue priority")
    message: str = Field(min_length=10, max_length=5000, description="Detailed message")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        """Basic email validation."""
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email address")
        return v.lower().strip()

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        """Validate category is one of the allowed values."""
        allowed = ["password_reset", "feature_question", "bug_report", "billing", "feedback", "integration", "api_help", "other"]
        if v not in allowed:
            raise ValueError(f"Category must be one of: {', '.join(allowed)}")
        return v

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v):
        """Validate priority level."""
        allowed = ["low", "medium", "high", "urgent"]
        if v not in allowed:
            raise ValueError(f"Priority must be one of: {', '.join(allowed)}")
        return v


class SupportFormResponse(BaseModel):
    """Response after form submission."""

    status: str
    ticket_number: str
    message: str
    estimated_response_time: str


class TicketStatusResponse(BaseModel):
    """Response for ticket status query."""

    ticket_number: str
    status: str
    subject: str
    category: Optional[str] = None
    priority: str
    channel: str
    created_at: str
    updated_at: str
    resolution: Optional[str] = None


# --- Endpoints ---

@router.post("/submit", response_model=SupportFormResponse)
async def submit_support_form(submission: SupportFormSubmission):
    """Handle web form support submission.

    1. Find or create customer
    2. Create conversation
    3. Store message
    4. Create ticket
    5. Publish to Kafka for processing
    """
    try:
        # Find or create customer
        customer = await queries.find_customer_by_email(submission.email)
        if not customer:
            customer = await queries.create_customer(
                name=submission.name,
                email=submission.email,
            )

        customer_id = customer["id"]

        # Create conversation
        conversation = await queries.create_conversation(
            customer_id=customer_id,
            channel="web_form",
            subject=submission.subject,
        )
        conversation_id = conversation["id"]

        # Store the inbound message
        await queries.create_message(
            conversation_id=conversation_id,
            sender_type="customer",
            content=submission.message,
            channel="web_form",
            metadata={
                "category": submission.category,
                "priority": submission.priority,
                "subject": submission.subject,
            },
        )

        # Create ticket
        ticket = await queries.create_ticket(
            conversation_id=conversation_id,
            customer_id=customer_id,
            channel="web_form",
            subject=submission.subject,
            category=submission.category,
            priority=submission.priority,
        )

        # Publish to Kafka for agent processing
        event = {
            "ticket_number": ticket["ticket_number"],
            "conversation_id": str(conversation_id),
            "customer_id": str(customer_id),
            "customer_name": submission.name,
            "customer_email": submission.email,
            "channel": "web_form",
            "subject": submission.subject,
            "category": submission.category,
            "priority": submission.priority,
            "message": submission.message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        event_bus = get_event_bus()
        await event_bus.publish(TOPICS["webform_inbound"], event, key=str(conversation_id))
        await event_bus.publish(TOPICS["tickets_incoming"], event, key=str(conversation_id))

        logger.info(
            "Web form submitted",
            ticket_number=ticket["ticket_number"],
            category=submission.category,
            priority=submission.priority,
        )

        # Determine estimated response time based on priority
        response_times = {
            "urgent": "1 hour",
            "high": "4 hours",
            "medium": "12 hours",
            "low": "24 hours",
        }

        return SupportFormResponse(
            status="submitted",
            ticket_number=ticket["ticket_number"],
            message="Your support request has been received. Our team will get back to you soon.",
            estimated_response_time=response_times.get(submission.priority, "24 hours"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Web form submission failed", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to process your request. Please try again.")


@router.get("/ticket/{ticket_id}", response_model=TicketStatusResponse)
async def get_ticket_status(ticket_id: str):
    """Get the current status of a support ticket."""
    try:
        ticket = await queries.get_ticket_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=404, detail=f"Ticket '{ticket_id}' not found")

        return TicketStatusResponse(
            ticket_number=ticket["ticket_number"],
            status=ticket["status"],
            subject=ticket["subject"],
            category=ticket.get("category"),
            priority=ticket["priority"],
            channel=ticket["channel"],
            created_at=ticket["created_at"].isoformat() if hasattr(ticket["created_at"], "isoformat") else str(ticket["created_at"]),
            updated_at=ticket["updated_at"].isoformat() if hasattr(ticket["updated_at"], "isoformat") else str(ticket["updated_at"]),
            resolution=ticket.get("resolution"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ticket status lookup failed", ticket_id=ticket_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket status")
