"""Tests for database query functions (mocked)."""

import pytest
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestDatabaseQueries:
    """Test database query functions with mocked connection pool."""

    @pytest.fixture
    def mock_pool(self):
        """Create a mock database pool."""
        pool = AsyncMock()
        conn = AsyncMock()

        # Mock async context manager
        pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
        pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

        return pool, conn

    @pytest.mark.asyncio
    async def test_create_customer(self, mock_pool):
        pool, conn = mock_pool
        test_id = uuid.uuid4()
        conn.fetchrow.return_value = {
            "id": test_id,
            "name": "Test User",
            "email": "test@example.com",
            "phone": None,
            "company": None,
            "created_at": datetime.utcnow(),
        }

        with patch("src.database.queries.get_db_pool", return_value=pool):
            from src.database.queries import create_customer
            result = await create_customer(name="Test User", email="test@example.com")

        assert result["name"] == "Test User"
        assert result["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_find_customer_by_email(self, mock_pool):
        pool, conn = mock_pool
        conn.fetchrow.return_value = {
            "id": uuid.uuid4(),
            "name": "Found User",
            "email": "found@example.com",
        }

        with patch("src.database.queries.get_db_pool", return_value=pool):
            from src.database.queries import find_customer_by_email
            result = await find_customer_by_email("found@example.com")

        assert result is not None
        assert result["name"] == "Found User"

    @pytest.mark.asyncio
    async def test_find_customer_by_email_not_found(self, mock_pool):
        pool, conn = mock_pool
        conn.fetchrow.return_value = None

        with patch("src.database.queries.get_db_pool", return_value=pool):
            from src.database.queries import find_customer_by_email
            result = await find_customer_by_email("missing@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_ticket(self, mock_pool):
        pool, conn = mock_pool
        conn.fetchrow.return_value = {
            "id": uuid.uuid4(),
            "ticket_number": "TKT-20260223-ABC123",
            "channel": "email",
            "subject": "Test Issue",
            "category": "bug_report",
            "priority": "high",
            "status": "open",
            "created_at": datetime.utcnow(),
        }

        with patch("src.database.queries.get_db_pool", return_value=pool):
            from src.database.queries import create_ticket
            result = await create_ticket(
                conversation_id=uuid.uuid4(),
                customer_id=uuid.uuid4(),
                channel="email",
                subject="Test Issue",
                category="bug_report",
                priority="high",
            )

        assert result["ticket_number"].startswith("TKT-")
        assert result["status"] == "open"

    @pytest.mark.asyncio
    async def test_search_knowledge_base(self, mock_pool):
        pool, conn = mock_pool
        conn.fetch.return_value = [
            {"id": uuid.uuid4(), "title": "Getting Started", "content": "Welcome!", "category": "getting_started", "relevance": 0.95},
        ]

        with patch("src.database.queries.get_db_pool", return_value=pool):
            from src.database.queries import search_knowledge_base
            results = await search_knowledge_base("getting started")

        assert len(results) == 1
        assert results[0]["title"] == "Getting Started"

    @pytest.mark.asyncio
    async def test_get_customer_history(self, mock_pool):
        pool, conn = mock_pool
        conn.fetch.return_value = [
            {
                "conversation_id": uuid.uuid4(),
                "channel": "email",
                "status": "resolved",
                "subject": "Previous Issue",
                "started_at": datetime.utcnow(),
                "content": "I had a problem...",
                "sender_type": "customer",
                "message_time": datetime.utcnow(),
            }
        ]

        with patch("src.database.queries.get_db_pool", return_value=pool):
            from src.database.queries import get_customer_history
            results = await get_customer_history(uuid.uuid4())

        assert len(results) == 1
        assert results[0]["channel"] == "email"

    @pytest.mark.asyncio
    async def test_record_metric(self, mock_pool):
        pool, conn = mock_pool
        conn.fetchrow.return_value = {
            "id": uuid.uuid4(),
            "channel": "email",
            "metric_type": "response_time",
            "metric_value": 1.5,
            "recorded_at": datetime.utcnow(),
        }

        with patch("src.database.queries.get_db_pool", return_value=pool):
            from src.database.queries import record_metric
            result = await record_metric("email", "response_time", 1.5)

        assert result["metric_type"] == "response_time"
        assert result["metric_value"] == 1.5
