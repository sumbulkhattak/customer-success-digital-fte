"""Tests for channel handlers."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.channels.gmail_handler import MockGmailHandler
from src.channels.whatsapp_handler import MockWhatsAppHandler
from src.channels.web_form_handler import SupportFormSubmission


class TestMockGmailHandler:
    """Test MockGmailHandler."""

    @pytest.fixture
    def handler(self):
        return MockGmailHandler()

    @pytest.mark.asyncio
    async def test_setup(self, handler):
        await handler.setup()
        assert handler._setup_complete is True

    @pytest.mark.asyncio
    async def test_process_notification_with_data(self, handler):
        notification = {
            "email": "test@example.com",
            "name": "Test User",
            "subject": "Help needed",
            "body": "I need help with my account",
        }
        result = await handler.process_notification(notification)
        assert result is not None
        assert len(result) == 1
        assert result[0]["from_email"] == "test@example.com"
        assert result[0]["body"] == "I need help with my account"

    @pytest.mark.asyncio
    async def test_process_notification_empty(self, handler):
        result = await handler.process_notification({})
        assert result is None

    @pytest.mark.asyncio
    async def test_send_reply(self, handler):
        result = await handler.send_reply("thread-1", "user@test.com", "Re: Help", "Here is help")
        assert result["status"] == "sent"


class TestMockWhatsAppHandler:
    """Test MockWhatsAppHandler."""

    @pytest.fixture
    def handler(self):
        return MockWhatsAppHandler()

    def test_validate_webhook_always_true(self, handler):
        assert handler.validate_webhook("url", {}, "sig") is True

    @pytest.mark.asyncio
    async def test_process_webhook(self, handler):
        form_data = {
            "From": "whatsapp:+1234567890",
            "Body": "Hello, need help!",
            "ProfileName": "Test User",
        }
        result = await handler.process_webhook(form_data)
        assert result is not None
        assert result["from_number"] == "+1234567890"
        assert result["body"] == "Hello, need help!"
        assert result["from_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_process_webhook_empty_body(self, handler):
        result = await handler.process_webhook({"From": "whatsapp:+1234567890", "Body": ""})
        assert result is None

    @pytest.mark.asyncio
    async def test_send_message(self, handler):
        result = await handler.send_message("+1234567890", "Hello!")
        assert result["status"] == "sent"
        assert result["parts"] == 1

    def test_format_response_short(self, handler):
        parts = handler.format_response("Short message")
        assert len(parts) == 1

    def test_format_response_long(self, handler):
        long_msg = "This is a very long message. " * 20
        parts = handler.format_response(long_msg, max_length=100)
        assert len(parts) > 1
        for part in parts:
            assert len(part) <= 100


class TestSupportFormValidation:
    """Test web form Pydantic validation."""

    def test_valid_submission(self):
        form = SupportFormSubmission(
            name="John Doe",
            email="john@example.com",
            subject="Need help with project",
            category="feature_question",
            priority="medium",
            message="I need help understanding how to create a new project in the platform.",
        )
        assert form.name == "John Doe"
        assert form.email == "john@example.com"

    def test_invalid_email(self):
        with pytest.raises(Exception):
            SupportFormSubmission(
                name="John Doe",
                email="not-an-email",
                subject="Need help",
                category="feature_question",
                message="This is a test message for the form.",
            )

    def test_invalid_category(self):
        with pytest.raises(Exception):
            SupportFormSubmission(
                name="John Doe",
                email="john@example.com",
                subject="Need help",
                category="invalid_category",
                message="This is a test message for the form.",
            )

    def test_short_message(self):
        with pytest.raises(Exception):
            SupportFormSubmission(
                name="John Doe",
                email="john@example.com",
                subject="Need help",
                category="feature_question",
                message="Short",
            )

    def test_email_normalized(self):
        form = SupportFormSubmission(
            name="John Doe",
            email="  JOHN@Example.COM  ",
            subject="Need help with project",
            category="feature_question",
            message="I need help understanding how to create a new project.",
        )
        assert form.email == "john@example.com"
