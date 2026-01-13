"""
Opinion clustering module using LLM.
Identifies main themes and discussion points from social media posts.
"""
from typing import List, Dict
from src.ai_analysis.client import LLMClient


class OpinionClusterer:
    """Clusters opinions from social media posts."""

    def __init__(self):
        """Initialize opinion clusterer with LLM client."""
        self.client = LLMClient()
        self.system_prompt = """You are an expert at identifying and clustering opinions.
Analyze the given texts and identify the 3 main themes/opinions being discussed.

Respond with ONLY a JSON object in this format:
{
  "clusters": [
    {
      "label": "<brief theme label>",
      "summary": "<2-3 sentence summary>",
      "mention_count": <number of posts mentioning this>,
      "sample_quotes": ["<representative quote 1>", "<representative quote 2>"]
    }
  ],
  "dominant_sentiment": "<overall positive/negative/neutral>"
}

Focus on:
- Distinct themes and topics
- Points of agreement or controversy
- Common concerns or praise
- Notable trends or patterns"""

    async def cluster_opinions(self, posts: List[Dict[str, str]], top_n: int = 3) -> List[Dict]:
        """
        Cluster opinions from multiple posts.

        Args:
            posts: List of dicts with 'content' and optionally 'author'
            top_n: Number of top clusters to return (default 3)

        Returns:
            List of cluster dicts with label, summary, mention_count
        """
        # Filter posts: remove spam, short content
        filtered_posts = [
            p
            for p in posts
            if len(p.get("content", "")) > 50 and not self._is_spam(p.get("content", ""))
        ]

        if not filtered_posts:
            return []

        # Prepare text for analysis (sample if too many)
        sample_size = min(50, len(filtered_posts))
        sampled_posts = filtered_posts[:sample_size]

        # Create prompt
        user_prompt = (
            f"Analyze these {len(sampled_posts)} social media posts "
            f"and identify the top {top_n} opinion clusters:\n\n"
        )

        for i, post in enumerate(sampled_posts, 1):
            content = post.get("content", "")[:300]  # Truncate long posts
            user_prompt += f"\n{i}. {content}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            response = await self.client.chat_completion(messages, temperature=0.5)

            # Parse JSON response
            import json

            result = json.loads(response)
            return result.get("clusters", [])

        except Exception as e:
            print(f"Error clustering opinions: {e}")
            return []

    def _is_spam(self, content: str) -> bool:
        """
        Simple spam detection.

        Args:
            content: Content to check

        Returns:
            True if content appears to be spam
        """
        spam_keywords = [
            "buy now",
            "click here",
            "free trial",
            "subscribe",
            "follow me",
            "check my profile",
            "link in bio",
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in spam_keywords)
