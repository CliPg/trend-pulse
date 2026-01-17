"""
Reddit data collector using Selenium headless browser.
This method doesn't require API access and works without PRAW credentials.

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
from src.utils.logger_config import get_collector_logger


class RedditCollector(BaseCollector):
    """Collects posts from Reddit using Selenium (no API required)."""

    def __init__(self, config: dict = None):
        """
        Initialize Reddit collector.

        Args:
            config: Dictionary with optional credentials (not required for Selenium)
        """
        # Initialize base collector (config not used but required for consistency)
        if config is None:
            config = {}
        super().__init__(config)
        self.logger = get_collector_logger("reddit")

        # Anti-detection settings
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/143.0.0.0 Safari/537.36"
        )

        # User data directory for persisting login state
        self.user_data_dir = os.path.join(os.getcwd(), "chrome_profile")

        # Configuration: whether to fetch full post content
        self.fetch_full_content = config.get("REDDIT_FETCH_FULL_CONTENT", True)

    async def search(
        self, keyword: str, language: str = "en", limit: int = 50
    ) -> List[PostData]:
        """
        Search Reddit using Selenium.

        Warning: This method uses web scraping and may break due to Reddit's
        structure changes. Consider using official API if available.

        Args:
            keyword: Search query
            language: Not used by Reddit (kept for interface consistency)
            limit: Maximum number of posts

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
            language: Language code (not used for Reddit)
            limit: Maximum number of posts

        Returns:
            List of PostData objects
        """
        driver = None
        posts = []

        try:
            self.logger.info("Initializing browser...")
            driver = self._launch_chrome_browser()

            self.logger.info(f"Searching for keyword: {keyword}")
            search_url = f"https://www.reddit.com/search/?q={quote(keyword)}&type=posts"
            self.logger.debug(f"Search URL: {search_url}")
            driver.get(search_url)

            # Wait for page to load
            self.logger.info("Waiting for page to load...")
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="search-post-unit"]'))
                )
                self.logger.info("Search results loaded")
            except TimeoutException:
                self.logger.warning("Timeout waiting for search results, trying to continue...")

            time.sleep(3)

            # Extract posts
            posts = self._extract_posts(driver, limit)

        except Exception as e:
            self.logger.error(f"Error during search: {e}")
            posts = []

        finally:
            if driver:
                self.logger.info("Closing browser...")
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
        self.logger.debug(f"Using user data directory: {self.user_data_dir}")
        chrome_options.add_argument(f"--user-data-dir={self.user_data_dir}")

        # Headless mode
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

        self.logger.info("Launching browser...")
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

    def _fetch_post_content(self, driver, post_url: str) -> str:
        """
        Fetch full content from a post detail page using optimized selectors.

        Based on diagnostic results, Reddit uses Shadow DOM with slot-based content.
        The best selector is [slot="text-body"] which captures the post body.

        Args:
            driver: Selenium WebDriver instance
            post_url: URL of the post to fetch content from

        Returns:
            Full post content text, or empty string if failed
        """
        if not post_url or not self.fetch_full_content:
            return ""

        original_url = driver.current_url
        content = ""

        try:
            self.logger.debug(f"Fetching content from: {post_url}")
            driver.get(post_url)

            # Wait for page to load
            time.sleep(3)

            # Optimized selectors based on diagnostic results
            # Priority: text-body slot > md class > fallback to full post
            content_selectors = [
                '[slot="text-body"]',  # Best: directly targets post body slot
                'div[slot="text-body"]',  # Alternative: div with text-body slot
                '.md',  # Fallback: markdown content class
            ]

            for i, selector in enumerate(content_selectors, 1):
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)

                    if elements:
                        # Get the first element with substantial content
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) > 20:  # Minimum content length
                                content = text
                                self.logger.info(f"Fetched {len(content)} chars.")
                                break

                        if content:
                            break
                    else:
                        self.logger.debug(f"Selector #{i} found no elements: {selector}")

                except Exception as e:
                    self.logger.debug(f"Selector #{i} failed: {e}")
                    continue

            if not content:
                self.logger.warning(f"⚠️  Could not extract substantial content from {post_url}")

        except Exception as e:
            self.logger.error(f"Error fetching post content: {e}")
        finally:
            # Always return to the original page
            try:
                driver.get(original_url)
                time.sleep(2)
            except Exception as e:
                self.logger.debug(f"Error returning to original page: {e}")

        return content

    def _extract_posts(self, driver, limit: int) -> List[PostData]:
        """
        Extract post data from page with smart scrolling.

        Args:
            driver: Selenium WebDriver instance
            limit: Maximum number of posts

        Returns:
            List of PostData objects
        """
        # Phase 1: Collect post URLs and basic info from search page
        posts_info = []
        seen_post_ids = set()
        last_height = 0
        max_scrolls = 20
        scroll_count = 0

        self.logger.info(f"Phase 1: Collecting post URLs and basic info...")

        while len(posts_info) < limit and scroll_count < max_scrolls:
            # Find all post elements
            post_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="search-post-unit"], [data-testid="search-post-with-content-preview"]')

            self.logger.info(f"Scroll {scroll_count + 1}: Found {len(post_elements)} post elements")

            # Extract basic info (title, URL, etc.) - don't visit detail pages yet
            for post_element in post_elements:
                try:
                    # Extract title
                    title = ""
                    try:
                        title_element = post_element.find_element(By.CSS_SELECTOR, '[data-testid="post-title-text"]')
                        title = title_element.text
                    except NoSuchElementException:
                        continue

                    # Extract URL
                    post_url = ""
                    try:
                        link_element = post_element.find_element(By.CSS_SELECTOR, '[data-testid="post-title"]')
                        post_url = link_element.get_attribute('href')
                        if post_url and post_url.startswith('/'):
                            post_url = f"https://www.reddit.com{post_url}"
                    except NoSuchElementException:
                        pass

                    # Create unique ID
                    if post_url:
                        post_id = post_url
                    else:
                        # Extract subreddit for fallback ID
                        subreddit = "Unknown"
                        try:
                            subreddit_link = post_element.find_element(By.CSS_SELECTOR, 'a[href^="/r/"]')
                            subreddit = subreddit_link.text
                            if not subreddit:
                                subreddit = subreddit_link.get_attribute('href').split('/r/')[1].split('/')[0]
                        except NoSuchElementException:
                            pass
                        post_id = f"{subreddit}:{hash(title)}"

                    # Skip duplicates
                    if post_id in seen_post_ids:
                        continue
                    seen_post_ids.add(post_id)

                    # Extract other metadata
                    subreddit = "Unknown"
                    try:
                        subreddit_link = post_element.find_element(By.CSS_SELECTOR, 'a[href^="/r/"]')
                        subreddit = subreddit_link.text
                        if not subreddit:
                            subreddit = subreddit_link.get_attribute('href').split('/r/')[1].split('/')[0]
                    except NoSuchElementException:
                        pass

                    # Extract preview content
                    preview_content = ""
                    try:
                        content_element = post_element.find_element(By.CSS_SELECTOR, 'div.text-neutral-content-weak')
                        if content_element and 'search-counter-row' not in content_element.get_attribute('class'):
                            preview_content = content_element.text
                    except NoSuchElementException:
                        pass

                    # Extract upvotes and comments
                    upvotes = 0
                    comments_count = 0
                    try:
                        counter_row = post_element.find_element(By.CSS_SELECTOR, '[data-testid="search-counter-row"]')
                        counter_text = counter_row.text
                        if '票' in counter_text and '评论' in counter_text:
                            parts = counter_text.split('·')
                            if len(parts) >= 2:
                                upvotes_text = parts[0].replace('票', '').strip()
                                comments_text = parts[1].replace('条评论', '').strip()
                                upvotes = self._parse_metric(upvotes_text)
                                comments_count = self._parse_metric(comments_text)
                    except NoSuchElementException:
                        pass
                    except Exception as e:
                        self.logger.debug(f"Error parsing counter row: {e}")

                    # Extract timestamp
                    timestamp = None
                    try:
                        time_element = post_element.find_element(By.TAG_NAME, 'time')
                        timestamp = time_element.get_attribute('datetime')
                    except NoSuchElementException:
                        pass

                    # Store post info (as a dict, not PostData yet)
                    posts_info.append({
                        'post_id': post_id,
                        'title': title,
                        'post_url': post_url,
                        'subreddit': subreddit,
                        'preview_content': preview_content,
                        'upvotes': upvotes,
                        'comments_count': comments_count,
                        'timestamp': timestamp
                    })

                    if len(posts_info) >= limit:
                        break

                except Exception as e:
                    self.logger.error(f"Error extracting post info: {e}")
                    continue

            if len(posts_info) >= limit:
                break

            # Scroll to load more posts
            self.logger.debug("Scrolling to load more posts...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            scroll_count += 1

            # Check if reached bottom
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                self.logger.info("Reached page bottom")
                break
            last_height = new_height

        self.logger.info(f"Phase 1 complete! Collected {len(posts_info)} post URLs")

        # Phase 2: Fetch full content for each post (if enabled)
        posts = []

        if self.fetch_full_content:
            self.logger.info(f"Phase 2: Fetching content for {len(posts_info)} posts...")

            for i, post_info in enumerate(posts_info, 1):
                try:
                    self.logger.info(f"Fetching content for post {i}/{len(posts_info)}")

                    # Fetch full content from detail page
                    full_content = post_info['preview_content']
                    if post_info['post_url']:
                        full_content = self._fetch_post_content(driver, post_info['post_url'])

                        # Fallback to preview if full content fetch failed
                        if not full_content:
                            full_content = post_info['preview_content']

                    # Combine title and content
                    if full_content:
                        final_content = f"{post_info['title']}\n\n{full_content}"
                    else:
                        final_content = post_info['title']

                    # Final spam check
                    if self.is_spam(final_content):
                        continue

                    # Create PostData object
                    post = PostData(
                        platform="reddit",
                        post_id=str(post_info['post_id']),
                        author=f"r/{post_info['subreddit']}",
                        content=self.clean_content(final_content),
                        url=post_info['post_url'],
                        upvotes=post_info['upvotes'],
                        likes=0,
                        shares=0,
                        comments_count=post_info['comments_count'],
                        created_at=post_info['timestamp']
                    )

                    posts.append(post)
                    self.logger.info(f"Scraped {len(posts)}/{len(posts_info)} posts - r/{post_info['subreddit']}: {post_info['title'][:50]}")

                except Exception as e:
                    self.logger.error(f"Error processing post {i}: {e}")
                    continue
        else:
            # Skip fetching full content, just use preview
            self.logger.info(f"Phase 2: Using preview content only (full content fetching disabled)")

            for post_info in posts_info:
                try:
                    # Combine title and preview
                    if post_info['preview_content']:
                        final_content = f"{post_info['title']}\n\n{post_info['preview_content']}"
                    else:
                        final_content = post_info['title']

                    # Spam check
                    if self.is_spam(final_content):
                        continue

                    post = PostData(
                        platform="reddit",
                        post_id=str(post_info['post_id']),
                        author=f"r/{post_info['subreddit']}",
                        content=self.clean_content(final_content),
                        url=post_info['post_url'],
                        upvotes=post_info['upvotes'],
                        likes=0,
                        shares=0,
                        comments_count=post_info['comments_count'],
                        created_at=post_info['timestamp']
                    )

                    posts.append(post)

                except Exception as e:
                    self.logger.error(f"Error creating post: {e}")
                    continue

        self.logger.info(f"Scraping completed! Collected {len(posts)} posts")
        return posts

    def _parse_metric(self, text: str) -> int:
        """
        Parse metric text like '10.5K', '425', or '425 票' to integer.

        Args:
            text: Metric text

        Returns:
            Integer value
        """
        if not text:
            return 0

        text = text.strip().upper()

        # Remove Chinese characters
        text = text.replace('票', '').strip()
        text = text.replace('条评论', '').strip()

        # Handle "10.5K", "1.2M" format
        if "K" in text:
            return int(float(text.replace("K", "")) * 1000)
        elif "M" in text:
            return int(float(text.replace("M", "")) * 1000000)
        else:
            try:
                # Remove any non-numeric characters except minus sign and dot
                text = ''.join(c for c in text if c.isdigit() or c == '-' or c == '.')
                if text:
                    return int(float(text))
                return 0
            except ValueError:
                return 0
