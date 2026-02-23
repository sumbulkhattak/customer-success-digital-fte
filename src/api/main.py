"""FastAPI application - main entry point for the Customer Success Digital FTE."""

import asyncio
import json
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog

from src.config import settings
from src.database.connection import init_db, close_db, get_db_pool
from src.database import queries
from src.kafka_client import TOPICS, get_event_bus
from src.channels.web_form_handler import router as web_form_router
from src.channels.gmail_handler import get_gmail_handler
from src.channels.whatsapp_handler import get_whatsapp_handler
from src.workers.message_processor import UnifiedMessageProcessor

logger = structlog.get_logger()

# Global references
_processor: Optional[UnifiedMessageProcessor] = None
_gmail_handler = None
_whatsapp_handler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown."""
    global _processor, _gmail_handler, _whatsapp_handler

    # Startup
    logger.info("Starting Customer Success Digital FTE", environment=settings.ENVIRONMENT)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Initialize channel handlers
    _gmail_handler = get_gmail_handler()
    await _gmail_handler.setup()
    _whatsapp_handler = get_whatsapp_handler()
    await _whatsapp_handler.setup()

    # Initialize event bus
    event_bus = get_event_bus()
    await event_bus.start()

    # Start message processor in background
    _processor = UnifiedMessageProcessor()
    asyncio.create_task(_start_processor(_processor))

    logger.info("All systems initialized", mock_mode=settings.USE_MOCK_OPENAI)

    yield

    # Shutdown
    logger.info("Shutting down Customer Success Digital FTE")
    if _processor:
        await _processor.stop()
    await event_bus.stop()
    await close_db()
    logger.info("Shutdown complete")


async def _start_processor(processor: UnifiedMessageProcessor):
    """Start the message processor (runs in background task)."""
    try:
        await processor.start()
    except Exception as e:
        logger.error("Message processor failed", error=str(e))


# Create FastAPI app
app = FastAPI(
    title="Customer Success Digital FTE",
    description="24/7 AI Customer Support Agent - Email, WhatsApp, Web Form",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include web form router
app.include_router(web_form_router)


# --- Health Check ---

@app.get("/health")
async def health_check():
    """Health check with system status."""
    db_status = "unknown"
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "service": "customer-success-fte",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": db_status,
            "mock_mode": {
                "openai": settings.USE_MOCK_OPENAI,
                "gmail": settings.USE_MOCK_GMAIL,
                "twilio": settings.USE_MOCK_TWILIO,
            },
        },
        "channels": {
            "email": "active",
            "whatsapp": "active",
            "web_form": "active",
        },
    }


# --- Gmail Webhook ---

@app.post("/webhooks/gmail")
async def gmail_webhook(request: Request):
    """Handle Gmail Pub/Sub push notifications."""
    try:
        body = await request.json()
        logger.info("Gmail webhook received")

        # Process the notification
        messages = await _gmail_handler.process_notification(body)

        if messages:
            event_bus = get_event_bus()
            for msg in messages:
                # Publish to Kafka for processing
                event = {
                    "channel": "email",
                    "message_id": msg.get("message_id", ""),
                    "thread_id": msg.get("thread_id", ""),
                    "from_email": msg.get("from_email", ""),
                    "from_name": msg.get("from_name", "Customer"),
                    "customer_email": msg.get("from_email", ""),
                    "customer_name": msg.get("from_name", "Customer"),
                    "subject": msg.get("subject", ""),
                    "message": msg.get("body", ""),
                    "timestamp": datetime.utcnow().isoformat(),
                }
                await event_bus.publish(TOPICS["email_inbound"], event, key=msg.get("thread_id", ""))
                await event_bus.publish(TOPICS["tickets_incoming"], event, key=msg.get("thread_id", ""))

            logger.info("Gmail messages published", count=len(messages))

        return {"status": "ok"}
    except Exception as e:
        logger.error("Gmail webhook error", error=str(e))
        return {"status": "error", "message": str(e)}


# --- WhatsApp Webhook ---

@app.post("/webhooks/whatsapp")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages via Twilio webhook."""
    try:
        form_data = await request.form()
        form_dict = dict(form_data)

        # Validate webhook signature (skip in mock mode)
        if not settings.USE_MOCK_TWILIO:
            signature = request.headers.get("X-Twilio-Signature", "")
            # Use forwarded URL (ngrok/proxy) or API_BASE_URL for signature validation
            forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
            forwarded_host = request.headers.get("X-Forwarded-Host", "") or request.headers.get("Host", "")
            if forwarded_proto and forwarded_host:
                url = f"{forwarded_proto}://{forwarded_host}{request.url.path}"
            elif settings.API_BASE_URL != "http://localhost:8000":
                url = f"{settings.API_BASE_URL}{request.url.path}"
            else:
                url = str(request.url)
            if not _whatsapp_handler.validate_webhook(url, form_dict, signature):
                raise HTTPException(status_code=403, detail="Invalid webhook signature")

        # Process the webhook
        message_data = await _whatsapp_handler.process_webhook(form_dict)

        if message_data:
            event_bus = get_event_bus()
            event = {
                "channel": "whatsapp",
                "message_sid": message_data.get("message_sid", ""),
                "from_number": message_data.get("from_number", ""),
                "from_name": message_data.get("from_name", "Customer"),
                "customer_name": message_data.get("from_name", "Customer"),
                "customer_phone": message_data.get("from_number", ""),
                "message": message_data.get("body", ""),
                "subject": f"WhatsApp: {message_data.get('body', '')[:50]}",
                "num_media": message_data.get("num_media", 0),
                "timestamp": datetime.utcnow().isoformat(),
            }
            await event_bus.publish(TOPICS["whatsapp_inbound"], event, key=message_data.get("from_number", ""))
            await event_bus.publish(TOPICS["tickets_incoming"], event, key=message_data.get("from_number", ""))

            logger.info("WhatsApp message published", from_number=message_data.get("from_number", ""))

        # Twilio expects empty TwiML response
        return "<Response></Response>"
    except HTTPException:
        raise
    except Exception as e:
        logger.error("WhatsApp webhook error", error=str(e))
        return "<Response></Response>"


