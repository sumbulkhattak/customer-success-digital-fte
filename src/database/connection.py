"""Database connection pool manager using asyncpg."""

import asyncpg
import structlog
import os
from src.config import settings

logger = structlog.get_logger()

_pool: asyncpg.Pool | None = None


async def get_db_pool() -> asyncpg.Pool:
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            min_size=2,
            max_size=10,
        )
        logger.info("Database pool created", host=settings.POSTGRES_HOST, db=settings.POSTGRES_DB)
    return _pool


async def init_db() -> None:
    """Initialize database by running schema.sql."""
    pool = await get_db_pool()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    async with pool.acquire() as conn:
        await conn.execute(schema_sql)
    logger.info("Database schema initialized")


async def close_db() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database pool closed")
