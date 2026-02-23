"""Database query functions for CRM operations."""

import uuid
from datetime import datetime
from typing import Optional
import asyncpg
import structlog
from src.database.connection import get_db_pool

logger = structlog.get_logger()


async def create_customer(name: str, email: str = None, phone: str = None, company: str = None) -> dict:
    """Create a new customer record."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO customers (name, email, phone, company)
               VALUES ($1, $2, $3, $4)
               RETURNING id, name, email, phone, company, created_at""",
            name, email, phone, company
        )
        # Also create identifier records for cross-channel matching
        if email:
            await conn.execute(
                """INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value, channel)
                   VALUES ($1, 'email', $2, 'email')
                   ON CONFLICT (identifier_type, identifier_value) DO NOTHING""",
                row["id"], email
            )
        if phone:
            await conn.execute(
                """INSERT INTO customer_identifiers (customer_id, identifier_type, identifier_value, channel)
                   VALUES ($1, 'phone', $2, 'whatsapp')
                   ON CONFLICT (identifier_type, identifier_value) DO NOTHING""",
                row["id"], phone
            )
        logger.info("Customer created", customer_id=str(row["id"]), name=name)
        return dict(row)


async def find_customer_by_email(email: str) -> Optional[dict]:
    """Find customer by email address."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT c.* FROM customers c
               JOIN customer_identifiers ci ON c.id = ci.customer_id
               WHERE ci.identifier_type = 'email' AND ci.identifier_value = $1""",
            email
        )
        return dict(row) if row else None


async def find_customer_by_phone(phone: str) -> Optional[dict]:
    """Find customer by phone number."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT c.* FROM customers c
               JOIN customer_identifiers ci ON c.id = ci.customer_id
               WHERE ci.identifier_type = 'phone' AND ci.identifier_value = $1""",
            phone
        )
        return dict(row) if row else None


async def create_conversation(customer_id: uuid.UUID, channel: str, subject: str = None) -> dict:
    """Create a new conversation thread."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO conversations (customer_id, channel, subject)
               VALUES ($1, $2, $3)
               RETURNING id, customer_id, channel, status, subject, started_at""",
            customer_id, channel, subject
        )
        logger.info("Conversation created", conversation_id=str(row["id"]), channel=channel)
        return dict(row)


async def get_active_conversation(customer_id: uuid.UUID, channel: str) -> Optional[dict]:
    """Get active conversation for a customer on a specific channel."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT * FROM conversations
               WHERE customer_id = $1 AND channel = $2 AND status = 'active'
               ORDER BY started_at DESC LIMIT 1""",
            customer_id, channel
        )
        return dict(row) if row else None


async def create_message(conversation_id: uuid.UUID, sender_type: str, content: str, channel: str, metadata: dict = None) -> dict:
    """Store a message in a conversation."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO messages (conversation_id, sender_type, content, channel, metadata)
               VALUES ($1, $2, $3, $4, $5::jsonb)
               RETURNING id, conversation_id, sender_type, content, channel, created_at""",
            conversation_id, sender_type, content, channel,
            __import__("json").dumps(metadata or {})
        )
        return dict(row)


async def create_ticket(
    conversation_id: uuid.UUID,
    customer_id: uuid.UUID,
    channel: str,
    subject: str,
    category: str = None,
    priority: str = "medium"
) -> dict:
    """Create a support ticket."""
    pool = await get_db_pool()
    ticket_number = f"TKT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO tickets (ticket_number, conversation_id, customer_id, channel, subject, category, priority)
               VALUES ($1, $2, $3, $4, $5, $6, $7)
               RETURNING id, ticket_number, channel, subject, category, priority, status, created_at""",
            ticket_number, conversation_id, customer_id, channel, subject, category, priority
        )
        logger.info("Ticket created", ticket_number=ticket_number, channel=channel)
        return dict(row)


async def update_ticket_status(ticket_id: uuid.UUID, status: str, resolution: str = None) -> dict:
    """Update ticket status."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        resolved_at = datetime.utcnow() if status in ("resolved", "closed") else None
        row = await conn.fetchrow(
            """UPDATE tickets SET status = $2, resolution = $3, resolved_at = $4, updated_at = NOW()
               WHERE id = $1
               RETURNING id, ticket_number, status, resolution, updated_at""",
            ticket_id, status, resolution, resolved_at
        )
        return dict(row) if row else None


async def get_ticket_by_id(ticket_id: str) -> Optional[dict]:
    """Get ticket by ID or ticket number."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Try ticket_number first, then UUID
        row = await conn.fetchrow(
            "SELECT * FROM tickets WHERE ticket_number = $1", ticket_id
        )
        if not row:
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM tickets WHERE id = $1", uuid.UUID(ticket_id)
                )
            except ValueError:
                pass
        return dict(row) if row else None


async def search_knowledge_base(query: str, limit: int = 5) -> list[dict]:
    """Search knowledge base. Uses text search (vector search when embeddings available)."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        # Text-based search fallback (works without embeddings)
        rows = await conn.fetch(
            """SELECT id, title, content, category,
                      ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', $1)) as relevance
               FROM knowledge_base
               WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
               ORDER BY relevance DESC
               LIMIT $2""",
            query, limit
        )
        if not rows:
            # Fallback: ILIKE search
            rows = await conn.fetch(
                """SELECT id, title, content, category, 0.5 as relevance
                   FROM knowledge_base
                   WHERE content ILIKE '%' || $1 || '%' OR title ILIKE '%' || $1 || '%'
                   LIMIT $2""",
                query, limit
            )
        return [dict(r) for r in rows]


async def get_customer_history(customer_id: uuid.UUID, limit: int = 10) -> list[dict]:
    """Get cross-channel conversation history for a customer."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT c.id as conversation_id, c.channel, c.status, c.subject, c.started_at,
                      m.content, m.sender_type, m.created_at as message_time
               FROM conversations c
               JOIN messages m ON c.id = m.conversation_id
               WHERE c.customer_id = $1
               ORDER BY m.created_at DESC
               LIMIT $2""",
            customer_id, limit
        )
        return [dict(r) for r in rows]


async def record_metric(channel: str, metric_type: str, metric_value: float, metadata: dict = None) -> dict:
    """Record an agent performance metric."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """INSERT INTO agent_metrics (channel, metric_type, metric_value, metadata)
               VALUES ($1, $2, $3, $4::jsonb)
               RETURNING id, channel, metric_type, metric_value, recorded_at""",
            channel, metric_type, metric_value,
            __import__("json").dumps(metadata or {})
        )
        return dict(row)


async def get_channel_metrics(channel: str = None, hours: int = 24) -> list[dict]:
    """Get aggregated channel metrics."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        if channel:
            rows = await conn.fetch(
                """SELECT channel, metric_type,
                          AVG(metric_value) as avg_value,
                          COUNT(*) as count
                   FROM agent_metrics
                   WHERE channel = $1 AND recorded_at > NOW() - INTERVAL '1 hour' * $2
                   GROUP BY channel, metric_type""",
                channel, hours
            )
        else:
            rows = await conn.fetch(
                """SELECT channel, metric_type,
                          AVG(metric_value) as avg_value,
                          COUNT(*) as count
                   FROM agent_metrics
                   WHERE recorded_at > NOW() - INTERVAL '1 hour' * $1
                   GROUP BY channel, metric_type""",
                hours
            )
        return [dict(r) for r in rows]
