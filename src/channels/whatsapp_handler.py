"""WhatsApp channel handler via Twilio with mock implementation."""

import hashlib
import hmac
from typing import Optional
from urllib.parse import urlencode
import structlog

from src.config import settings

logger = structlog.get_logger()


class WhatsAppHandler:
    """WhatsApp handler via Twilio API."""

    def __init__(self):
        """Initialize Twilio client."""
        self._client = None

    async def setup(self):
        """Set up Twilio client."""
        try:
            from twilio.rest import Client
            self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            logger.info("Twilio WhatsApp client initialized")
        except Exception as e:
            logger.error("Twilio setup failed", error=str(e))
            raise

    def validate_webhook(self, url: str, params: dict, signature: str) -> bool:
        """Validate Twilio webhook signature.

        Args:
            url: The full webhook URL
            params: The POST parameters from Twilio
            signature: The X-Twilio-Signature header value
        """
        try:
            from twilio.request_validator import RequestValidator
            validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
            return validator.validate(url, params, signature)
        except Exception as e:
            logger.error("Webhook validation failed", error=str(e))
            return False

    async def process_webhook(self, form_data: dict) -> Optional[dict]:
        """Process incoming WhatsApp message from Twilio webhook.

        Args:
            form_data: The POST form data from Twilio webhook

        Returns:
            Parsed message data or None
        """
        try:
            from_number = form_data.get("From", "").replace("whatsapp:", "")
            body = form_data.get("Body", "")
            message_sid = form_data.get("MessageSid", "")
            profile_name = form_data.get("ProfileName", "Customer")
            num_media = int(form_data.get("NumMedia", "0"))

            if not body and num_media == 0:
                logger.warning("Empty WhatsApp message received", from_number=from_number)
                return None

            message_data = {
                "message_sid": message_sid,
                "from_number": from_number,
                "from_name": profile_name,
                "body": body,
                "num_media": num_media,
                "media_urls": [],
            }

            # Extract media URLs if present
            for i in range(num_media):
                media_url = form_data.get(f"MediaUrl{i}", "")
                media_type = form_data.get(f"MediaContentType{i}", "")
                if media_url:
                    message_data["media_urls"].append({
                        "url": media_url,
                        "content_type": media_type,
                    })

            logger.info(
                "WhatsApp message received",
                from_number=from_number,
                body_length=len(body),
                media_count=num_media,
            )
            return message_data
        except Exception as e:
            logger.error("Failed to process WhatsApp webhook", error=str(e))
            return None

    async def send_message(self, to_number: str, body: str) -> dict:
        """Send a WhatsApp message via Twilio.

        Args:
            to_number: Recipient phone number (without whatsapp: prefix)
            body: Message text
        """
        if not self._client:
            await self.setup()

        try:
            # Split long messages (WhatsApp best practice: 300 chars)
            messages_to_send = self.format_response(body)

            results = []
            for msg_text in messages_to_send:
                message = self._client.messages.create(
                    from_=settings.TWILIO_WHATSAPP_NUMBER,
                    to=f"whatsapp:{to_number}",
                    body=msg_text,
                )
                results.append({
                    "sid": message.sid,
                    "status": message.status,
                })
                logger.info("WhatsApp message sent", to=to_number, sid=message.sid)

            return {
                "status": "sent",
                "messages": results,
                "parts": len(results),
            }
        except Exception as e:
            logger.error("Failed to send WhatsApp message", to=to_number, error=str(e))
            return {"status": "error", "error": str(e)}

    def format_response(self, body: str, max_length: int = 300) -> list[str]:
        """Split long messages into WhatsApp-friendly chunks.

        Args:
            body: Full message text
            max_length: Maximum characters per message

        Returns:
            List of message parts
        """
        if len(body) <= max_length:
            return [body]

        # Split at sentence boundaries where possible
        parts = []
        current = ""
        sentences = body.replace(". ", ".\n").split("\n")

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current) + len(sentence) + 1 <= max_length:
                current = f"{current} {sentence}".strip() if current else sentence
            else:
                if current:
                    parts.append(current)
                # If single sentence exceeds max, force split
                if len(sentence) > max_length:
                    while len(sentence) > max_length:
                        parts.append(sentence[:max_length])
                        sentence = sentence[max_length:]
                    if sentence:
                        current = sentence
                else:
                    current = sentence

        if current:
            parts.append(current)

        return parts if parts else [body[:max_length]]


class MockWhatsAppHandler:
    """Mock WhatsApp handler for development without Twilio credentials."""

    def __init__(self):
        self._sent_messages = []

    async def setup(self):
        """No-op setup for mock."""
        logger.info("MockWhatsAppHandler initialized (no Twilio API)")

    def validate_webhook(self, url: str, params: dict, signature: str) -> bool:
        """Mock validation - always returns True in development."""
        logger.info("Mock: WhatsApp webhook validation (always True)")
        return True

    async def process_webhook(self, form_data: dict) -> Optional[dict]:
        """Mock webhook processing - extracts data from form payload."""
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        body = form_data.get("Body", "")
        profile_name = form_data.get("ProfileName", "Customer")

        if not body:
            return None

        message_data = {
            "message_sid": f"mock-{__import__('uuid').uuid4().hex[:12]}",
            "from_number": from_number,
            "from_name": profile_name,
            "body": body,
            "num_media": 0,
            "media_urls": [],
        }

        logger.info("Mock: WhatsApp message received", from_number=from_number, body_length=len(body))
        return message_data

    async def send_message(self, to_number: str, body: str) -> dict:
        """Mock send - logs instead of sending via Twilio."""
        messages = self.format_response(body)

        results = []
        for msg_text in messages:
            mock_sid = f"mock-{__import__('uuid').uuid4().hex[:12]}"
            results.append({"sid": mock_sid, "status": "sent"})
            self._sent_messages.append({
                "to": to_number,
                "body": msg_text,
                "sid": mock_sid,
            })
            logger.info("Mock: WhatsApp message sent", to=to_number, body_length=len(msg_text))

        return {
            "status": "sent",
            "messages": results,
            "parts": len(results),
        }

    def format_response(self, body: str, max_length: int = 300) -> list[str]:
        """Split long messages into chunks (same logic as real handler)."""
        if len(body) <= max_length:
            return [body]

        parts = []
        current = ""
        sentences = body.replace(". ", ".\n").split("\n")

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(current) + len(sentence) + 1 <= max_length:
                current = f"{current} {sentence}".strip() if current else sentence
            else:
                if current:
                    parts.append(current)
                if len(sentence) > max_length:
                    while len(sentence) > max_length:
                        parts.append(sentence[:max_length])
                        sentence = sentence[max_length:]
                    if sentence:
                        current = sentence
                else:
                    current = sentence

        if current:
            parts.append(current)

        return parts if parts else [body[:max_length]]


def get_whatsapp_handler():
    """Factory: returns real or mock WhatsApp handler based on config."""
    if settings.USE_MOCK_TWILIO:
        logger.info("Using MockWhatsAppHandler")
        return MockWhatsAppHandler()
    else:
        logger.info("Using WhatsAppHandler with Twilio API")
        return WhatsAppHandler()
