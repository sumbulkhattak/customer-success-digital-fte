"""End-to-end tests using FastAPI TestClient."""

import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport

from src.api.main import app


@pytest.fixture
def mock_db():
    """Mock database operations for E2E tests."""
    with patch("src.database.connection.get_db_pool") as mock_pool, \
         patch("src.database.connection.init_db") as mock_init, \
         patch("src.database.connection.close_db") as mock_close:

        mock_init.return_value = None
        mock_close.return_value = None

        # Mock pool with async context manager
        pool = AsyncMock()
        conn = AsyncMock()
        conn.fetchval = AsyncMock(return_value=1)
        conn.fetchrow = AsyncMock(return_value=None)
        conn.fetch = AsyncMock(return_value=[])
        pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
        pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_pool.return_value = pool

        yield {"pool": pool, "conn": conn}


@pytest.mark.asyncio
async def test_health_check(mock_db):
    """Test health endpoint returns system status."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "customer-success-fte"
    assert "channels" in data
    assert "components" in data


@pytest.mark.asyncio
async def test_web_form_validation_error(mock_db):
    """Test web form rejects invalid submissions."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/support/submit", json={
            "name": "J",  # too short
            "email": "invalid",
            "subject": "Hi",  # too short
            "category": "invalid",
            "message": "short",
        })

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_ticket_not_found(mock_db):
    """Test ticket lookup returns 404 for unknown tickets."""
    with patch("src.database.queries.get_ticket_by_id", new_callable=AsyncMock, return_value=None):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/support/ticket/NONEXISTENT")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_customer_lookup_no_params(mock_db):
    """Test customer lookup requires email or phone."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/customers/lookup")

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_metrics_endpoint(mock_db):
    """Test metrics endpoint returns data."""
    with patch("src.database.queries.get_channel_metrics", new_callable=AsyncMock, return_value=[]):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/metrics/channels")

    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "period_hours" in data
