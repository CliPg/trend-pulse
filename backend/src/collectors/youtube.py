"""
YouTube data collector using YouTube Data API v3.
Collects video metadata and transcripts based on keyword search.
"""
import asyncio
import os
import functools
import random
from typing import List, Optional
import aiohttp
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig, WebshareProxyConfig
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from src.collectors.base import BaseCollector, PostData


class YouTubeCollector(BaseCollector):
    """Collects YouTube video metadata and transcripts."""

    def __init__(self, config: dict):
        """
        Initialize YouTube collector.

        Args:
            config: Dictionary containing YouTube API key
        """
        super().__init__(config)
        self.api_key = config.get("YOUTUBE_API_KEY")

        if not self.api_key:
            raise ValueError("YouTube API key not configured")

        self.base_url = "https://www.googleapis.com/youtube/v3"

        # Configure timeout (longer for China network conditions)
        self.timeout = aiohttp.ClientTimeout(
            total=60,  # 60 seconds total
            connect=30,  # 30 seconds to connect
            sock_read=30  # 30 seconds to read data
        )

        # Get proxy from environment variable
        self.proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        self.proxy_config = self._create_proxy_config()

    def _create_proxy_config(self) -> Optional[GenericProxyConfig | WebshareProxyConfig]:
        """
        Create proxy configuration for YouTubeTranscriptApi.

        Supports multiple proxy types:
        1. Webshare residential proxies (recommended for production)
        2. Generic HTTP/HTTPS proxies (for local development)

        Priority: Webshare > Generic HTTP_PROXY

        Returns:
            GenericProxyConfig or WebshareProxyConfig if proxy is set, None otherwise
        """
        # Priority 1: Check for Webshare proxy configuration
        webshare_username = os.getenv("WEBSHARE_PROXY_USERNAME")
        webshare_password = os.getenv("WEBSHARE_PROXY_PASSWORD")

        if webshare_username and webshare_password:
            print("✓ Using Webshare residential proxy")
            return WebshareProxyConfig(
                proxy_username=webshare_username,
                proxy_password=webshare_password,
            )

        # Priority 2: Check for generic HTTP/HTTPS proxy
        http_proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
        if http_proxy:
            print(f"✓ Using generic proxy: {http_proxy}")
            # Use the same proxy for both HTTP and HTTPS
            return GenericProxyConfig(
                http_url=http_proxy,
                https_url=http_proxy,
            )

        # No proxy configured
        return None

    async def search(
        self, keyword: str, language: str = "en", limit: int = 50
    ) -> List[PostData]:
        """
        Search YouTube for videos and retrieve transcripts.

        Args:
            keyword: Search query
            language: Language code for transcript preference
            limit: Maximum number of videos

        Returns:
            List of PostData objects with transcripts as content
        """
        # Conservative limits to avoid IP blocking
        actual_limit = min(limit, 5)  # Reduced from 10 to 5

        print(f"🔍 Searching for videos with keyword: '{keyword}'")
        print(f"📊 Limit: {actual_limit} videos (conservative mode to avoid IP blocking)")
        print()

        # Step 1: Search for videos
        videos = await self._search_videos(keyword, actual_limit)

        if not videos:
            print("⚠️  No videos found")
            return []

        print(f"📺 Found {len(videos)} videos, fetching transcripts...")
        print(f"⏱️  Using conservative delays (3-6 seconds between requests) to avoid IP blocking")
        print()

        # Print video URLs for reference
        print("📋 Video URLs:")
        for i, video in enumerate(videos, 1):
            url = f"https://youtube.com/watch?v={video['id']}"
            title = video.get('title', 'Unknown')[:50]
            print(f"  {i}. {title}...")
            print(f"     {url}")
        print()

        # Add initial random delay before starting
        initial_delay = random.uniform(2, 4)
        print(f"⏳ Waiting {initial_delay:.1f} seconds before starting...")
        await asyncio.sleep(initial_delay)

        # Step 2: Fetch transcripts sequentially (to avoid IP blocking)
        posts = []
        for i, video in enumerate(videos, 1):
            url = f"https://youtube.com/watch?v={video['id']}"
            print(f"  [{i}/{len(videos)}] Fetching transcript for {video['id']}...")

            try:
                result = await self._fetch_transcript(video, language)

                if result:  # Transcript found
                    post = PostData(
                        platform="youtube",
                        post_id=video["id"],
                        author=video["channel_title"],
                        content=result,
                        url=url,
                        likes=video.get("like_count", 0),
                        comments_count=video.get("comment_count", 0),
                        created_at=video.get("published_at"),
                    )
                    posts.append(post)
                    print(f"    ✓ Success (transcript length: {len(result)} chars)")
                else:
                    print(f"    ⚠️  No transcript available")

                # Add random delay between requests (3-6 seconds) to avoid IP blocking
                if i < len(videos):
                    delay = random.uniform(3, 6)
                    print(f"    ⏳ Waiting {delay:.1f} seconds before next request...")
                    await asyncio.sleep(delay)

            except Exception as e:
                print(f"    ✗ Failed: {str(e)[:100]}")
                # Add extra delay on error
                error_delay = random.uniform(5, 8)
                print(f"    ⏳ Waiting {error_delay:.1f} seconds due to error...")
                await asyncio.sleep(error_delay)
                continue

        print()
        print(f"✅ Completed! Successfully fetched {len(posts)}/{len(videos)} transcripts")
        return posts

    async def _search_videos(self, keyword: str, limit: int) -> List[dict]:
        """
        Search YouTube API for videos.

        Args:
            keyword: Search query
            limit: Maximum number of videos

        Returns:
            List of video metadata dictionaries
        """
        url = f"{self.base_url}/search"
        params = {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": limit,
            "order": "relevance",
            "key": self.api_key,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    url,
                    params=params,
                    proxy=self.proxy
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"YouTube API error: {error_text}")

                    data = await response.json()

            # Extract video IDs and fetch detailed statistics
            video_ids = [item["id"]["videoId"] for item in data["items"]]
            videos_with_stats = await self._fetch_video_stats(video_ids)

            return videos_with_stats

        except asyncio.TimeoutError:
            print("⏱️  YouTube API timeout - check your network connection or proxy")
            return []
        except Exception as e:
            print(f"❌ YouTube API error: {e}")
            return []

    async def _fetch_video_stats(self, video_ids: List[str]) -> List[dict]:
        """
        Fetch detailed statistics for videos.

        Args:
            video_ids: List of YouTube video IDs

        Returns:
            List of video metadata with statistics
        """
        url = f"{self.base_url}/videos"
        params = {
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": self.api_key,
        }

        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(
                    url,
                    params=params,
                    proxy=self.proxy
                ) as response:
                    if response.status != 200:
                        return []

                    data = await response.json()

            videos = []
            for item in data.get("items", []):
                videos.append(
                    {
                        "id": item["id"],
                        "title": item["snippet"]["title"],
                        "channel_title": item["snippet"]["channelTitle"],
                        "published_at": item["snippet"]["publishedAt"],
                        "like_count": int(item["statistics"].get("likeCount", 0)),
                        "comment_count": int(item["statistics"].get("commentCount", 0)),
                        "view_count": int(item["statistics"].get("viewCount", 0)),
                    }
                )

            return videos

        except asyncio.TimeoutError:
            print("⏱️  YouTube API timeout while fetching video stats")
            return []
        except Exception as e:
            print(f"❌ Error fetching video stats: {e}")
            return []

    async def _fetch_transcript(self, video: dict, language: str) -> str | None:
        """
        Fetch transcript for a video.

        Args:
            video: Video metadata dictionary
            language: Preferred language code

        Returns:
            Transcript text or None if not available
        """
        video_id = video["id"]
        loop = asyncio.get_event_loop()

        try:
            # Create API instance with proxy config if available
            if self.proxy_config:
                # Print proxy info (already printed in __init__, so this is just for debug)
                api = YouTubeTranscriptApi(proxy_config=self.proxy_config)
            else:
                print("    ⚠️  No proxy configured - may encounter IP blocking")
                api = YouTubeTranscriptApi()

            # Use functools.partial to bind the video_id parameter
            # Pass languages parameter for better compatibility
            fetch_transcript_func = functools.partial(
                api.fetch, video_id, languages=[language]
            )

            # Run in thread pool to avoid blocking
            transcript = await loop.run_in_executor(
                None, fetch_transcript_func
            )

            # Extract text from transcript snippets
            # FetchedTranscript object contains snippets list with text, start, duration
            text = " ".join([snippet.text for snippet in transcript.snippets])
            text = self.clean_content(text)

            return text

        except (TranscriptsDisabled, NoTranscriptFound):
            # No transcript available
            return None
        except VideoUnavailable:
            # Video deleted or private
            return None
        except Exception as e:
            # Check for IP blocking errors
            print(f"    ✗ Error fetching transcript: {str(e)}")
            error_str = str(e).lower()
            if "ip blocked" in error_str or "requestblocked" in error_str or "ipblocked" in error_str:
                print(f"    ⚠️  YouTube IP blocking detected!")
                print(f"    💡 Solution: Configure proxy in .env file:")
                print(f"       # Option 1: Webshare residential proxy (recommended)")
                print(f"       WEBSHARE_PROXY_USERNAME=your_username")
                print(f"       WEBSHARE_PROXY_PASSWORD=your_password")
                print(f"       # Option 2: Generic HTTP proxy")
                print(f"       HTTP_PROXY=http://127.0.0.1:7890")
            return None
