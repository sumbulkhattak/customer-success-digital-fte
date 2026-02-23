"""Seed script to populate knowledge base and channel configs."""

import asyncio
import os
import json
import random
import structlog
from src.database.connection import get_db_pool, init_db

logger = structlog.get_logger()


def split_into_sections(content: str) -> list[dict]:
    """Split markdown content into titled sections."""
    sections = []
    current_title = ""
    current_content = []
    current_category = "general"

    for line in content.split("\n"):
        if line.startswith("## "):
            if current_title and current_content:
                sections.append({
                    "title": current_title,
                    "content": "\n".join(current_content).strip(),
                    "category": current_category,
                })
            current_title = line.lstrip("# ").strip()
            current_content = []
            # Derive category from section title
            title_lower = current_title.lower()
            if "getting started" in title_lower:
                current_category = "getting_started"
            elif "account" in title_lower:
                current_category = "account_management"
            elif "feature" in title_lower or "project" in title_lower or "task" in title_lower:
                current_category = "features"
            elif "integration" in title_lower:
                current_category = "integrations"
            elif "troubleshoot" in title_lower or "error" in title_lower:
                current_category = "troubleshooting"
            elif "faq" in title_lower:
                current_category = "faq"
            else:
                current_category = "general"
        else:
            current_content.append(line)

    # Don't forget last section
    if current_title and current_content:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_content).strip(),
            "category": current_category,
        })

    return sections


def generate_mock_embedding(dimension: int = 1536) -> list[float]:
    """Generate a mock embedding vector (random, normalized)."""
    vec = [random.gauss(0, 1) for _ in range(dimension)]
    magnitude = sum(x**2 for x in vec) ** 0.5
    return [x / magnitude for x in vec]


async def seed_knowledge_base(pool) -> int:
    """Seed knowledge base from product-docs.md."""
    docs_path = os.path.join(os.path.dirname(__file__), "..", "..", "context", "product-docs.md")
    if not os.path.exists(docs_path):
        logger.warning("product-docs.md not found", path=docs_path)
        return 0

    with open(docs_path, "r", encoding="utf-8") as f:
        content = f.read()

    sections = split_into_sections(content)
    count = 0

    async with pool.acquire() as conn:
        for section in sections:
            embedding = generate_mock_embedding()
            embedding_str = "[" + ",".join(str(v) for v in embedding) + "]"
            await conn.execute(
                """INSERT INTO knowledge_base (title, content, category, embedding)
                   VALUES ($1, $2, $3, $4::vector)
                   ON CONFLICT DO NOTHING""",
                section["title"], section["content"], section["category"], embedding_str
            )
            count += 1

    logger.info("Knowledge base seeded", sections=count)
    return count


async def seed_channel_configs(pool) -> None:
    """Seed default channel configurations."""
    configs = [
        {
            "channel": "email",
            "config": json.dumps({
                "greeting": "Dear {customer_name},",
                "signature": "Best regards,\\nTechCorp Support Team",
                "max_words": 500,
            }),
            "response_template": "Dear {customer_name},\\n\\n{response}\\n\\nTicket Reference: {ticket_number}\\n\\nBest regards,\\nTechCorp Support Team",
            "max_response_length": 3000,
        },
        {
            "channel": "whatsapp",
            "config": json.dumps({
                "emoji_allowed": True,
                "max_chars": 300,
                "split_long_messages": True,
            }),
            "response_template": "Hi {customer_name}! {response}",
            "max_response_length": 300,
        },
        {
            "channel": "web_form",
            "config": json.dumps({
                "include_ticket_link": True,
                "include_help_center": True,
            }),
            "response_template": "Hello {customer_name},\\n\\n{response}\\n\\nYour ticket: {ticket_number}\\nHelp Center: https://help.techcorp.com",
            "max_response_length": 2000,
        },
    ]

    async with pool.acquire() as conn:
        for cfg in configs:
            await conn.execute(
                """INSERT INTO channel_configs (channel, config, response_template, max_response_length)
                   VALUES ($1, $2::jsonb, $3, $4)
                   ON CONFLICT (channel) DO UPDATE SET config = $2::jsonb, response_template = $3, max_response_length = $4""",
                cfg["channel"], cfg["config"], cfg["response_template"], cfg["max_response_length"]
            )

    logger.info("Channel configs seeded", channels=len(configs))


async def run_seed():
    """Run all seed operations."""
    await init_db()
    pool = await get_db_pool()
    kb_count = await seed_knowledge_base(pool)
    await seed_channel_configs(pool)
    logger.info("Seeding complete", knowledge_base_sections=kb_count)


if __name__ == "__main__":
    asyncio.run(run_seed())
