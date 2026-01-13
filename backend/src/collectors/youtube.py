"""
YouTube data collector using YouTube Data API v3.
Collects video metadata and transcripts based on keyword search.
"""
import asyncio
from typing import List
import aiohttp
from youtube_transcript_api import YouTubeTranscriptApi
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
        # Step 1: Search for videos
        videos = await self._search_videos(keyword, limit)

        # Step 2: Fetch transcripts concurrently
        posts = []
        tasks = [self._fetch_transcript(video, language) for video in videos]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for video, result in zip(videos, results):
            if isinstance(result, Exception):
                print(f"Error fetching transcript for {video['id']}: {result}")
                continue

            if result:  # Transcript found
                post = PostData(
                    platform="youtube",
                    post_id=video["id"],
                    author=video["channel_title"],
                    content=result,
                    url=f"https://youtube.com/watch?v={video['id']}",
                    likes=video.get("like_count", 0),
                    comments_count=video.get("comment_count", 0),
                    created_at=video.get("published_at"),
                )
                posts.append(post)

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

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"YouTube API error: {error_text}")

                data = await response.json()

        # Extract video IDs and fetch detailed statistics
        video_ids = [item["id"]["videoId"] for item in data["items"]]
        videos_with_stats = await self._fetch_video_stats(video_ids)

        return videos_with_stats

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

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
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
            # Run YouTubeTranscriptApi in thread pool
            transcript = await loop.run_in_executor(
                None, YouTubeTranscriptApi.get_transcript, video_id
            )

            # Combine transcript segments
            text = " ".join([entry["text"] for entry in transcript])
            text = self.clean_content(text)

            return text

        except (TranscriptsDisabled, NoTranscriptFound):
            # No transcript available
            return None
        except VideoUnavailable:
            # Video deleted or private
            return None
        except Exception as e:
            print(f"Error fetching transcript: {e}")
            return None
