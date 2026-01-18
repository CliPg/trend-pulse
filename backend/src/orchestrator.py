"""
Main orchestrator for TrendPulse.
Coordinates data collection, AI analysis, and database operations.
"""
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
import asyncio

from src.collectors.reddit import RedditCollector
from src.collectors.youtube import YouTubeCollector
from src.collectors.twitter import TwitterCollector
from src.ai_analysis.pipeline import AnalysisPipeline
from src.database.operations import DatabaseManager
from src.config import Config
from src.utils.logger_config import get_orchestrator_logger
from src.utils.mermaid_generator import (
    generate_mermaid_mindmap,
    generate_mermaid_pie_chart,
    generate_mermaid_flowchart
)


# Progress callback type for streaming updates
ProgressCallback = Callable[[str, str, Optional[Dict[str, Any]]], None]


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
        progress_callback: Optional[ProgressCallback] = None,
    ) -> Dict:
        """
        Complete analysis pipeline for a keyword.

        Args:
            keyword: Search keyword
            language: Language code (en, zh)
            platforms: List of platforms (default: all available)
            limit_per_platform: Max posts per platform
            progress_callback: Optional callback for progress updates
                               Signature: (stage: str, message: str, data: Optional[Dict]) -> None

        Returns:
            Dict with analysis results and metadata
        """
        # Helper function for progress updates
        async def report_progress(stage: str, message: str, data: Optional[Dict] = None):
            self.logger.info(f"[{stage}] {message}")
            if progress_callback:
                try:
                    progress_callback(stage, message, data)
                    await asyncio.sleep(0)  # Yield control to allow SSE to flush
                except Exception as e:
                    self.logger.warning(f"Progress callback error: {e}")

        # Default to all platforms if none specified
        if platforms is None:
            platforms = ["reddit", "youtube", "twitter"]

        await report_progress("init", f"Starting analysis for keyword: '{keyword}'", {
            "keyword": keyword,
            "platforms": platforms,
            "language": language,
            "limit": limit_per_platform
        })

        self.logger.info(f"Platforms: {', '.join(platforms)}")
        self.logger.info(f"Language: {language}")
        self.logger.info(f"Limit: {limit_per_platform} per platform")

        # Create or get keyword entry
        await report_progress("database", "Preparing database...")
        db_keyword = await self.db.get_or_create_keyword(keyword, language)

        # Collect data from all platforms
        all_posts = []

        # Reddit
        if "reddit" in platforms:
            await report_progress("collecting", "Collecting data from Reddit...", {"platform": "reddit"})
            try:
                reddit_posts = await self.reddit_collector.search(
                    keyword, language, limit_per_platform
                )
                all_posts.extend(reddit_posts)
                await report_progress("collecting", f"Collected {len(reddit_posts)} posts from Reddit", {
                    "platform": "reddit",
                    "count": len(reddit_posts)
                })
            except Exception as e:
                self.logger.error(f"Reddit collection failed: {e}")
                await report_progress("error", f"Reddit collection failed: {str(e)[:100]}", {"platform": "reddit"})

        # YouTube
        if "youtube" in platforms:
            await report_progress("collecting", "Collecting data from YouTube...", {"platform": "youtube"})
            try:
                youtube_posts = await self.youtube_collector.search(
                    keyword, language, limit_per_platform
                )
                all_posts.extend(youtube_posts)
                await report_progress("collecting", f"Collected {len(youtube_posts)} comments from YouTube", {
                    "platform": "youtube",
                    "count": len(youtube_posts)
                })
            except Exception as e:
                self.logger.error(f"YouTube collection failed: {e}")
                await report_progress("error", f"YouTube collection failed: {str(e)[:100]}", {"platform": "youtube"})

        # Twitter (optional)
        if "twitter" in platforms:
            await report_progress("collecting", "Collecting data from Twitter/X...", {"platform": "twitter"})
            try:
                twitter_posts = await self.twitter_collector.search(
                    keyword, language, limit_per_platform
                )
                all_posts.extend(twitter_posts)
                await report_progress("collecting", f"Collected {len(twitter_posts)} tweets from Twitter/X", {
                    "platform": "twitter",
                    "count": len(twitter_posts)
                })
            except Exception as e:
                self.logger.error(f"Twitter collection failed: {e}")
                await report_progress("error", f"Twitter collection failed: {str(e)[:100]}", {"platform": "twitter"})

        if not all_posts:
            self.logger.error("No posts collected from any platform")
            await report_progress("error", "No posts collected from any platform", {"total": 0})
            return {
                "keyword": keyword,
                "status": "failed",
                "message": "No posts collected",
                "posts_count": 0,
            }

        await report_progress("collecting", f"Total posts collected: {len(all_posts)}", {"total": len(all_posts)})

        # Save posts to database
        await report_progress("database", "Saving posts to database...")
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
        await report_progress("database", f"Saved {len(saved_posts)} posts to database", {"saved": len(saved_posts)})

        # Run AI analysis
        await report_progress("analyzing", "Running AI sentiment analysis...", {"total_posts": len(saved_posts)})
        posts_for_analysis = [
            {"content": post.content, "author": post.author} for post in saved_posts
        ]

        analysis_results = await self.pipeline.analyze_posts(posts_for_analysis)
        await report_progress("analyzing", "AI analysis complete, processing results...", {
            "sentiment": analysis_results.get("overall_sentiment"),
            "clusters": len(analysis_results.get("clusters", []))
        })

        # Update sentiment scores in database
        await report_progress("database", "Saving analysis results to database...")
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

        await report_progress("visualizing", "Generating visualizations...")

        # Generate Mermaid visualizations
        sentiment_label = self._get_sentiment_label(analysis_results["overall_sentiment"])

        mermaid_mindmap = generate_mermaid_mindmap(
            keyword=keyword,
            clusters=analysis_results["clusters"][:3],
            sentiment_score=analysis_results["overall_sentiment"],
            sentiment_label=sentiment_label
        )

        mermaid_pie_chart = generate_mermaid_pie_chart(
            keyword=keyword,
            clusters=analysis_results["clusters"][:3]
        )

        # Prepare posts data for flowchart (only include posts with valid sentiment scores)
        posts_data = [
            {
                "platform": post.platform,
                "author": post.author,
                "content": post.content,
                "sentiment_score": post.sentiment_score,
            }
            for post in saved_posts[:10]
            if post.sentiment_score is not None  # Filter out None values
        ]

        mermaid_flowchart = generate_mermaid_flowchart(
            keyword=keyword,
            posts=posts_data,
            top_n=10
        )

        await report_progress("complete", "Analysis complete!", {
            "posts_count": len(saved_posts),
            "sentiment": analysis_results["overall_sentiment"],
            "sentiment_label": sentiment_label
        })

        return {
            "keyword": keyword,
            "keyword_id": db_keyword.id,
            "status": "success",
            "posts_count": len(saved_posts),
            "platforms": platforms,
            "overall_sentiment": analysis_results["overall_sentiment"],
            "sentiment_label": sentiment_label,
            "summary": analysis_results["summary"],
            "opinion_clusters": analysis_results["clusters"][:3],
            "mermaid": {
                "mindmap": mermaid_mindmap,
                "pie_chart": mermaid_pie_chart,
                "flowchart": mermaid_flowchart,
            },
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
