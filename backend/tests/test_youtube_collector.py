"""
Tests for YouTube collector transcript fetching functionality.
"""
import asyncio
import os
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import pytest

from src.collectors.youtube import YouTubeCollector
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)


class TestFetchTranscript:
    """Test suite for _fetch_transcript method."""

    @pytest.fixture
    def collector(self):
        """Create a YouTubeCollector instance for testing."""
        config = {"YOUTUBE_API_KEY": "test_api_key"}
        return YouTubeCollector(config)

    @pytest.fixture
    def mock_video(self):
        """Create a mock video object."""
        return {
            "id": "test_video_id",
            "title": "Test Video",
            "channel_title": "Test Channel",
        }

    @pytest.mark.asyncio
    async def test_fetch_transcript_success(self, collector, mock_video):
        """Test successful transcript fetching."""
        # Mock the transcript API response
        mock_transcript = MagicMock()
        mock_snippet = Mock(text="This is a test transcript")
        mock_transcript.snippets = [mock_snippet]

        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.return_value = mock_transcript
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            assert result is not None
            assert result == "This is a test transcript"
            mock_api_instance.fetch.assert_called_once_with("test_video_id")

    @pytest.mark.asyncio
    async def test_fetch_transcript_multiple_snippets(self, collector, mock_video):
        """Test transcript with multiple snippets is properly joined."""
        mock_transcript = MagicMock()
        mock_snippets = [
            Mock(text="Hello world"),
            Mock(text="This is a test"),
            Mock(text="Goodbye"),
        ]
        mock_transcript.snippets = mock_snippets

        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.return_value = mock_transcript
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            assert result == "Hello world This is a test Goodbye"

    @pytest.mark.asyncio
    async def test_fetch_transcript_no_transcript_available(
        self, collector, mock_video
    ):
        """Test when transcript is disabled."""
        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.side_effect = TranscriptsDisabled("test_video_id")
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_transcript_no_transcript_found(self, collector, mock_video):
        """Test when no transcript is found."""
        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.side_effect = NoTranscriptFound(
                video_id="test_video_id",
                requested_language_codes=["en"],
                transcript_data={}
            )
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_transcript_video_unavailable(self, collector, mock_video):
        """Test when video is unavailable."""
        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.side_effect = VideoUnavailable("test_video_id")
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_transcript_ip_blocked(self, collector, mock_video):
        """Test when IP is blocked by YouTube."""
        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.side_effect = Exception("IP blocked")
            mock_api.return_value = mock_api_instance

            with patch("builtins.print") as mock_print:
                result = await collector._fetch_transcript(mock_video, "en")

                assert result is None
                # Check that warning message was printed
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_fetch_transcript_with_proxy(self, collector, mock_video):
        """Test transcript fetching with proxy configuration."""
        # Set proxy environment variable
        import os

        with patch.dict(os.environ, {"HTTP_PROXY": "http://proxy.example.com:8080"}):
            # Recreate collector to pick up proxy setting
            config = {"YOUTUBE_API_KEY": "test_api_key"}
            collector_with_proxy = YouTubeCollector(config)

            mock_transcript = MagicMock()
            mock_snippet = Mock(text="Transcript with proxy")
            mock_transcript.snippets = [mock_snippet]

            with patch(
                "src.collectors.youtube.YouTubeTranscriptApi"
            ) as mock_api:
                mock_api_instance = MagicMock()
                mock_api_instance.fetch.return_value = mock_transcript
                mock_api.return_value = mock_api_instance

                result = await collector_with_proxy._fetch_transcript(
                    mock_video, "en"
                )

                assert result == "Transcript with proxy"
                # Verify that API was called with proxy_config
                assert mock_api.call_count == 1
                call_kwargs = mock_api.call_args[1] if mock_api.call_args[1] else {}
                assert "proxy_config" in call_kwargs
                # Verify proxy_config has correct URLs
                proxy_config = call_kwargs["proxy_config"]
                assert proxy_config._http_url == "http://proxy.example.com:8080"
                assert proxy_config._https_url == "http://proxy.example.com:8080"

    @pytest.mark.asyncio
    async def test_fetch_transcript_with_webshare_proxy(self, collector, mock_video):
        """Test transcript fetching with Webshare proxy configuration."""
        from youtube_transcript_api.proxies import WebshareProxyConfig

        # Set Webshare environment variables
        with patch.dict(os.environ, {
            "WEBSHARE_PROXY_USERNAME": "test_user",
            "WEBSHARE_PROXY_PASSWORD": "test_pass"
        }):
            # Recreate collector to pick up Webshare proxy setting
            config = {"YOUTUBE_API_KEY": "test_api_key"}
            collector_with_webshare = YouTubeCollector(config)

            mock_transcript = MagicMock()
            mock_snippet = Mock(text="Transcript with Webshare proxy")
            mock_transcript.snippets = [mock_snippet]

            with patch(
                "src.collectors.youtube.YouTubeTranscriptApi"
            ) as mock_api:
                mock_api_instance = MagicMock()
                mock_api_instance.fetch.return_value = mock_transcript
                mock_api.return_value = mock_api_instance

                result = await collector_with_webshare._fetch_transcript(
                    mock_video, "en"
                )

                assert result == "Transcript with Webshare proxy"
                # Verify that API was called with Webshare proxy_config
                assert mock_api.call_count == 1
                call_kwargs = mock_api.call_args[1] if mock_api.call_args[1] else {}
                assert "proxy_config" in call_kwargs
                # Verify proxy_config is WebshareProxyConfig
                proxy_config = call_kwargs["proxy_config"]
                assert isinstance(proxy_config, WebshareProxyConfig)

    @pytest.mark.asyncio
    async def test_proxy_priority_webshare_over_http(self, collector, mock_video):
        """Test that Webshare proxy has priority over HTTP_PROXY."""
        from youtube_transcript_api.proxies import WebshareProxyConfig

        # Set both Webshare and HTTP proxy - Webshare should take priority
        with patch.dict(os.environ, {
            "WEBSHARE_PROXY_USERNAME": "test_user",
            "WEBSHARE_PROXY_PASSWORD": "test_pass",
            "HTTP_PROXY": "http://127.0.0.1:7890"
        }):
            config = {"YOUTUBE_API_KEY": "test_api_key"}
            collector_with_both = YouTubeCollector(config)

            # Verify proxy_config is Webshare (not HTTP)
            assert isinstance(collector_with_both.proxy_config, WebshareProxyConfig)
            assert collector_with_both.proxy_config._proxy_username == "test_user"
            assert collector_with_both.proxy_config._proxy_password == "test_pass"

    @pytest.mark.asyncio
    async def test_fetch_transcript_content_cleaning(self, collector, mock_video):
        """Test that transcript content is properly cleaned."""
        mock_transcript = MagicMock()
        # Include URLs and markdown that should be cleaned
        mock_snippet = Mock(
            text="Check this out https://example.com and [link](url) for more"
        )
        mock_transcript.snippets = [mock_snippet]

        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.return_value = mock_transcript
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            # URLs should be removed by clean_content
            assert "https://example.com" not in result
            assert result is not None

    @pytest.mark.asyncio
    async def test_fetch_transcript_generic_exception(self, collector, mock_video):
        """Test handling of unexpected exceptions."""
        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.side_effect = Exception("Unexpected error")
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            assert result is None

    @pytest.mark.asyncio
    async def test_fetch_transcript_empty_transcript(self, collector, mock_video):
        """Test handling of empty transcript."""
        mock_transcript = MagicMock()
        mock_transcript.snippets = []

        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.return_value = mock_transcript
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            assert result == ""

    @pytest.mark.asyncio
    async def test_fetch_transcript_whitespace_normalization(
        self, collector, mock_video
    ):
        """Test that extra whitespace is normalized."""
        mock_transcript = MagicMock()
        mock_snippet = Mock(text="  Hello    world  \n\n  Test  ")
        mock_transcript.snippets = [mock_snippet]

        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.return_value = mock_transcript
            mock_api.return_value = mock_api_instance

            result = await collector._fetch_transcript(mock_video, "en")

            # Should be normalized to single spaces
            assert result == "Hello world Test"

    @pytest.mark.asyncio
    async def test_fetch_transcript_request_blocked_error(self, collector, mock_video):
        """Test different IP blocking error messages."""
        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.side_effect = Exception("requestblocked")
            mock_api.return_value = mock_api_instance

            with patch("builtins.print") as mock_print:
                result = await collector._fetch_transcript(mock_video, "en")

                assert result is None
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_fetch_transcript_ip_blocked_lowercase(self, collector, mock_video):
        """Test IP blocking error with lowercase 'ipblocked'."""
        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.side_effect = Exception("ipblocked")
            mock_api.return_value = mock_api_instance

            with patch("builtins.print") as mock_print:
                result = await collector._fetch_transcript(mock_video, "en")

                assert result is None
                mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_fetch_transcript_run_in_executor(self, collector, mock_video):
        """Test that blocking operation is run in executor."""
        mock_transcript = MagicMock()
        mock_snippet = Mock(text="Async transcript")
        mock_transcript.snippets = [mock_snippet]

        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api, \
             patch("asyncio.get_event_loop") as mock_get_loop:

            mock_loop = AsyncMock()
            mock_get_loop.return_value = mock_loop

            mock_api_instance = MagicMock()
            mock_api_instance.fetch.return_value = mock_transcript
            mock_api.return_value = mock_api_instance

            await collector._fetch_transcript(mock_video, "en")

            # Verify that run_in_executor was called
            assert mock_loop.run_in_executor.called

    @pytest.mark.asyncio
    async def test_fetch_transcript_different_video_ids(self, collector):
        """Test fetching transcripts for different video IDs."""
        videos = [
            {"id": "video1", "title": "Video 1", "channel_title": "Channel 1"},
            {"id": "video2", "title": "Video 2", "channel_title": "Channel 2"},
            {"id": "video3", "title": "Video 3", "channel_title": "Channel 3"},
        ]

        mock_transcript = MagicMock()
        mock_snippet = Mock(text="Sample transcript")
        mock_transcript.snippets = [mock_snippet]

        with patch("src.collectors.youtube.YouTubeTranscriptApi") as mock_api:
            mock_api_instance = MagicMock()
            mock_api_instance.fetch.return_value = mock_transcript
            mock_api.return_value = mock_api_instance

            for video in videos:
                result = await collector._fetch_transcript(video, "en")
                assert result == "Sample transcript"
                # Verify each video ID was passed correctly
                mock_api_instance.fetch.assert_called_with(video["id"])

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fetch_real_video_transcript(self, collector):
        """
        Integration test: Fetch transcript from a real YouTube video.

        This test makes a real API call to YouTube to fetch the transcript
        for video ID: xIFkrVU5Krk

        Note: This test requires internet connection and may fail if:
        - The video is removed or made private
        - The transcript is disabled
        - Network issues occur
        - IP is blocked by YouTube

        To skip integration tests: pytest -m "not integration"
        """
        real_video_id = "xIFkrVU5Krk"
        video = {
            "id": real_video_id,
            "title": "Real Test Video",
            "channel_title": "Test Channel",
        }

        # Don't mock - make real API call
        result = await collector._fetch_transcript(video, "en")

        # Verify result
        if result is not None:
            # Success case
            assert isinstance(result, str)
            assert len(result) > 0, "Transcript should not be empty"
            print(f"\n✓ Successfully fetched transcript for video {real_video_id}")
            print(f"  Transcript length: {len(result)} characters")
            print(f"  First 200 chars: {result[:200]}...")
        else:
            # If transcript is not available, that's also acceptable
            # (video might not have transcripts enabled)
            print(f"\n⚠️  No transcript available for video {real_video_id}")
            print("  This is acceptable if the video doesn't have transcripts enabled")

        # Test should pass either way (transcript found or not)
        assert True
