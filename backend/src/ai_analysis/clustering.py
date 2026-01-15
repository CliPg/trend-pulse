"""
Opinion clustering module using LangChain with enhanced features.
Identifies main themes and discussion points from social media posts.
"""
from typing import List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
import json
import re

from .client import LangChainLLMClient
from .prompts import (
    create_clustering_prompt_template,
    get_clustering_system_prompt
)
from .utils import get_analysis_logger, TokenCounter, TextPreprocessor, MapReduceProcessor


class OpinionClusterer:
    """Enhanced opinion clusterer using LangChain."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize opinion clusterer with LangChain client.

        Args:
            provider: LLM provider ('openai', 'tongyi')
        """
        self.client = LangChainLLMClient(provider=provider, temperature=0.5)
        self.logger = get_analysis_logger()
        self.system_prompt = get_clustering_system_prompt()

        # Preconfigure chain
        self._chain = self._create_clustering_chain()

    def _create_clustering_chain(self):
        """Create chain for opinion clustering."""
        prompt_template = create_clustering_prompt_template()
        chain = prompt_template | self.client.llm | StrOutputParser()
        return chain

    async def cluster_opinions(
        self,
        posts: List[Dict[str, str]],
        top_n: int = 3,
        use_map_reduce: bool = False
    ) -> List[Dict]:
        """
        Cluster opinions from multiple posts.

        Args:
            posts: List of dicts with 'content' and optionally 'author'
            top_n: Number of top clusters to return (default 3)
            use_map_reduce: Use Map-Reduce for large datasets

        Returns:
            List of cluster dicts with label, summary, mention_count
        """
        if not posts:
            return []

        self.client.logger.start_operation("opinion_clustering")

        # Filter and preprocess posts
        filtered_posts = self._filter_posts(posts)

        if not filtered_posts:
            self.logger.warning("No valid posts after filtering")
            return []

        # Estimate tokens and decide strategy
        total_chars = sum(len(p.get("content", "")) for p in filtered_posts)
        estimated_tokens = TokenCounter.estimate_tokens_from_chars(total_chars)

        if estimated_tokens > 4000 or use_map_reduce:
            results = await self._cluster_with_map_reduce(filtered_posts, top_n)
        else:
            results = await self._cluster_direct(filtered_posts, top_n)

        self.client.logger.end_operation("opinion_clustering")
        return results

    def _filter_posts(self, posts: List[Dict]) -> List[Dict]:
        """Filter out low-quality posts."""
        filtered = []

        for post in posts:
            content = post.get("content", "")

            # Filter by length
            if len(content) < 50:
                continue

            # Filter spam
            if self._is_spam(content):
                continue

            # Clean content
            post["content"] = TextPreprocessor.clean_for_analysis(content, max_length=500)
            filtered.append(post)

        self.logger.info(f"Filtered {len(posts)} posts down to {len(filtered)} valid posts")
        return filtered

    def _is_spam(self, content: str) -> bool:
        """Detect spam content."""
        spam_keywords = [
            "buy now", "click here", "free trial", "subscribe",
            "follow me", "check my profile", "link in bio"
        ]

        content_lower = content.lower()
        return any(keyword in content_lower for keyword in spam_keywords)

    async def _cluster_direct(
        self,
        posts: List[Dict],
        top_n: int
    ) -> List[Dict]:
        """Cluster posts using single API call."""
        # Sample if too many
        sample_size = min(50, len(posts))
        sampled_posts = posts[:sample_size]

        # Build prompt
        posts_text = "\n".join(
            f"{i+1}. {p['content'][:300]}"
            for i, p in enumerate(sampled_posts)
        )

        try:
            response = await self.client.run_chain(
                self._chain,
                {
                    "post_count": len(sampled_posts),
                    "top_n": top_n,
                    "posts": posts_text
                },
                operation="clustering_analysis"
            )

            # Parse JSON response
            return self._parse_clustering_response(response)

        except Exception as e:
            self.logger.error(f"Error in direct clustering: {e}")
            return []

    async def _cluster_with_map_reduce(
        self,
        posts: List[Dict],
        top_n: int
    ) -> List[Dict]:
        """Cluster using Map-Reduce pattern."""
        processor = MapReduceProcessor(
            max_tokens_per_chunk=2000,
            batch_size=3
        )

        # Split posts into batches
        batches = processor.split_posts(posts)

        # Map phase: analyze each batch
        async def map_batch(batch_posts: List[Dict]) -> List[Dict]:
            return await self._cluster_direct(batch_posts, min(2, top_n))

        # Reduce phase: merge clusters
        async def reduce_clusters(batch_clusters: List[List[Dict]]) -> List[Dict]:
            # Flatten all clusters
            all_clusters = []
            for clusters in batch_clusters:
                all_clusters.extend(clusters)

            if not all_clusters:
                return []

            # Group by similar labels
            merged = self._merge_similar_clusters(all_clusters, top_n)
            return merged

        # Execute Map-Reduce
        results = await processor.process_posts(
            posts,
            map_batch,
            reduce_clusters,
            "clustering_map_reduce"
        )

        return results[:top_n]

    def _parse_clustering_response(self, response: str) -> List[Dict]:
        """Parse JSON response from LLM."""
        try:
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                return result.get("clusters", [])

            # Try direct parse
            result = json.loads(response)
            return result.get("clusters", [])

        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing clustering response: {e}")
            self.logger.debug(f"Response was: {response[:300]}")
            return []

    def _merge_similar_clusters(
        self,
        clusters: List[Dict],
        max_clusters: int
    ) -> List[Dict]:
        """Merge clusters with similar themes."""
        if len(clusters) <= max_clusters:
            return clusters

        # Simple merging: group by keywords in labels
        merged = []
        used_indices = set()

        for i, cluster in enumerate(clusters):
            if i in used_indices:
                continue

            # Find similar clusters
            similar = [cluster]
            used_indices.add(i)

            label_words = set(cluster["label"].lower().split())

            for j, other in enumerate(clusters):
                if j <= i or j in used_indices:
                    continue

                other_words = set(other["label"].lower().split())

                # Check for overlap
                if label_words & other_words:  # Intersection
                    similar.append(other)
                    used_indices.add(j)

            # Merge similar clusters
            if len(similar) == 1:
                merged.append(cluster)
            else:
                # Merge mention counts and combine sample quotes
                merged_cluster = {
                    "label": cluster["label"],
                    "summary": f"Combined insights from {len(similar)} related discussions",
                    "mention_count": sum(c.get("mention_count", 0) for c in similar),
                    "sample_quotes": []
                }

                # Collect unique quotes
                all_quotes = []
                for c in similar:
                    all_quotes.extend(c.get("sample_quotes", []))

                # Get top few unique quotes
                seen = set()
                for quote in all_quotes:
                    if quote not in seen:
                        merged_cluster["sample_quotes"].append(quote)
                        seen.add(quote)
                        if len(merged_cluster["sample_quotes"]) >= 3:
                            break

                merged.append(merged_cluster)

        # Sort by mention count and return top N
        merged.sort(key=lambda x: x.get("mention_count", 0), reverse=True)
        return merged[:max_clusters]

    def log_summary(self):
        """Log token usage summary."""
        self.client.log_summary()
