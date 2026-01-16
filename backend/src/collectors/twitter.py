"""
X/Twitter data collector using Selenium headless browser.
This method doesn't require API access but is more fragile than official API.

Improved with:
- Automatic ChromeDriver management via webdriver_manager
- User profile persistence for login state
- Smart scrolling with bottom detection
- Enhanced anti-detection measures
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
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote
from src.collectors.base import BaseCollector, PostData


class TwitterCollector(BaseCollector):
    """Collects tweets using Selenium (no API required)."""

    def __init__(self, config: dict = None):
        """
        Initialize Twitter collector.

        Args:
            config: Dictionary with optional bearer_token (if using official API)
        """
        # Initialize base collector (config not used but required for consistency)
        if config is None:
            config = {}
        super().__init__(config)

        # Anti-detection settings
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/143.0.0.0 Safari/537.36"
        )

        # User data directory for persisting login state
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_profile")

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
            print(f"[Twitter] 正在初始化浏览器...")
            driver = self._launch_chrome_browser()

            print(f"[Twitter] 正在搜索关键词: {keyword}")
            search_url = f"https://x.com/search?q={quote(keyword)}&src=typed_query&lang={language}"
            print(f"[Twitter] 搜索 URL: {search_url}")
            driver.get(search_url)

            # Wait for page to load
            print(f"[Twitter] 等待页面加载...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
                )
                print(f"[Twitter] 搜索结果已加载")
            except TimeoutException:
                print(f"[Twitter] 等待搜索结果超时，尝试继续...")

            time.sleep(3)

            # Extract tweets
            posts = self._extract_tweets(driver, limit)

        except Exception as e:
            print(f"[Twitter] Error during search: {e}")
            posts = []

        finally:
            if driver:
                print(f"[Twitter] 关闭浏览器...")
                driver.quit()

        return posts

    def _launch_chrome_browser(self):
        """
        Launch Chrome browser with anti-detection settings.

        Returns:
            Selenium WebDriver instance
        """
        chrome_options = Options()

        # User data directory for persisting login state
        print(f"[Twitter] 使用用户数据目录: {self.user_data_dir}")
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")

        # headless mode
        chrome_options.add_argument("--headless")

        # Anti-detection configuration
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Set real User-Agent
        chrome_options.add_argument(f"--user-agent={self.user_agent}")

        # Stability options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-infobars")

        # Window size
        chrome_options.add_argument("--window-size=1920,1080")

        # Run in headless mode (unless SHOW_BROWSER env var is set for debugging)
        # show_browser = os.getenv("SHOW_BROWSER", "false").lower() == "true"
        # if not show_browser:
        #     chrome_options.add_argument("--headless")

        print(f"[Twitter] 正在启动浏览器...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Execute CDP commands to hide webdriver property
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })

        return driver

    def _extract_tweets(self, driver, limit: int) -> List[PostData]:
        """
        Extract tweet data from page with smart scrolling.

        Args:
            driver: Selenium WebDriver instance
            limit: Maximum number of tweets

        Returns:
            List of PostData objects
        """
        posts = []
        last_height = 0

        print(f"[Twitter] 开始爬取前 {limit} 条推文...")

        while len(posts) < limit:
            # Find all tweet elements
            tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

            # Process new tweets
            for tweet_element in tweet_elements[len(posts):limit]:
                try:
                    # Extract tweet text
                    try:
                        text_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                        text = text_element.text
                    except NoSuchElementException:
                        continue

                    # Extract author information
                    try:
                        author_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                        author = author_element.text.split('\n')[0]  # Get only the username
                    except NoSuchElementException:
                        author = "未知用户"

                    # Extract timestamp
                    timestamp = None
                    try:
                        time_element = tweet_element.find_element(By.TAG_NAME, 'time')
                        timestamp = time_element.get_attribute('datetime')
                    except NoSuchElementException:
                        pass

                    # Extract tweet URL
                    tweet_url = ""
                    try:
                        link_element = tweet_element.find_element(By.TAG_NAME, 'time')
                        tweet_url = link_element.find_element(By.XPATH, "..").get_attribute('href')
                    except NoSuchElementException:
                        pass

                    # Extract engagement metrics
                    metrics = self._extract_metrics(tweet_element)

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
                        created_at=timestamp
                    )
                    posts.append(post)

                    print(f"[Twitter] 已爬取 {len(posts)}/{limit} 条推文")

                except Exception as e:
                    print(f"[Twitter] 提取推文时出错: {e}")
                    continue

            if len(posts) >= limit:
                break

            # Scroll to load more tweets
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # Check if reached bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print(f"[Twitter] 已到达页面底部")
                break
            last_height = new_height

        print(f"[Twitter] 爬取完成！共获取 {len(posts)} 条推文")
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
            # Extract likes
            try:
                like_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="like"]')
                like_text = like_element.text
                metrics["likes"] = self._parse_metric(like_text)
            except NoSuchElementException:
                metrics["likes"] = 0

            # Extract retweets
            try:
                retweet_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="retweet"]')
                retweet_text = retweet_element.text
                metrics["retweets"] = self._parse_metric(retweet_text)
            except NoSuchElementException:
                metrics["retweets"] = 0

            # Extract replies
            try:
                reply_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
                reply_text = reply_element.text
                metrics["replies"] = self._parse_metric(reply_text)
            except NoSuchElementException:
                metrics["replies"] = 0

        except Exception as e:
            print(f"[Twitter] 提取指标时出错: {e}")

        return metrics

    def _parse_metric(self, text: str) -> int:
        """
        Parse metric text like '10.5K' to integer.

        Args:
            text: Metric text

        Returns:
            Integer value
        """
        if not text:
            return 0

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
