"""Gmail channel handler with mock implementation."""

import base64
import json
from email.mime.text import MIMEText
from typing import Optional
import structlog

from src.config import settings

logger = structlog.get_logger()


class GmailHandler:
    """Gmail API handler for email channel integration."""

    def __init__(self):
        """Initialize Gmail API client."""
        self._service = None
        self._setup_complete = False

    async def setup(self):
        """Set up Gmail API client with credentials."""
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_file(settings.GMAIL_CREDENTIALS_PATH)
            self._service = build("gmail", "v1", credentials=creds)
            self._setup_complete = True
            logger.info("Gmail API client initialized")
        except Exception as e:
            logger.error("Gmail setup failed", error=str(e))
            raise

    async def setup_push_notifications(self, topic_name: str = None):
        """Set up Gmail push notifications via Pub/Sub."""
        if not self._setup_complete:
            await self.setup()

        topic = topic_name or settings.GMAIL_PUBSUB_TOPIC
        request = {
            "labelIds": ["INBOX"],
            "topicName": topic,
        }
        try:
            result = self._service.users().watch(userId="me", body=request).execute()
            logger.info("Gmail push notifications configured", history_id=result.get("historyId"))
            return result
        except Exception as e:
            logger.error("Failed to set up push notifications", error=str(e))
            raise

    async def process_notification(self, notification_data: dict) -> Optional[dict]:
        """Process a Gmail Pub/Sub push notification.

        Returns extracted message data or None if not a new message.
        """
        if not self._setup_complete:
            await self.setup()

        try:
            # Decode Pub/Sub message
            encoded_data = notification_data.get("message", {}).get("data", "")
            decoded = json.loads(base64.b64decode(encoded_data).decode("utf-8"))

            email_address = decoded.get("emailAddress", "")
            history_id = decoded.get("historyId", "")

            # Get history changes
            history = self._service.users().history().list(
                userId="me", startHistoryId=history_id, historyTypes=["messageAdded"]
            ).execute()

            messages = []
            for record in history.get("history", []):
                for msg_added in record.get("messagesAdded", []):
                    msg_id = msg_added["message"]["id"]
                    message_data = await self.get_message(msg_id)
                    if message_data:
                        messages.append(message_data)

            return messages if messages else None
        except Exception as e:
            logger.error("Failed to process Gmail notification", error=str(e))
            return None

    async def get_message(self, message_id: str) -> Optional[dict]:
        """Retrieve and parse a Gmail message."""
        try:
            msg = self._service.users().messages().get(
                userId="me", id=message_id, format="full"
            ).execute()

            headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}

            return {
                "message_id": message_id,
                "thread_id": msg.get("threadId", ""),
                "from_email": self._extract_email(headers.get("from", "")),
                "from_name": self._extract_name(headers.get("from", "")),
                "subject": headers.get("subject", "(No Subject)"),
                "body": self._extract_body(msg.get("payload", {})),
                "date": headers.get("date", ""),
            }
        except Exception as e:
            logger.error("Failed to get Gmail message", message_id=message_id, error=str(e))
            return None

    async def send_reply(self, thread_id: str, to_email: str, subject: str, body: str) -> dict:
        """Send a reply email in the same thread."""
        try:
            message = MIMEText(body)
            message["to"] = to_email
            message["subject"] = f"Re: {subject}" if not subject.startswith("Re:") else subject
            message["In-Reply-To"] = thread_id
            message["References"] = thread_id

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            result = self._service.users().messages().send(
                userId="me",
                body={"raw": raw, "threadId": thread_id},
            ).execute()

            logger.info("Gmail reply sent", thread_id=thread_id, to=to_email)
            return {"status": "sent", "message_id": result.get("id", "")}
        except Exception as e:
            logger.error("Failed to send Gmail reply", error=str(e))
            return {"status": "error", "error": str(e)}

    def _extract_email(self, from_header: str) -> str:
        """Extract email address from 'Name <email>' format."""
        if "<" in from_header and ">" in from_header:
            return from_header.split("<")[1].split(">")[0]
        return from_header.strip()

    def _extract_name(self, from_header: str) -> str:
        """Extract name from 'Name <email>' format."""
        if "<" in from_header:
            return from_header.split("<")[0].strip().strip('"')
        return "Customer"

    def _extract_body(self, payload: dict) -> str:
        """Extract text body from email payload."""
        if payload.get("mimeType") == "text/plain":
            data = payload.get("body", {}).get("data", "")
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

        # Check parts for multipart messages
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

        # Fallback: try HTML
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/html":
                data = part.get("body", {}).get("data", "")
                html = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
                # Basic HTML stripping
                import re
                return re.sub(r"<[^>]+>", "", html).strip()

        return ""


class MockGmailHandler:
    """Mock Gmail handler for development without Gmail API credentials.

    Logs all operations to the database instead of calling Gmail API.
    """

    def __init__(self):
        self._setup_complete = False

    async def setup(self):
        """No-op setup for mock."""
        self._setup_complete = True
        logger.info("MockGmailHandler initialized (no Gmail API)")

    async def setup_push_notifications(self, topic_name: str = None):
        """Mock push notification setup."""
        logger.info("Mock: Gmail push notifications configured (no-op)")
        return {"historyId": "mock-0", "expiration": "9999999999999"}

    async def process_notification(self, notification_data: dict) -> Optional[dict]:
        """Mock notification processing - extract data from the raw payload."""
        logger.info("Mock: Processing Gmail notification", data=notification_data)

        # For mock, we accept direct message data in a simplified format
        if "email" in notification_data and "body" in notification_data:
            return [{
                "message_id": f"mock-{__import__('uuid').uuid4().hex[:8]}",
                "thread_id": f"mock-thread-{__import__('uuid').uuid4().hex[:8]}",
                "from_email": notification_data["email"],
                "from_name": notification_data.get("name", "Customer"),
                "subject": notification_data.get("subject", "Support Request"),
                "body": notification_data["body"],
                "date": __import__("datetime").datetime.utcnow().isoformat(),
            }]
        return None

    async def get_message(self, message_id: str) -> Optional[dict]:
        """Mock message retrieval."""
        logger.info("Mock: Get message", message_id=message_id)
        return None

    async def send_reply(self, thread_id: str, to_email: str, subject: str, body: str) -> dict:
        """Mock reply - logs instead of sending."""
        logger.info(
            "Mock: Email reply",
            thread_id=thread_id,
            to=to_email,
            subject=subject,
            body_length=len(body),
        )
        return {"status": "sent", "message_id": f"mock-sent-{__import__('uuid').uuid4().hex[:8]}"}

    def _extract_email(self, from_header: str) -> str:
        if "<" in from_header and ">" in from_header:
            return from_header.split("<")[1].split(">")[0]
        return from_header.strip()

    def _extract_name(self, from_header: str) -> str:
        if "<" in from_header:
            return from_header.split("<")[0].strip().strip('"')
        return "Customer"


def get_gmail_handler():
    """Factory: returns real or mock Gmail handler based on config."""
    if settings.USE_MOCK_GMAIL:
        logger.info("Using MockGmailHandler")
        return MockGmailHandler()
    else:
        logger.info("Using GmailHandler with Gmail API")
        return GmailHandler()
