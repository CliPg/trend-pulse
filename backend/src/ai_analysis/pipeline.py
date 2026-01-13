"""
AI analysis pipeline that orchestrates sentiment analysis, clustering, and summarization.
"""
from typing import List, Dict
from src.ai_analysis.sentiment import SentimentAnalyzer
from src.ai_analysis.clustering import OpinionClusterer
from src.ai_analysis.summarizer import Summarizer


class AnalysisPipeline:
    """Complete AI analysis pipeline for social media data."""

    def __init__(self):
        """Initialize pipeline with all AI components."""
        self.sentiment_analyzer = SentimentAnalyzer()
        self.opinion_clusterer = OpinionClusterer()
        self.summarizer = Summarizer()

    async def analyze_posts(self, posts: List[Dict]) -> Dict:
        """
        Run complete analysis pipeline on posts.

        Args:
            posts: List of dicts with 'content' field

        Returns:
            Dict with:
                - sentiment_results: List of individual sentiment analyses
                - overall_sentiment: Average sentiment score (0-100)
                - clusters: Top 3 opinion clusters
                - summary: Discussion summary
        """
        if not posts:
            return {
                "sentiment_results": [],
                "overall_sentiment": 50.0,
                "clusters": [],
                "summary": "No posts to analyze.",
            }

        print(f"\n🔍 Analyzing {len(posts)} posts...")

        # Step 1: Sentiment analysis
        print("📊 Analyzing sentiment...")
        contents = [p.get("content", "") for p in posts]
        sentiment_results = await self.sentiment_analyzer.analyze_batch(contents)

        # Calculate overall sentiment
        sentiment_scores = [r.get("score", 50) for r in sentiment_results]
        overall_sentiment = self.sentiment_analyzer.calculate_overall_sentiment(
            sentiment_scores
        )

        print(f"   Overall sentiment: {overall_sentiment:.1f}/100")

        # Step 2: Opinion clustering
        print("🎯 Clustering opinions...")
        posts_with_sentiment = [
            {**p, "sentiment": s} for p, s in zip(posts, sentiment_results)
        ]

        clusters = await self.opinion_clusterer.cluster_opinions(
            posts_with_sentiment, top_n=3
        )

        print(f"   Found {len(clusters)} main opinion clusters")

        # Step 3: Summary
        print("📝 Generating summary...")
        summary = await self.summarizer.summarize_discussion(
            posts_with_sentiment, overall_sentiment
        )

        print("✅ Analysis complete!")

        return {
            "sentiment_results": sentiment_results,
            "overall_sentiment": overall_sentiment,
            "clusters": clusters,
            "summary": summary,
        }
