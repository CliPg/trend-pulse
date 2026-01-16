"""
X/Twitter data collector using Selenium headless browser.
This method doesn't require API access but is more fragile than official API.
"""
import asyncio
import time
import os
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.collectors.base import BaseCollector, PostData


class TwitterCollector(BaseCollector):
    """Collects tweets using Selenium (no API required)."""

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
        Search X/Twitter using Selenium.

        Warning: This method is fragile and may break due to Twitter's
        anti-bot measures. Consider using official API if available.

        Args:
            keyword: Search query
            language: Language code
            limit: Maximum number of tweets

        Returns:
            List of PostData objects
        """
        # Run synchronous Selenium code in executor
        loop = asyncio.get_event_loop()
        posts = await loop.run_in_executor(None, self._search_sync, keyword, language, limit)
        return posts

    def _search_sync(
        self, keyword: str, language: str, limit: int
    ) -> List[PostData]:
        """
        Synchronous search implementation using Selenium.

        Args:
            keyword: Search query
            language: Language code
            limit: Maximum number of tweets

        Returns:
            List of PostData objects
        """
        driver = None
        posts = []

        try:
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument(f"user-agent={self.user_agent}")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")

            # Run in headless mode (unless SHOW_BROWSER env var is set for debugging)
            # show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"
            show_browser = True
            if not show_browser:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-extensions")

            # Exclude automation flags
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)

            # Execute CDP commands to hide webdriver property
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            })

            # Navigate to Twitter search
            search_url = f"https://x.com/search?q={keyword}&src=typed_query"
            driver.get(search_url)

            # Wait for page to load
            time.sleep(5)

            # Extract tweets
            posts = self._extract_tweets(driver, limit)

        except Exception as e:
            print(f"Error navigating to Twitter: {e}")
            posts = []

        finally:
            if driver:
                driver.quit()

        return posts

    def _extract_tweets(self, driver, limit: int) -> List[PostData]:
        """
        Extract tweet data from page.

        Args:
            driver: Selenium WebDriver instance
            limit: Maximum number of tweets

        Returns:
            List of PostData objects
        """
        posts = []

        try:
            # Scroll to load more tweets
            for _ in range(3):  # Scroll 3 times
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Extract tweet elements
            tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

            for tweet in tweets[:limit]:
                try:
                    # Extract tweet text
                    try:
                        text_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                        text = text_element.text
                    except NoSuchElementException:
                        continue

                    # Extract author
                    try:
                        author_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                        author = author_element.text
                    except NoSuchElementException:
                        author = "Unknown"

                    # Extract tweet URL
                    tweet_url = ""
                    try:
                        link_element = tweet.find_element(By.TAG_NAME, 'time')
                        tweet_url = link_element.find_element(By.XPATH, "..").get_attribute('href')
                    except NoSuchElementException:
                        pass

                    # Extract engagement metrics
                    metrics = self._extract_metrics(tweet)

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

    def _extract_metrics(self, tweet) -> dict:
        """
        Extract engagement metrics from tweet.

        Args:
            tweet: Tweet WebElement

        Returns:
            Dictionary with metrics
        """
        metrics = {}

        try:
            # This is fragile and may break - selectors change frequently
            try:
                like_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="like"]')
                like_text = like_element.text
                metrics["likes"] = self._parse_metric(like_text)
            except NoSuchElementException:
                pass

            try:
                retweet_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]')
                retweet_text = retweet_element.text
                metrics["retweets"] = self._parse_metric(retweet_text)
            except NoSuchElementException:
                pass

            try:
                reply_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
                reply_text = reply_element.text
                metrics["replies"] = self._parse_metric(reply_text)
            except NoSuchElementException:
                pass

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
