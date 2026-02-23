"""Channel-aware response formatters."""

from typing import Optional


def format_for_channel(response: str, channel: str, customer_name: str = "Customer", ticket_number: str = "") -> str:
    """Format agent response for the specific channel."""
    if channel == "email":
        return _format_email(response, customer_name, ticket_number)
    elif channel == "whatsapp":
        return _format_whatsapp(response, customer_name, ticket_number)
    elif channel == "web_form":
        return _format_web_form(response, customer_name, ticket_number)
    return response


def _format_email(response: str, customer_name: str, ticket_number: str) -> str:
    """Format for email: formal with greeting and signature."""
    parts = [
        f"Dear {customer_name},",
        "",
        "Thank you for reaching out to TechCorp Support.",
        "",
        response,
        "",
    ]
    if ticket_number:
        parts.append(f"Your ticket reference: {ticket_number}")
        parts.append("")
    parts.extend([
        "If you need further assistance, please reply to this email.",
        "",
        "Best regards,",
        "TechCorp Support Team",
    ])
    # Enforce max 500 words
    full_text = "\n".join(parts)
    words = full_text.split()
    if len(words) > 500:
        full_text = " ".join(words[:500]) + "..."
    return full_text


def _format_whatsapp(response: str, customer_name: str, ticket_number: str) -> str:
    """Format for WhatsApp: concise with optional emoji."""
    greeting = f"Hi {customer_name}! "
    footer = ""
    if ticket_number:
        footer = f"\n\nRef: {ticket_number}"

    formatted = greeting + response + footer

    # Enforce 300 char preference (truncate with ellipsis if needed)
    if len(formatted) > 300:
        available = 300 - len(greeting) - len(footer) - 3  # 3 for "..."
        formatted = greeting + response[:available] + "..." + footer

    return formatted


def _format_web_form(response: str, customer_name: str, ticket_number: str) -> str:
    """Format for web form: semi-formal with help link."""
    parts = [
        f"Hello {customer_name},",
        "",
        response,
        "",
    ]
    if ticket_number:
        parts.append(f"Ticket Reference: {ticket_number}")
    parts.extend([
        "",
        "Need more help? Visit our Help Center: https://help.techcorp.com",
        "",
        "— TechCorp Support",
    ])
    # Enforce max 300 words
    full_text = "\n".join(parts)
    words = full_text.split()
    if len(words) > 300:
        full_text = " ".join(words[:300]) + "..."
    return full_text


def format_search_results(results: list[dict]) -> str:
    """Format knowledge base search results for agent context."""
    if not results:
        return "No relevant documentation found."

    formatted = []
    for i, result in enumerate(results, 1):
        title = result.get("title", "Untitled")
        content = result.get("content", "")
        relevance = result.get("relevance", 0)
        # Truncate content for context window efficiency
        if len(content) > 500:
            content = content[:500] + "..."
        formatted.append(f"[{i}] {title} (relevance: {relevance:.2f})\n{content}")

    return "\n\n".join(formatted)


def format_customer_history(history: list[dict]) -> str:
    """Format cross-channel customer history for agent context."""
    if not history:
        return "No previous interaction history found."

    formatted = ["Previous interactions:"]
    for entry in history:
        channel = entry.get("channel", "unknown")
        sender = entry.get("sender_type", "unknown")
        content = entry.get("content", "")
        timestamp = entry.get("message_time", "")
        subject = entry.get("subject", "")

        # Truncate long messages
        if len(content) > 200:
            content = content[:200] + "..."

        line = f"- [{channel}] ({timestamp}) {sender}: {content}"
        if subject:
            line = f"- [{channel}] {subject} ({timestamp}) {sender}: {content}"
        formatted.append(line)

    return "\n".join(formatted)
