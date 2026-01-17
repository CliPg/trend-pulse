"""
Main orchestrator for TrendPulse.
Coordinates data collection, AI analysis, and database operations.
"""
from typing import List, Dict, Optional
from datetime import datetime

from src.collectors.reddit import RedditCollector
from src.collectors.youtube import YouTubeCollector
from src.collectors.twitter import TwitterCollector
from src.ai_analysis.pipeline import AnalysisPipeline
from src.database.operations import DatabaseManager
from src.config import Config
from src.utils.logger_config import get_orchestrator_logger


class TrendPulseOrchestrator:
    """Orchestrates the complete data collection and analysis pipeline."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize orchestrator with database manager.

        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.pipeline = AnalysisPipeline()
        self.logger = get_orchestrator_logger()

        # Initialize collectors
        self.reddit_collector = RedditCollector(
            {
                "REDDIT_CLIENT_ID": Config.REDDIT_CLIENT_ID,
                "REDDIT_CLIENT_SECRET": Config.REDDIT_CLIENT_SECRET,
                "REDDIT_USER_AGENT": Config.REDDIT_USER_AGENT,
            }
        )

        self.youtube_collector = YouTubeCollector(
            {
                "YOUTUBE_API_KEY": Config.YOUTUBE_API_KEY,
            }
        )

        self.twitter_collector = TwitterCollector()

    async def analyze_keyword(
        self,
        keyword: str,
        language: str = "en",
        platforms: Optional[List[str]] = None,
        limit_per_platform: int = 20,  # Reduced from 50 to 20 for testing
    ) -> Dict:
        """
        Complete analysis pipeline for a keyword.

        Args:
            keyword: Search keyword
            language: Language code (en, zh)
            platforms: List of platforms (default: all available)
            limit_per_platform: Max posts per platform

        Returns:
            Dict with analysis results and metadata
        """
        # Default to all platforms if none specified
        if platforms is None:
            platforms = ["reddit", "youtube", "twitter"]

        self.logger.info(f"Starting analysis for keyword: '{keyword}'")
        self.logger.info(f"Platforms: {', '.join(platforms)}")
        self.logger.info(f"Language: {language}")
        self.logger.info(f"Limit: {limit_per_platform} per platform")

        # Create or get keyword entry
        db_keyword = await self.db.get_or_create_keyword(keyword, language)

        # Collect data from all platforms
        all_posts = []

        # Reddit
        if "reddit" in platforms:
            self.logger.info("Collecting from Reddit...")
            try:
                reddit_posts = await self.reddit_collector.search(
                    keyword, language, limit_per_platform
                )
                all_posts.extend(reddit_posts)
                self.logger.info(f"Collected {len(reddit_posts)} posts from Reddit")
            except Exception as e:
                self.logger.error(f"Reddit collection failed: {e}")

        # YouTube
        if "youtube" in platforms:
            self.logger.info("Collecting from YouTube...")
            try:
                youtube_posts = await self.youtube_collector.search(
                    keyword, language, limit_per_platform
                )
                all_posts.extend(youtube_posts)
                self.logger.info(f"Collected {len(youtube_posts)} posts from YouTube")
            except Exception as e:
                self.logger.error(f"YouTube collection failed: {e}")

        # Twitter (optional)
        if "twitter" in platforms:
            self.logger.info("Collecting from Twitter...")
            try:
                twitter_posts = await self.twitter_collector.search(
                    keyword, language, limit_per_platform
                )
                all_posts.extend(twitter_posts)
                self.logger.info(f"Collected {len(twitter_posts)} posts from Twitter")
            except Exception as e:
                self.logger.error(f"Twitter collection failed: {e}")

        if not all_posts:
            self.logger.error("No posts collected from any platform")
            return {
                "keyword": keyword,
                "status": "failed",
                "message": "No posts collected",
                "posts_count": 0,
            }

        self.logger.info(f"Total posts collected: {len(all_posts)}")

        # Save posts to database
        self.logger.info("Saving to database...")
        posts_data = [
            {
                "platform": post.platform,
                "post_id": post.post_id,
                "author": post.author,
                "content": post.content,
                "url": post.url,
                "upvotes": post.upvotes,
                "likes": post.likes,
                "shares": post.shares,
                "comments_count": post.comments_count,
            }
            for post in all_posts
        ]

        saved_posts = await self.db.save_posts(posts_data, db_keyword.id)
        self.logger.info(f"Saved {len(saved_posts)} posts to database")

        # Run AI analysis
        self.logger.info("Running AI analysis...")
        posts_for_analysis = [
            {"content": post.content, "author": post.author} for post in saved_posts
        ]

        analysis_results = await self.pipeline.analyze_posts(posts_for_analysis)

        # Update sentiment scores in database
        self.logger.info("Saving analysis results...")
        for post, sentiment_result in zip(saved_posts, analysis_results["sentiment_results"]):
            await self.db.update_sentiment(
                post.id,
                sentiment_result.get("score", 50),
                sentiment_result.get("label", "neutral"),
            )

        # Save opinion clusters
        if analysis_results["clusters"]:
            clusters_data = [
                {
                    "label": c.get("label", ""),
                    "summary": c.get("summary", ""),
                    "mention_count": c.get("mention_count", 0),
                }
                for c in analysis_results["clusters"]
            ]
            await self.db.save_opinion_clusters(clusters_data, db_keyword.id)

        # Update keyword with overall results
        await self.db.update_keyword_analysis(
            db_keyword.id,
            analysis_results["overall_sentiment"],
            analysis_results["summary"],
        )

        self.logger.info("Analysis complete!")

        return {
            "keyword": keyword,
            "keyword_id": db_keyword.id,
            "status": "success",
            "posts_count": len(saved_posts),
            "platforms": platforms,
            "overall_sentiment": analysis_results["overall_sentiment"],
            "sentiment_label": self._get_sentiment_label(
                analysis_results["overall_sentiment"]
            ),
            "summary": analysis_results["summary"],
            "opinion_clusters": analysis_results["clusters"][:3],
            "posts": [
                {
                    "platform": post.platform,
                    "author": post.author,
                    "content": post.content[:200],  # Truncate for response
                    "url": post.url,
                    "sentiment_score": post.sentiment_score,
                    "sentiment_label": post.sentiment_label,
                    "upvotes": post.upvotes,
                    "likes": post.likes,
                }
                for post in saved_posts[:20]  # Return first 20 posts
            ],
        }

    def _get_sentiment_label(self, score: float) -> str:
        """
        Convert sentiment score to label.

        Args:
            score: Sentiment score (0-100)

        Returns:
            Sentiment label string
        """
        if score >= 70:
            return "positive"
        elif score >= 40:
            return "neutral"
        else:
            return "negative"
