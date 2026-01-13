"""
Summarization module using LLM.
Generates human-readable summaries of social media discussions.
"""
from typing import List, Dict
from src.ai_analysis.client import LLMClient


class Summarizer:
    """Generates summaries of social media discussions."""

    def __init__(self):
        """Initialize summarizer with LLM client."""
        self.client = LLMClient()
        self.system_prompt = """You are an expert at synthesizing social media discussions.
Create a clear, concise summary that captures:
- Main topics being discussed
- Overall sentiment (positive/negative/mixed)
- Key points of consensus or controversy
- Notable trends or patterns

Write in a natural, human-readable style. Avoid lists and bullet points.
Keep the summary to 2-3 paragraphs maximum."""

    async def summarize_discussion(
        self, posts: List[Dict[str, str]], sentiment_score: float
    ) -> str:
        """
        Summarize a collection of social media posts.

        Args:
            posts: List of dicts with 'content' field
            sentiment_score: Overall sentiment (0-100)

        Returns:
            Summary text
        """
        # Filter and sample posts
        filtered_posts = [p for p in posts if len(p.get("content", "")) > 50]

        if not filtered_posts:
            return "No substantial discussion found."

        # Sample posts to control token usage
        sample_size = min(30, len(filtered_posts))
        sampled_posts = filtered_posts[:sample_size]

        # Create prompt
        sentiment_desc = self._describe_sentiment(sentiment_score)

        user_prompt = f"""Summarize this social media discussion with an overall sentiment of {sentiment_desc} ({sentiment_score:.0f}/100).

Here are {len(sampled_posts)} representative posts:\n"""

        for i, post in enumerate(sampled_posts, 1):
            content = post.get("content", "")[:400]
            user_prompt += f"\n{i}. {content}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            summary = await self.client.chat_completion(messages, temperature=0.6)
            return summary

        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Summary generation failed."

    def _describe_sentiment(self, score: float) -> str:
        """
        Convert sentiment score to description.

        Args:
            score: Sentiment score (0-100)

        Returns:
            Description string
        """
        if score >= 80:
            return "very positive"
        elif score >= 60:
            return "positive"
        elif score >= 40:
            return "neutral"
        elif score >= 20:
            return "negative"
        else:
            return "very negative"
