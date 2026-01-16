"""
Reddit data collector using PRAW library.
Collects posts and comments from Reddit based on keyword search.
"""
import asyncio
from typing import List
from datetime import datetime
import praw
from prawcore.exceptions import ResponseException
from src.collectors.base import BaseCollector, PostData
from src.utils.logger_config import get_collector_logger


class RedditCollector(BaseCollector):
    """Collects posts from Reddit using PRAW."""

    def __init__(self, config: dict):
        """
        Initialize Reddit collector.

        Args:
            config: Dictionary containing Reddit credentials (client_id, client_secret, user_agent)
        """
        super().__init__(config)
        self.logger = get_collector_logger("reddit")
        self.client_id = config.get("REDDIT_CLIENT_ID")
        self.client_secret = config.get("REDDIT_CLIENT_SECRET")
        self.user_agent = config.get("REDDIT_USER_AGENT", "trendpulse/1.0")

        if not all([self.client_id, self.client_secret]):
            raise ValueError("Reddit credentials not configured")

        # Initialize PRAW in sync mode (we'll run in thread pool)
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=self.user_agent,
            read_only=True,
        )

    async def search(
        self, keyword: str, language: str = "en", limit: int = 50
    ) -> List[PostData]:
        """
        Search Reddit for posts containing the keyword.

        Args:
            keyword: Search query
            language: Not used by Reddit (kept for interface consistency)
            limit: Maximum number of posts to collect

        Returns:
            List of PostData objects
        """
        loop = asyncio.get_event_loop()
        posts = await loop.run_in_executor(
            None, lambda: self._search_sync(keyword, limit)
        )
        return posts

    def _search_sync(self, keyword: str, limit: int) -> List[PostData]:
        """
        Synchronous Reddit search (runs in thread pool).

        Args:
            keyword: Search query
            limit: Maximum number of posts

        Returns:
            List of PostData objects
        """
        posts = []

        try:
            # Search across all subreddits
            results = self.reddit.subreddit("all").search(
                keyword, sort="relevance", limit=limit
            )

            for submission in results:
                # Filter spam
                if self.is_spam(submission.title + " " + submission.selftext):
                    continue

                # Combine title and content
                content = f"{submission.title}\n\n{submission.selftext}"
                content = self.clean_content(content)

                post = PostData(
                    platform="reddit",
                    post_id=submission.id,
                    author=str(submission.author) if submission.author else "[deleted]",
                    content=content,
                    url=f"https://reddit.com{submission.permalink}",
                    upvotes=submission.score,
                    comments_count=submission.num_comments,
                    created_at=datetime.fromtimestamp(submission.created_utc).isoformat(),
                )
                posts.append(post)

        except ResponseException as e:
            self.logger.error(f"Reddit API error: {e}")
        except Exception as e:
            self.logger.error(f"Error searching Reddit: {e}")

        return posts

    async def search_subreddit(
        self, subreddit: str, keyword: str, limit: int = 50
    ) -> List[PostData]:
        """
        Search within a specific subreddit.

        Args:
            subreddit: Subreddit name (e.g., 'technology')
            keyword: Search query
            limit: Maximum number of posts

        Returns:
            List of PostData objects
        """
        loop = asyncio.get_event_loop()
        posts = await loop.run_in_executor(
            None, lambda: self._search_subreddit_sync(subreddit, keyword, limit)
        )
        return posts

    def _search_subreddit_sync(
        self, subreddit: str, keyword: str, limit: int
    ) -> List[PostData]:
        """
        Synchronous subreddit-specific search.

        Args:
            subreddit: Subreddit name
            keyword: Search query
            limit: Maximum number of posts

        Returns:
            List of PostData objects
        """
        posts = []

        try:
            sub = self.reddit.subreddit(subreddit)
            results = sub.search(keyword, sort="relevance", limit=limit)

            for submission in results:
                if self.is_spam(submission.title + " " + submission.selftext):
                    continue

                content = f"{submission.title}\n\n{submission.selftext}"
                content = self.clean_content(content)

                post = PostData(
                    platform="reddit",
                    post_id=submission.id,
                    author=str(submission.author) if submission.author else "[deleted]",
                    content=content,
                    url=f"https://reddit.com{submission.permalink}",
                    upvotes=submission.score,
                    comments_count=submission.num_comments,
                    created_at=datetime.fromtimestamp(submission.created_utc).isoformat(),
                )
                posts.append(post)

        except Exception as e:
            self.logger.error(f"Error searching subreddit {subreddit}: {e}")

        return posts
