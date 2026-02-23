"""MCP Server exposing Customer Success agent tools.

Allows MCP-compatible clients (e.g., Claude Desktop) to use the
customer success tools directly.
"""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import run_server
from mcp.types import Tool, TextContent
import structlog

from src.database.connection import init_db, close_db
from src.agent import tools as agent_tools

logger = structlog.get_logger()

# Create MCP server
server = Server("customer-success-fte")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available customer success tools."""
    return [
        Tool(
            name="search_knowledge_base",
            description="Search the TechCorp product knowledge base for relevant documentation. Use to find answers about features, troubleshooting, account management, and integrations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for the knowledge base",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (1-20)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="create_ticket",
            description="Create a support ticket for tracking a customer interaction. Must be called before sending any response.",
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string", "description": "UUID of the conversation"},
                    "customer_id": {"type": "string", "description": "UUID of the customer"},
                    "channel": {"type": "string", "enum": ["email", "whatsapp", "web_form"], "description": "Source channel"},
                    "subject": {"type": "string", "description": "Brief description of the issue"},
                    "category": {
                        "type": "string",
                        "enum": ["password_reset", "feature_question", "bug_report", "billing", "feedback", "integration", "api_help"],
                        "description": "Issue category",
                    },
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "default": "medium"},
                },
                "required": ["conversation_id", "customer_id", "channel", "subject"],
            },
        ),
        Tool(
            name="get_customer_history",
            description="Retrieve a customer's previous interactions across all channels (email, WhatsApp, web form).",
            inputSchema={
                "type": "object",
                "properties": {
                    "customer_id": {"type": "string", "description": "UUID of the customer"},
                    "limit": {"type": "integer", "description": "Max history entries", "default": 10},
                },
                "required": ["customer_id"],
            },
        ),
        Tool(
            name="escalate_to_human",
            description="Escalate the conversation to a human support agent. Use when: legal language detected, customer very upset, pricing/refund requests, or customer requests human help.",
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string", "description": "UUID of the conversation"},
                    "customer_id": {"type": "string", "description": "UUID of the customer"},
                    "reason": {"type": "string", "description": "Reason for escalation"},
                    "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"], "default": "P3"},
                    "channel": {"type": "string", "enum": ["email", "whatsapp", "web_form"]},
                    "context_summary": {"type": "string", "description": "Summary of conversation so far"},
                },
                "required": ["conversation_id", "customer_id", "reason", "channel"],
            },
        ),
        Tool(
            name="send_response",
            description="Send a formatted response to the customer. Automatically formats for the channel (email: formal, WhatsApp: concise, web: semi-formal).",
            inputSchema={
                "type": "object",
                "properties": {
                    "conversation_id": {"type": "string", "description": "UUID of the conversation"},
                    "customer_id": {"type": "string", "description": "UUID of the customer"},
                    "channel": {"type": "string", "enum": ["email", "whatsapp", "web_form"]},
                    "response": {"type": "string", "description": "The response message content"},
                    "customer_name": {"type": "string", "default": "Customer"},
                    "ticket_number": {"type": "string", "default": ""},
                },
                "required": ["conversation_id", "customer_id", "channel", "response"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a customer success tool."""
    try:
        if name == "search_knowledge_base":
            result = await agent_tools.search_knowledge_base(
                query=arguments["query"],
                limit=arguments.get("limit", 5),
            )
        elif name == "create_ticket":
            result = await agent_tools.create_ticket(
                conversation_id=arguments["conversation_id"],
                customer_id=arguments["customer_id"],
                channel=arguments["channel"],
                subject=arguments["subject"],
                category=arguments.get("category"),
                priority=arguments.get("priority", "medium"),
            )
        elif name == "get_customer_history":
            result = await agent_tools.get_customer_history(
                customer_id=arguments["customer_id"],
                limit=arguments.get("limit", 10),
            )
        elif name == "escalate_to_human":
            result = await agent_tools.escalate_to_human(
                conversation_id=arguments["conversation_id"],
                customer_id=arguments["customer_id"],
                reason=arguments["reason"],
                severity=arguments.get("severity", "P3"),
                channel=arguments["channel"],
                context_summary=arguments.get("context_summary", ""),
            )
        elif name == "send_response":
            result = await agent_tools.send_response(
                conversation_id=arguments["conversation_id"],
                customer_id=arguments["customer_id"],
                channel=arguments["channel"],
                response=arguments["response"],
                customer_name=arguments.get("customer_name", "Customer"),
                ticket_number=arguments.get("ticket_number", ""),
            )
        else:
            result = json.dumps({"error": f"Unknown tool: {name}"})

        return [TextContent(type="text", text=result)]

    except Exception as e:
        logger.error("MCP tool execution failed", tool=name, error=str(e))
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Run the MCP server."""
    # Initialize database connection
    await init_db()
    logger.info("MCP Server starting", tools=5)

    try:
        await run_server(server)
    finally:
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
