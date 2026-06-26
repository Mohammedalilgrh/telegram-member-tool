"""
Telegram Member Tool — Multi-Account config
"""
import os


class Settings:
    # Telegram API credentials (one set for all accounts)
    API_ID: int = int(os.getenv("TG_API_ID", "0"))
    API_HASH: str = os.getenv("TG_API_HASH", "")

    # Session strings for multiple accounts — stored as JSON
    # Format: [{"phone": "+xxx", "session": "string..."}, ...]
    ACCOUNTS_JSON: str = os.getenv("ACCOUNTS_JSON", "[]")

    # Default source & target groups
    SOURCE_GROUP: str = os.getenv("SOURCE_GROUP", "")
    TARGET_GROUP: str = os.getenv("TARGET_GROUP", "")

    # Safety per account
    DAILY_LIMIT_PER_ACCOUNT: int = int(os.getenv("DAILY_LIMIT", "35"))
    MAX_MEMBERS_PER_RUN: int = int(os.getenv("MAX_MEMBERS", "200"))

    # Delays
    MIN_DELAY: float = float(os.getenv("MIN_DELAY", "2.0"))
    MAX_DELAY: float = float(os.getenv("MAX_DELAY", "5.0"))

    # Daily schedule (UTC)
    SCHEDULE_TIME: str = os.getenv("SCHEDULE_TIME", "09:00")

    # Dashboard
    DASHBOARD_TOKEN: str = os.getenv("DASHBOARD_TOKEN", "admin123")

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
