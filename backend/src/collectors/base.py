"""
Base collector interface for all social media platforms.
Defines abstract interface and common utility methods.
"""
from abc import ABC, abstractmethod
from typing import List
from dataclasses import dataclass
import re


@dataclass
class PostData:
    """Standardized post data structure across all platforms."""

    platform: str
    post_id: str
    author: str | None
    content: str
    url: str | None
    upvotes: int = 0
    likes: int = 0
    shares: int = 0
    comments_count: int = 0
    created_at: str | None = None


class BaseCollector(ABC):
    """Abstract base class for all platform collectors."""

    def __init__(self, config: dict):
        """
        Initialize collector with configuration.

        Args:
            config: Dictionary of configuration values
        """
        self.config = config

    @abstractmethod
    async def search(
        self, keyword: str, language: str = "en", limit: int = 50
    ) -> List[PostData]:
        """
        Search for posts containing the keyword.

        Args:
            keyword: Search query
            language: Language code (en, zh)
            limit: Maximum number of posts to collect

        Returns:
            List of PostData objects
        """
        pass

    def clean_content(self, content: str) -> str:
        """
        Remove HTML, markdown, and other artifacts from content.

        Args:
            content: Raw content text

        Returns:
            Cleaned content string
        """
        # Remove URLs
        content = re.sub(r"http\S+", "", content)

        # Remove markdown links
        content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)

        # Remove extra whitespace and newlines
        content = " ".join(content.split())

        return content.strip()

    def is_spam(self, content: str) -> bool:
        """
        Simple spam detection.

        Args:
            content: Content to check

        Returns:
            True if content appears to be spam
        """
        spam_indicators = [
            "buy now",
            "click here",
            "free trial",
            "limited time",
            "subscribe",
            "follow me",
            "check my profile",
            "DM me",
            "link in bio",
        ]

        content_lower = content.lower()
        return any(indicator in content_lower for indicator in spam_indicators)
