"""
Summarization module using LangChain with Map-Reduce support.
Generates human-readable summaries of social media discussions.
"""
from typing import List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

from .client import LangChainLLMClient
from .prompts import (
    create_summarization_prompt_template,
    create_map_prompt,
    create_reduce_prompt,
    get_summarization_system_prompt
)
from .utils import get_analysis_logger, TokenCounter, TextPreprocessor, MapReduceProcessor


class Summarizer:
    """Enhanced summarizer using LangChain with Map-Reduce."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize summarizer with LangChain client.

        Args:
            provider: LLM provider ('openai', 'tongyi')
        """
        self.client = LangChainLLMClient(provider=provider, temperature=0.6)
        self.logger = get_analysis_logger()
        self.system_prompt = get_summarization_system_prompt()

        # Preconfigure chains
        self._summary_chain = self._create_summary_chain()
        self._map_chain = self._create_map_chain()
        self._reduce_chain = self._create_reduce_chain()

    def _create_summary_chain(self):
        """Create chain for direct summarization."""
        prompt_template = create_summarization_prompt_template()
        chain = prompt_template | self.client.llm | StrOutputParser()
        return chain

    def _create_map_chain(self):
        """Create chain for Map phase."""
        prompt_template = create_map_prompt()
        chain = prompt_template | self.client.llm | StrOutputParser()
        return chain

    def _create_reduce_chain(self):
        """Create chain for Reduce phase."""
        prompt_template = create_reduce_prompt()
        chain = prompt_template | self.client.llm | StrOutputParser()
        return chain

    async def summarize_discussion(
        self,
        posts: List[Dict[str, str]],
        sentiment_score: float,
        use_map_reduce: bool = False
    ) -> str:
        """
        Summarize a collection of social media posts.

        Args:
            posts: List of dicts with 'content' field
            sentiment_score: Overall sentiment (0-100)
            use_map_reduce: Force use of Map-Reduce

        Returns:
            Summary text (2-3 paragraphs)
        """
        if not posts:
            return "No posts to summarize."

        self.client.logger.start_operation("discussion_summarization")

        # Filter and preprocess posts
        filtered_posts = self._filter_posts(posts)

        if not filtered_posts:
            self.logger.warning("No valid posts after filtering")
            return "No substantial discussion found."

        # Estimate tokens and decide strategy
        total_chars = sum(len(p.get("content", "")) for p in filtered_posts)
        estimated_tokens = TokenCounter.estimate_tokens_from_chars(total_chars)

        if estimated_tokens > 3000 or use_map_reduce:
            summary = await self._summarize_with_map_reduce(filtered_posts, sentiment_score)
        else:
            summary = await self._summarize_direct(filtered_posts, sentiment_score)

        self.client.logger.end_operation("discussion_summarization")
        return summary

    def _filter_posts(self, posts: List[Dict]) -> List[Dict]:
        """Filter and preprocess posts."""
        filtered = []

        for post in posts:
            content = post.get("content", "")

            # Filter by length
            if len(content) < 50:
                continue

            # Clean content
            post["content"] = TextPreprocessor.clean_for_analysis(content, max_length=600)
            filtered.append(post)

        # Sample if too many
        max_posts = 30
        if len(filtered) > max_posts:
            # Sample evenly from the list
            step = len(filtered) // max_posts
            filtered = filtered[::step][:max_posts]

        self.logger.info(f"Filtered to {len(filtered)} posts for summarization")
        return filtered

    async def _summarize_direct(
        self,
        posts: List[Dict],
        sentiment_score: float
    ) -> str:
        """Summarize using single API call."""
        # Build posts text
        posts_text = "\n".join(
            f"- \"{p['content']}\""
            for p in posts
        )

        # Get sentiment description
        sentiment_desc = self._describe_sentiment(sentiment_score)

        # Get platform if available
        platform = posts[0].get("platform", "social media")

        try:
            summary = await self.client.run_chain(
                self._summary_chain,
                {
                    "sentiment_description": sentiment_desc,
                    "sentiment_score": f"{sentiment_score:.0f}",
                    "post_count": len(posts),
                    "platform": platform,
                    "posts": posts_text
                },
                operation="summarization_analysis"
            )

            return summary.strip()

        except Exception as e:
            self.logger.error(f"Error in direct summarization: {e}")
            return "Summary generation failed."

    async def _summarize_with_map_reduce(
        self,
        posts: List[Dict],
        sentiment_score: float
    ) -> str:
        """Summarize using Map-Reduce pattern."""
        processor = MapReduceProcessor(
            max_tokens_per_chunk=1500,
            overlap=100
        )

        # Combine all posts into single text for splitting
        combined_text = "\n\n".join(
            f"Post: {p['content']}"
            for p in posts
        )

        sentiment_desc = self._describe_sentiment(sentiment_score)

        # Map phase: summarize each chunk
        async def map_chunk(chunk: str) -> str:
            try:
                result = await self.client.run_chain(
                    self._map_chain,
                    {"posts": chunk},
                    operation="summarization_map"
                )
                return result.strip()
            except Exception as e:
                self.logger.error(f"Error in map phase: {e}")
                return f"Summary of {len(chunk)} characters of discussion."

        # Reduce phase: combine summaries
        async def reduce_summaries(summaries: List[str]) -> str:
            if not summaries:
                return "No summary generated."

            # Combine summaries
            combined_summaries = "\n\n".join(
                f"Summary {i+1}: {s}"
                for i, s in enumerate(summaries)
            )

            try:
                final_summary = await self.client.run_chain(
                    self._reduce_chain,
                    {
                        "sentiment_description": sentiment_desc,
                    "sentiment_score": f"{sentiment_score:.0f}",
                    "summaries": combined_summaries
                })

                return final_summary.strip()

            except Exception as e:
                self.logger.error(f"Error in reduce phase: {e}")
                # Fallback: concatenate summaries
                return "\n\n".join(summaries)

        # Execute Map-Reduce
        summary = await processor.process(
            combined_text,
            map_chunk,
            reduce_summaries,
            "summarization_map_reduce"
        )

        return summary

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

    async def extract_key_points(
        self,
        posts: List[Dict],
        max_points: int = 5
    ) -> List[str]:
        """
        Extract key discussion points from posts.

        Args:
            posts: List of posts
            max_points: Maximum number of key points

        Returns:
            List of key point strings
        """
        # Sample posts
        sampled_posts = posts[:min(20, len(posts))]

        prompt = f"""Analyze these social media posts and extract the top {max_points} key discussion points.

Posts:
{chr(10).join(f'{i+1}. {p["content"][:200]}' for i, p in enumerate(sampled_posts))}

Provide a JSON array of key discussion points:
["point 1", "point 2", ...]

JSON array:"""

        try:
            response = await self.client.invoke(
                prompt,
                system_prompt="You are an expert at extracting key points from discussions. Always respond with valid JSON.",
                operation="extract_key_points"
            )

            # Parse JSON array
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                points = json.loads(json_match.group(0))
                return points[:max_points]

            points = json.loads(response)
            return points[:max_points]

        except Exception as e:
            self.logger.error(f"Error extracting key points: {e}")
            return []

    def log_summary(self):
        """Log token usage summary."""
        self.client.log_summary()
