"""
Enhanced AI analysis pipeline using LangChain.
Orchestrates sentiment analysis, clustering, and summarization with Map-Reduce support.
"""
from typing import List, Dict, Optional
from .sentiment import SentimentAnalyzer
from .clustering import OpinionClusterer
from .summarizer import Summarizer
from .client import LangChainLLMClient
from .utils import get_analysis_logger


class AnalysisPipeline:
    """Enhanced AI analysis pipeline with LangChain and Map-Reduce."""

    def __init__(self, provider: Optional[str] = None, use_map_reduce: bool = False):
        """
        Initialize pipeline with all AI components.

        Args:
            provider: LLM provider ('openai', 'tongyi')
            use_map_reduce: Whether to use Map-Reduce for large datasets
        """
        self.provider = provider
        self.use_map_reduce = use_map_reduce
        self.logger = get_analysis_logger()

        # Initialize components
        self.sentiment_analyzer = SentimentAnalyzer(provider=provider)
        self.opinion_clusterer = OpinionClusterer(provider=provider)
        self.summarizer = Summarizer(provider=provider)

        self.logger.info(f"Initialized AnalysisPipeline with provider: {provider}")

    async def analyze_posts(
        self,
        posts: List[Dict],
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Run complete analysis pipeline on posts.

        Args:
            posts: List of dicts with 'content' field
            options: Optional analysis options
                - use_map_reduce: Enable Map-Reduce for large datasets
                - skip_clustering: Skip opinion clustering
                - skip_summary: Skip summary generation
                - top_n_clusters: Number of top clusters (default 3)

        Returns:
            Dict with:
                - sentiment_results: List of individual sentiment analyses
                - overall_sentiment: Average sentiment score (0-100)
                - clusters: Top 3 opinion clusters (or None if skipped)
                - summary: Discussion summary (or None if skipped)
                - token_usage: Token usage statistics
        """
        if not posts:
            return {
                "sentiment_results": [],
                "overall_sentiment": 50.0,
                "clusters": [],
                "summary": "No posts to analyze.",
                "token_usage": {}
            }

        options = options or {}
        use_map_reduce = options.get("use_map_reduce", self.use_map_reduce)
        skip_clustering = options.get("skip_clustering", False)
        skip_summary = options.get("skip_summary", False)
        top_n_clusters = options.get("top_n_clusters", 3)

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Starting AI analysis pipeline")
        self.logger.info(f"Posts: {len(posts)}")
        self.logger.info(f"Map-Reduce: {use_map_reduce}")
        self.logger.info(f"{'='*60}\n")

        # Step 1: Sentiment analysis
        self.logger.info("📊 Step 1/3: Analyzing sentiment...")
        contents = [p.get("content", "") for p in posts]
        sentiment_results = await self.sentiment_analyzer.analyze_batch(
            contents,
            use_map_reduce=use_map_reduce
        )

        # Calculate overall sentiment
        sentiment_scores = [r.get("score", 50) for r in sentiment_results]
        overall_sentiment = self.sentiment_analyzer.calculate_overall_sentiment(
            sentiment_scores
        )

        self.logger.info(f"✓ Overall sentiment: {overall_sentiment:.1f}/100")

        # Step 2: Opinion clustering (optional)
        clusters = []
        if not skip_clustering:
            self.logger.info("🎯 Step 2/3: Clustering opinions...")
            posts_with_sentiment = [
                {**p, "sentiment": s}
                for p, s in zip(posts, sentiment_results)
            ]

            clusters = await self.opinion_clusterer.cluster_opinions(
                posts_with_sentiment,
                top_n=top_n_clusters,
                use_map_reduce=use_map_reduce
            )

            self.logger.info(f"✓ Found {len(clusters)} main opinion clusters")
        else:
            self.logger.info("⏭️  Skipping opinion clustering")

        # Step 3: Summary (optional)
        summary = None
        if not skip_summary:
            self.logger.info("📝 Step 3/3: Generating summary...")
            posts_with_sentiment = [
                {**p, "sentiment": s}
                for p, s in zip(posts, sentiment_results)
            ]

            summary = await self.summarizer.summarize_discussion(
                posts_with_sentiment,
                overall_sentiment,
                use_map_reduce=use_map_reduce
            )

            self.logger.info(f"✓ Summary generated ({len(summary)} characters)")
        else:
            self.logger.info("⏭️  Skipping summary generation")

        self.logger.info(f"\n{'='*60}")
        self.logger.info("✅ AI analysis pipeline completed!")
        self.logger.info(f"{'='*60}\n")

        # Log token usage summary
        self.logger.log_token_summary()

        # Collect token usage from all components
        token_usage = {
            "total": self.logger.total_input_tokens + self.logger.total_output_tokens,
            "input": self.logger.total_input_tokens,
            "output": self.logger.total_output_tokens,
            "cost": self.logger.total_cost_estimate,
            "api_calls": self.logger.api_calls
        }

        return {
            "sentiment_results": sentiment_results,
            "overall_sentiment": overall_sentiment,
            "clusters": clusters,
            "summary": summary,
            "token_usage": token_usage
        }

    async def analyze_sentiment_only(self, posts: List[Dict]) -> Dict:
        """
        Run only sentiment analysis (faster, cheaper).

        Args:
            posts: List of dicts with 'content' field

        Returns:
            Dict with sentiment_results and overall_sentiment
        """
        if not posts:
            return {
                "sentiment_results": [],
                "overall_sentiment": 50.0,
                "token_usage": {}
            }

        self.logger.info(f"Analyzing sentiment for {len(posts)} posts...")

        contents = [p.get("content", "") for p in posts]
        sentiment_results = await self.sentiment_analyzer.analyze_batch(contents)

        sentiment_scores = [r.get("score", 50) for r in sentiment_results]
        overall_sentiment = self.sentiment_analyzer.calculate_overall_sentiment(
            sentiment_scores
        )

        return {
            "sentiment_results": sentiment_results,
            "overall_sentiment": overall_sentiment,
            "token_usage": self.client.get_token_summary()
        }

    def reset_tracking(self):
        """Reset token tracking."""
        self.logger.reset_token_tracking()
