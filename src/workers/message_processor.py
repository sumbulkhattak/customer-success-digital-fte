"""Unified Message Processor - Kafka worker that processes messages from all channels."""

import json
import time
import asyncio
from typing import Optional
import structlog

from src.config import settings
from src.database import queries
from src.kafka_client import TOPICS, get_event_bus
from src.agent.customer_success_agent import get_agent
from src.channels.gmail_handler import get_gmail_handler
from src.channels.whatsapp_handler import get_whatsapp_handler

logger = structlog.get_logger()


class UnifiedMessageProcessor:
    """Processes incoming messages from all channels via Kafka.

    Consumes from fte.tickets.incoming and channel-specific topics,
    routes to the AI agent, and delivers responses.
    """

    def __init__(self):
        self._agent = get_agent()
        self._gmail_handler = get_gmail_handler()
        self._whatsapp_handler = get_whatsapp_handler()
        self._event_bus = get_event_bus()
        self._running = False

    async def start(self):
        """Start the message processor."""
        logger.info("Starting Unified Message Processor")
        self._running = True
        await self._event_bus.start()
        await self._gmail_handler.setup()
        await self._whatsapp_handler.setup()

        # Start consuming from the unified intake topic
        await self._event_bus.consume(self._handle_message)

    async def stop(self):
        """Stop the message processor."""
        self._running = False
        await self._event_bus.stop()
        logger.info("Unified Message Processor stopped")

    async def _handle_message(self, topic: str, message: dict):
        """Handle an incoming message from any channel.

        Only processes messages from the unified tickets_incoming topic
        to avoid duplicate processing (channel-specific topics are for
        future per-channel consumers).

        Args:
            topic: The Kafka topic the message came from
            message: The deserialized message data
        """
        # Only process from the unified intake topic to avoid duplicates
        if topic != TOPICS["tickets_incoming"]:
            return

        start_time = time.time()
        channel = message.get("channel", "unknown")

        logger.info(
            "Processing message",
            topic=topic,
            channel=channel,
            ticket_number=message.get("ticket_number", "N/A"),
        )

        try:
            # Step 1: Resolve customer identity
            customer = await self.resolve_customer(message)
            customer_id = str(customer["id"])
            customer_name = customer.get("name", "Customer")

            # Step 2: Get or create conversation
            conversation = await self.get_or_create_conversation(
                customer_id=customer["id"],
                channel=channel,
                subject=message.get("subject", "Support Request"),
            )
            conversation_id = str(conversation["id"])

            # Step 3: Store inbound message (if not already stored by channel handler)
            if topic == TOPICS["tickets_incoming"]:
                await queries.create_message(
                    conversation_id=conversation["id"],
                    sender_type="customer",
                    content=message.get("message", message.get("body", "")),
                    channel=channel,
                    metadata={"source": "kafka", "topic": topic},
                )

            # Step 4: Run the AI agent
            agent_result = await self._agent.run(
                message=message.get("message", message.get("body", "")),
                channel=channel,
                customer_name=customer_name,
                customer_id=customer_id,
                conversation_id=conversation_id,
            )

            # Step 5: Store agent response in database
            response_text = agent_result.get("response", "")
            if response_text:
                await queries.create_message(
                    conversation_id=conversation["id"],
                    sender_type="agent",
                    content=response_text,
                    channel=channel,
                    metadata={
                        "category": agent_result.get("category", ""),
                        "escalated": agent_result.get("escalated", False),
                        "ticket_number": message.get("ticket_number", ""),
                    },
                )

            # Step 6: Deliver response via channel
            if not agent_result.get("escalated", False) and response_text:
                await self._deliver_response(
                    channel=channel,
                    message_data=message,
                    response=response_text,
                )

            # Step 7: Record metrics
            processing_time = time.time() - start_time
            await queries.record_metric(
                channel=channel,
                metric_type="response_time",
                metric_value=processing_time,
                metadata={
                    "ticket_number": message.get("ticket_number", ""),
                    "escalated": agent_result.get("escalated", False),
                    "category": agent_result.get("category", ""),
                },
            )

            logger.info(
                "Message processed",
                channel=channel,
                processing_time=f"{processing_time:.2f}s",
                escalated=agent_result.get("escalated", False),
            )

        except Exception as e:
            logger.error("Message processing failed", channel=channel, error=str(e))
            await self._handle_error(message, channel, str(e))

    async def resolve_customer(self, message: dict) -> dict:
        """Resolve customer identity across channels.

        Tries to find existing customer by email or phone,
        creates new customer if not found.
        """
        channel = message.get("channel", "")
        customer = None

        # Try email lookup
        email = message.get("customer_email", message.get("from_email", ""))
        if email:
            customer = await queries.find_customer_by_email(email)

        # Try phone lookup (for WhatsApp)
        if not customer:
            phone = message.get("from_number", message.get("customer_phone", ""))
            if phone:
                customer = await queries.find_customer_by_phone(phone)

        # Create new customer if not found
        if not customer:
            name = message.get("customer_name", message.get("from_name", "Customer"))
            email = message.get("customer_email", message.get("from_email"))
            phone = message.get("from_number", message.get("customer_phone"))

            customer = await queries.create_customer(
                name=name,
                email=email,
                phone=phone,
            )
            logger.info("New customer created", customer_id=str(customer["id"]), channel=channel)

        return customer

    async def get_or_create_conversation(
        self, customer_id, channel: str, subject: str = "Support Request"
    ) -> dict:
        """Get active conversation or create a new one."""
        conversation = await queries.get_active_conversation(customer_id, channel)
        if not conversation:
            conversation = await queries.create_conversation(
                customer_id=customer_id,
                channel=channel,
                subject=subject,
            )
        return conversation

    async def _deliver_response(self, channel: str, message_data: dict, response: str):
        """Deliver the agent's response via the appropriate channel."""
        try:
            if channel == "email":
                thread_id = message_data.get("thread_id", "")
                to_email = message_data.get("from_email", message_data.get("customer_email", ""))
                subject = message_data.get("subject", "Support Response")
                if to_email:
                    await self._gmail_handler.send_reply(thread_id, to_email, subject, response)

            elif channel == "whatsapp":
                to_number = message_data.get("from_number", message_data.get("customer_phone", ""))
                if to_number:
                    await self._whatsapp_handler.send_message(to_number, response)

            elif channel == "web_form":
                # Web form: send email notification to customer if email available
                to_email = message_data.get("customer_email", "")
                subject = message_data.get("subject", "Support Response")
                if to_email:
                    await self._gmail_handler.send_reply(
                        thread_id="",
                        to_email=to_email,
                        subject=subject,
                        body=response,
                    )
                    logger.info("Web form email response sent", to_email=to_email)
                else:
                    logger.info("Web form response stored (no email to send to)")

            logger.info("Response delivered", channel=channel)
        except Exception as e:
            logger.error("Response delivery failed", channel=channel, error=str(e))

    async def _handle_error(self, message: dict, channel: str, error: str):
        """Handle processing errors with an apology response."""
        try:
            # Publish to dead letter queue
            dlq_event = {
                "original_message": message,
                "channel": channel,
                "error": error,
            }
            await self._event_bus.publish(TOPICS["dlq"], dlq_event)

            # Send apology response
            apology = (
                "We apologize for the inconvenience. We encountered an issue processing "
                "your request. A team member has been notified and will follow up with you shortly."
            )
            await self._deliver_response(channel, message, apology)

            # Record error metric
            await queries.record_metric(
                channel=channel,
                metric_type="error",
                metric_value=1.0,
                metadata={"error": error},
            )
        except Exception as e:
            logger.error("Error handler failed", error=str(e))


async def run_processor():
    """Entry point for running the message processor."""
    processor = UnifiedMessageProcessor()
    try:
        await processor.start()
        # Keep running until interrupted
        while True:
            await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutting down message processor")
    finally:
        await processor.stop()


if __name__ == "__main__":
    asyncio.run(run_processor())
