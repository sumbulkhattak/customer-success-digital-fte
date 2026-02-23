"""Tests for the Customer Success Agent."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.agent.customer_success_agent import MockAgent
from src.agent.formatters import format_for_channel, format_search_results, format_customer_history
from src.agent.prompts import get_system_prompt, CUSTOMER_SUCCESS_SYSTEM_PROMPT


class TestMockAgent:
    """Test the MockAgent keyword-based processing."""

    @pytest.fixture
    def agent(self):
        return MockAgent()

    @pytest.mark.asyncio
    @patch("src.agent.tools.create_ticket", new_callable=AsyncMock)
    @patch("src.agent.tools.get_customer_history", new_callable=AsyncMock)
    @patch("src.agent.tools.search_knowledge_base", new_callable=AsyncMock)
    @patch("src.agent.tools.send_response", new_callable=AsyncMock)
    async def test_password_reset_categorization(self, mock_send, mock_search, mock_history, mock_ticket, agent):
        """Agent should categorize password reset messages correctly."""
        mock_ticket.return_value = '{"status": "created", "ticket_number": "TKT-001", "ticket_id": "abc"}'
        mock_history.return_value = "No previous interaction history found."
        mock_search.return_value = "Password reset instructions..."
        mock_send.return_value = '{"status": "sent"}'

        result = await agent.run(
            message="I forgot my password and can't log in",
            channel="email",
            customer_name="Test User",
            customer_id="test-id",
            conversation_id="conv-id",
        )

        assert result["category"] == "password_reset"
        assert result["escalated"] is False

    @pytest.mark.asyncio
    @patch("src.agent.tools.create_ticket", new_callable=AsyncMock)
    @patch("src.agent.tools.escalate_to_human", new_callable=AsyncMock)
    @patch("src.agent.tools.send_response", new_callable=AsyncMock)
    async def test_pricing_triggers_escalation(self, mock_send, mock_escalate, mock_ticket, agent):
        """Agent should escalate pricing questions."""
        mock_ticket.return_value = '{"status": "created", "ticket_number": "TKT-002", "ticket_id": "abc"}'
        mock_escalate.return_value = '{"status": "escalated"}'
        mock_send.return_value = '{"status": "sent"}'

        result = await agent.run(
            message="What is the pricing for the enterprise plan?",
            channel="email",
            customer_name="Test User",
            customer_id="test-id",
            conversation_id="conv-id",
        )

        assert result["escalated"] is True

    @pytest.mark.asyncio
    @patch("src.agent.tools.create_ticket", new_callable=AsyncMock)
    @patch("src.agent.tools.escalate_to_human", new_callable=AsyncMock)
    @patch("src.agent.tools.send_response", new_callable=AsyncMock)
    async def test_angry_customer_escalation(self, mock_send, mock_escalate, mock_ticket, agent):
        """Agent should escalate when multiple profanity indicators detected."""
        mock_ticket.return_value = '{"status": "created", "ticket_number": "TKT-003", "ticket_id": "abc"}'
        mock_escalate.return_value = '{"status": "escalated"}'
        mock_send.return_value = '{"status": "sent"}'

        result = await agent.run(
            message="This is terrible and useless, the worst product ever",
            channel="whatsapp",
            customer_name="Angry User",
            customer_id="test-id",
            conversation_id="conv-id",
        )

        assert result["escalated"] is True

    @pytest.mark.asyncio
    @patch("src.agent.tools.create_ticket", new_callable=AsyncMock)
    @patch("src.agent.tools.escalate_to_human", new_callable=AsyncMock)
    @patch("src.agent.tools.send_response", new_callable=AsyncMock)
    async def test_legal_language_escalation(self, mock_send, mock_escalate, mock_ticket, agent):
        """Agent should escalate legal language."""
        mock_ticket.return_value = '{"status": "created", "ticket_number": "TKT-004", "ticket_id": "abc"}'
        mock_escalate.return_value = '{"status": "escalated"}'
        mock_send.return_value = '{"status": "sent"}'

        result = await agent.run(
            message="I will contact my attorney about this lawsuit",
            channel="email",
            customer_name="Legal User",
            customer_id="test-id",
            conversation_id="conv-id",
        )

        assert result["escalated"] is True

    def test_category_detection(self, agent):
        """Test category keyword matching."""
        assert agent._detect_category("how to create a project") == "feature_question"
        assert agent._detect_category("password reset please") == "password_reset"
        assert agent._detect_category("billing invoice charge") == "billing"
        assert agent._detect_category("slack integration not working") == "integration"
        assert agent._detect_category("api endpoint rate limit") == "api_help"

    def test_priority_detection(self, agent):
        """Test priority detection from message urgency."""
        assert agent._detect_priority("this is urgent please help asap") == "urgent"
        assert agent._detect_priority("this is important and broken") == "high"
        assert agent._detect_priority("just a general question") == "medium"


class TestFormatters:
    """Test channel-specific formatters."""

    def test_email_format_includes_greeting(self):
        result = format_for_channel("Here is your answer.", "email", "John", "TKT-001")
        assert "Dear John" in result
        assert "TKT-001" in result
        assert "Best regards" in result

    def test_whatsapp_format_concise(self):
        result = format_for_channel("Here is your answer.", "whatsapp", "Jane", "TKT-002")
        assert "Hi Jane" in result
        assert len(result) <= 300

    def test_whatsapp_truncates_long_messages(self):
        long_message = "A" * 500
        result = format_for_channel(long_message, "whatsapp", "Jane", "TKT-002")
        assert len(result) <= 300

    def test_web_form_includes_help_link(self):
        result = format_for_channel("Here is your answer.", "web_form", "Bob", "TKT-003")
        assert "Hello Bob" in result
        assert "help.techcorp.com" in result
        assert "TKT-003" in result

    def test_format_search_results_empty(self):
        result = format_search_results([])
        assert "No relevant documentation found" in result

    def test_format_search_results_with_data(self):
        results = [
            {"title": "Getting Started", "content": "Step 1: Create account", "relevance": 0.95},
        ]
        result = format_search_results(results)
        assert "Getting Started" in result
        assert "0.95" in result

    def test_format_customer_history_empty(self):
        result = format_customer_history([])
        assert "No previous interaction" in result


class TestPrompts:
    """Test system prompt generation."""

    def test_system_prompt_contains_required_sections(self):
        assert "Required Workflow" in CUSTOMER_SUCCESS_SYSTEM_PROMPT
        assert "Hard Constraints" in CUSTOMER_SUCCESS_SYSTEM_PROMPT
        assert "Escalation Triggers" in CUSTOMER_SUCCESS_SYSTEM_PROMPT

    def test_get_system_prompt_fills_variables(self):
        prompt = get_system_prompt("email", "Alice", "conv-123")
        assert "email" in prompt
        assert "Alice" in prompt
        assert "conv-123" in prompt

    def test_channel_addendum_email(self):
        prompt = get_system_prompt("email")
        assert "thorough" in prompt.lower() or "professional" in prompt.lower()

    def test_channel_addendum_whatsapp(self):
        prompt = get_system_prompt("whatsapp")
        assert "brief" in prompt.lower() or "concise" in prompt.lower()
