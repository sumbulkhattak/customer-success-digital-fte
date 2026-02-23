"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings from environment."""

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # PostgreSQL
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "fte_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "fte_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "fte_password_dev")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # AI Provider (supports OpenAI, Groq, Google Gemini via OpenAI-compatible API)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")  # Custom base URL for Groq/Gemini
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o")  # Model name (provider-specific)
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai")  # openai, groq, gemini

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    # Gmail
    GMAIL_CREDENTIALS_PATH: str = os.getenv("GMAIL_CREDENTIALS_PATH", "")
    GMAIL_PUBSUB_TOPIC: str = os.getenv("GMAIL_PUBSUB_TOPIC", "")

    # Twilio
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_WHATSAPP_NUMBER: str = os.getenv("TWILIO_WHATSAPP_NUMBER", "")

    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")

    # Feature flags (for mock mode)
    USE_MOCK_OPENAI: bool = not os.getenv("OPENAI_API_KEY", "")
    USE_MOCK_GMAIL: bool = not os.getenv("GMAIL_CREDENTIALS_PATH", "")
    USE_MOCK_TWILIO: bool = not os.getenv("TWILIO_ACCOUNT_SID", "")

    @property
    def effective_base_url(self) -> str:
        """Get the effective base URL for the AI provider."""
        if self.OPENAI_BASE_URL:
            return self.OPENAI_BASE_URL
        provider = self.AI_PROVIDER.lower()
        if provider == "groq":
            return "https://api.groq.com/openai/v1"
        elif provider == "gemini":
            return "https://generativelanguage.googleapis.com/v1beta/openai/"
        return ""  # Default OpenAI

    @property
    def effective_model(self) -> str:
        """Get the effective model name for the AI provider."""
        if self.AI_MODEL != "gpt-4o":
            return self.AI_MODEL  # User explicitly set a model
        provider = self.AI_PROVIDER.lower()
        if provider == "groq":
            return "llama-3.3-70b-versatile"
        elif provider == "gemini":
            return "gemini-2.0-flash"
        return self.AI_MODEL  # Default gpt-4o


settings = Settings()