@app.post("/webhooks/whatsapp/status")
async def whatsapp_status_webhook(request: Request):
    """Handle WhatsApp message delivery status callbacks."""
    try:
        form_data = await request.form()
        message_sid = form_data.get("MessageSid", "")
        status = form_data.get("MessageStatus", "")

        logger.info("WhatsApp status update", message_sid=message_sid, status=status)

        # Record delivery metric
        if status in ("delivered", "read"):
            await queries.record_metric(
                channel="whatsapp",
                metric_type="delivery",
                metric_value=1.0,
                metadata={"message_sid": message_sid, "status": status},
            )

        return {"status": "ok"}
    except Exception as e:
        logger.error("WhatsApp status webhook error", error=str(e))
        return {"status": "ok"}


# --- Conversation & Customer APIs ---

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    try:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            # Get conversation
            conv = await conn.fetchrow(
                "SELECT * FROM conversations WHERE id = $1",
                uuid.UUID(conversation_id)
            )
            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")

            # Get messages
            messages = await conn.fetch(
                """SELECT id, sender_type, content, channel, delivery_status, created_at
                   FROM messages WHERE conversation_id = $1 ORDER BY created_at""",
                uuid.UUID(conversation_id)
            )

        return {
            "conversation": {
                "id": str(conv["id"]),
                "customer_id": str(conv["customer_id"]),
                "channel": conv["channel"],
                "status": conv["status"],
                "subject": conv["subject"],
                "started_at": conv["started_at"].isoformat(),
            },
            "messages": [
                {
                    "id": str(m["id"]),
                    "sender_type": m["sender_type"],
                    "content": m["content"],
                    "channel": m["channel"],
                    "delivery_status": m["delivery_status"],
                    "created_at": m["created_at"].isoformat(),
                }
                for m in messages
            ],
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get conversation", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@app.get("/customers/lookup")
async def customer_lookup(email: Optional[str] = None, phone: Optional[str] = None):
    """Look up a customer by email or phone."""
    if not email and not phone:
        raise HTTPException(status_code=400, detail="Provide email or phone parameter")

    customer = None
    if email:
        customer = await queries.find_customer_by_email(email)
    if not customer and phone:
        customer = await queries.find_customer_by_phone(phone)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    return {
        "id": str(customer["id"]),
        "name": customer["name"],
        "email": customer.get("email"),
        "phone": customer.get("phone"),
        "created_at": customer["created_at"].isoformat() if hasattr(customer["created_at"], "isoformat") else str(customer["created_at"]),
    }


# --- Metrics ---

@app.get("/metrics/channels")
async def channel_metrics(channel: Optional[str] = None, hours: int = 24):
    """Get per-channel performance metrics."""
    metrics = await queries.get_channel_metrics(channel, hours)
    return {
        "period_hours": hours,
        "channel_filter": channel,
        "metrics": [
            {
                "channel": m["channel"],
                "metric_type": m["metric_type"],
                "avg_value": float(m["avg_value"]),
                "count": m["count"],
            }
            for m in metrics
        ],
    }


# --- Entry Point ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
    )
