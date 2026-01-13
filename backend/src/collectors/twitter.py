"""
X/Twitter data collector using Playwright headless browser.
This method doesn't require API access but is more fragile than official API.
"""
import asyncio
from typing import List
from playwright.async_api import async_playwright, Page
from src.collectors.base import BaseCollector, PostData


class TwitterCollector(BaseCollector):
    """Collects tweets using Playwright (no API required)."""

    def __init__(self, config: dict):
        """
        Initialize Twitter collector.

        Args:
            config: Dictionary with optional bearer_token (if using official API)
        """
        super().__init__(config)
        self.bearer_token = config.get("TWITTER_BEARER_TOKEN")

        # Anti-detection settings
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    async def search(
        self, keyword: str, language: str = "en", limit: int = 50
    ) -> List[PostData]:
        """
        Search X/Twitter using Playwright.

        Warning: This method is fragile and may break due to Twitter's
        anti-bot measures. Consider using official API if available.

        Args:
            keyword: Search query
            language: Language code
            limit: Maximum number of tweets

        Returns:
            List of PostData objects
        """
        async with async_playwright() as p:
            # Launch browser with anti-detection settings
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                ],
            )

            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={"width": 1920, "height": 1080},
            )

            page = await context.new_page()

            # Navigate to Twitter search
            search_url = f"https://twitter.com/search?q={keyword}&src=typed_query"
            try:
                await page.goto(search_url, wait_until="networkidle", timeout=15000)

                # Wait for content to load
                await asyncio.sleep(3)

                # Extract tweets
                posts = await self._extract_tweets(page, limit)

            except Exception as e:
                print(f"Error navigating to Twitter: {e}")
                posts = []

            finally:
                await browser.close()

            return posts

    async def _extract_tweets(self, page: Page, limit: int) -> List[PostData]:
        """
        Extract tweet data from page.

        Args:
            page: Playwright page object
            limit: Maximum number of tweets

        Returns:
            List of PostData objects
        """
        posts = []

        try:
            # Scroll to load more tweets
            for _ in range(3):  # Scroll 3 times
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

            # Extract tweet elements
            tweets = await page.query_selector_all('[data-testid="tweet"]')

            for tweet in tweets[:limit]:
                try:
                    # Extract tweet text
                    text_element = await tweet.query_selector('[data-testid="tweetText"]')
                    if not text_element:
                        continue

                    text = await text_element.inner_text()

                    # Extract author
                    author_element = await tweet.query_selector('[data-testid="User-Name"]')
                    author = await author_element.inner_text() if author_element else "Unknown"

                    # Extract tweet URL
                    tweet_url = ""
                    link_element = await tweet.query_selector('time')
                    if link_element:
                        parent = await link_element.evaluate("el => el.closest('a').href")
                        tweet_url = parent

                    # Extract engagement metrics
                    metrics = await self._extract_metrics(tweet)

                    # Filter spam
                    if self.is_spam(text):
                        continue

                    post = PostData(
                        platform="twitter",
                        post_id=str(hash(text)),  # Simple ID generation
                        author=author,
                        content=self.clean_content(text),
                        url=tweet_url,
                        shares=metrics.get("retweets", 0),
                        likes=metrics.get("likes", 0),
                        comments_count=metrics.get("replies", 0),
                    )
                    posts.append(post)

                except Exception as e:
                    print(f"Error extracting tweet: {e}")
                    continue

        except Exception as e:
            print(f"Error extracting tweets: {e}")

        return posts

    async def _extract_metrics(self, tweet) -> dict:
        """
        Extract engagement metrics from tweet.

        Args:
            tweet: Tweet element

        Returns:
            Dictionary with metrics
        """
        metrics = {}

        try:
            # This is fragile and may break - selectors change frequently
            like_element = await tweet.query_selector('[data-testid="like"]')
            if like_element:
                like_text = await like_element.inner_text()
                metrics["likes"] = self._parse_metric(like_text)

            retweet_element = await tweet.query_selector('[data-testid="retweet"]')
            if retweet_element:
                retweet_text = await retweet_element.inner_text()
                metrics["retweets"] = self._parse_metric(retweet_text)

            reply_element = await tweet.query_selector('[data-testid="reply"]')
            if reply_element:
                reply_text = await reply_element.inner_text()
                metrics["replies"] = self._parse_metric(reply_text)

        except Exception as e:
            print(f"Error extracting metrics: {e}")

        return metrics

    def _parse_metric(self, text: str) -> int:
        """
        Parse metric text like '10.5K' to integer.

        Args:
            text: Metric text

        Returns:
            Integer value
        """
        text = text.strip().upper()

        if "K" in text:
            return int(float(text.replace("K", "")) * 1000)
        elif "M" in text:
            return int(float(text.replace("M", "")) * 1000000)
        else:
            try:
                return int(text)
            except ValueError:
                return 0
