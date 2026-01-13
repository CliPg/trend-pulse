"""
Configuration management for TrendPulse.
Loads all settings from environment variables.
"""
import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Reddit
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "trendpulse/1.0")

    # YouTube
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")

    # X/Twitter (Optional)
    TWITTER_BEARER_TOKEN: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")

    # LLM API (Tongyi Qianwen)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_BASE_URL: str = os.getenv(
        "LLM_API_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen-plus")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./trendpulse.db")

    # App Settings
    MAX_POSTS_PER_PLATFORM: int = int(os.getenv("MAX_POSTS_PER_PLATFORM", "50"))
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "en")

    @classmethod
    def validate(cls) -> None:
        """
        Validate that required credentials are present.
        Raises ValueError if any required credential is missing.
        """
        missing = []

        if not all([cls.REDDIT_CLIENT_ID, cls.REDDIT_CLIENT_SECRET]):
            missing.append("Reddit credentials (REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)")

        if not cls.YOUTUBE_API_KEY:
            missing.append("YouTube API key (YOUTUBE_API_KEY)")

        if not cls.LLM_API_KEY:
            missing.append("LLM API key (LLM_API_KEY)")

        if missing:
            raise ValueError(
                "Missing required credentials:\n" + "\n".join(f"  - {m}" for m in missing)
            )
