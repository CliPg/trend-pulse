"""
Map-Reduce utilities for processing long texts with LLMs.
"""
from typing import List, Dict, Callable, Any, TypeVar, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .token_counter import TokenCounter
from .logger import get_analysis_logger
import asyncio


T = TypeVar('T')


class MapReduceProcessor:
    """Process large texts using Map-Reduce pattern."""

    def __init__(
        self,
        max_tokens_per_chunk: int = 2000,
        overlap: int = 200,
        batch_size: int = 5
    ):
        """
        Initialize Map-Reduce processor.

        Args:
            max_tokens_per_chunk: Maximum tokens per chunk
            overlap: Token overlap between chunks
            batch_size: Number of chunks to process in parallel
        """
        self.max_tokens_per_chunk = max_tokens_per_chunk
        self.overlap = overlap
        self.batch_size = batch_size
        self.logger = get_analysis_logger()

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_tokens_per_chunk * 4,  # Rough char to token estimate
            chunk_overlap=overlap * 4,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks.

        Args:
            text: Text to split

        Returns:
            List of text chunks
        """
        chunks = self.text_splitter.split_text(text)
        self.logger.info(f"Split text into {len(chunks)} chunks")
        return chunks

    def split_posts(self, posts: List[Dict[str, str]]) -> List[List[Dict]]:
        """
        Split posts into batches.

        Args:
            posts: List of post dictionaries

        Returns:
            List of post batches
        """
        # Estimate tokens per post
        total_chars = sum(len(p.get("content", "")) for p in posts)
        estimated_tokens = TokenCounter.estimate_tokens_from_chars(total_chars)

        # Calculate optimal batch size
        chunks_needed = max(1, estimated_tokens // self.max_tokens_per_chunk)
        batch_size = max(1, len(posts) // chunks_needed)

        batches = []
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i + batch_size]
            batches.append(batch)

        self.logger.info(
            f"Split {len(posts)} posts into {len(batches)} batches "
            f"(~{batch_size} posts per batch)"
        )

        return batches

    async def map_phase(
        self,
        chunks: List[str],
        map_func: Callable[[str], Any],
        description: str = "Map phase"
    ) -> List[Any]:
        """
        Execute map phase: process each chunk independently.

        Args:
            chunks: List of text chunks
            map_func: Async function to process each chunk
            description: Description for logging

        Returns:
            List of map results
        """
        self.logger.start_operation(description)
        results = []

        # Process in batches
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            total_batches = (len(chunks) + self.batch_size - 1) // self.batch_size

            self.logger.log_batch_progress(
                description, batch_num, total_batches, len(batch)
            )

            # Process batch concurrently
            batch_results = await asyncio.gather(
                *[map_func(chunk) for chunk in batch],
                return_exceptions=True
            )

            # Filter out exceptions
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Error processing chunk {i + j}: {result}")
                    results.append(None)  # Placeholder for failed chunks
                else:
                    results.append(result)

        self.logger.end_operation(description)
        # Filter out None values
        return [r for r in results if r is not None]

    async def reduce_phase(
        self,
        map_results: List[Any],
        reduce_func: Callable[[List[Any]], Any],
        description: str = "Reduce phase"
    ) -> Any:
        """
        Execute reduce phase: combine map results.

        Args:
            map_results: Results from map phase
            reduce_func: Async function to combine results
            description: Description for logging

        Returns:
            Final reduced result
        """
        self.logger.start_operation(description)
        result = await reduce_func(map_results)
        self.logger.end_operation(description)
        return result

    async def process(
        self,
        text: str,
        map_func: Callable[[str], Any],
        reduce_func: Callable[[List[Any]], Any],
        operation_name: str = "Map-Reduce"
    ) -> Any:
        """
        Execute full Map-Reduce pipeline.

        Args:
            text: Input text
            map_func: Async function to process each chunk
            reduce_func: Async function to combine results
            operation_name: Name of the operation

        Returns:
            Final result
        """
        self.logger.info(f"Starting {operation_name} Map-Reduce processing")

        # Split text
        chunks = self.split_text(text)

        # Map phase
        map_results = await self.map_phase(
            chunks,
            map_func,
            f"{operation_name} - Map"
        )

        # Reduce phase
        final_result = await self.reduce_phase(
            map_results,
            reduce_func,
            f"{operation_name} - Reduce"
        )

        self.logger.info(f"Completed {operation_name} Map-Reduce processing")
        return final_result

    async def process_posts(
        self,
        posts: List[Dict],
        map_func: Callable[[List[Dict]], Any],
        reduce_func: Callable[[List[Any]], Any],
        operation_name: str = "Map-Reduce"
    ) -> Any:
        """
        Execute Map-Reduce on posts.

        Args:
            posts: List of post dictionaries
            map_func: Async function to process each batch
            reduce_func: Async function to combine results
            operation_name: Name of the operation

        Returns:
            Final result
        """
        self.logger.info(f"Starting {operation_name} on {len(posts)} posts")

        # Split posts into batches
        batches = self.split_posts(posts)

        # Map phase
        map_results = await self.map_phase(
            batches,
            map_func,
            f"{operation_name} - Map"
        )

        # Reduce phase
        final_result = await self.reduce_phase(
            map_results,
            reduce_func,
            f"{operation_name} - Reduce"
        )

        self.logger.info(f"Completed {operation_name} Map-Reduce processing")
        return final_result


class KeySentenceExtractor:
    """Extract key sentences from long texts to reduce tokens."""

    @staticmethod
    def extract_by_position(
        text: str,
        num_sentences: int = 10
    ) -> str:
        """
        Extract key sentences by position (beginning, middle, end).

        Args:
            text: Input text
            num_sentences: Number of sentences to extract

        Returns:
            Text with key sentences
        """
        import re

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= num_sentences:
            return text

        # Extract from beginning, middle, and end
        indices = set()

        # First 3 sentences
        for i in range(min(3, len(sentences))):
            indices.add(i)

        # Last 3 sentences
        for i in range(max(0, len(sentences) - 3), len(sentences)):
            indices.add(i)

        # Middle sentences (evenly distributed)
        remaining = num_sentences - len(indices)
        if remaining > 0:
            step = len(sentences) // remaining
            for i in range(1, remaining):
                idx = min(i * step, len(sentences) - 1)
                indices.add(idx)

        selected = [sentences[i] for i in sorted(indices)]
        return '. '.join(selected) + '.'

    @staticmethod
    def extract_by_keywords(
        text: str,
        keywords: List[str],
        sentences_per_keyword: int = 2
    ) -> str:
        """
        Extract sentences containing important keywords.

        Args:
            text: Input text
            keywords: List of keywords to look for
            sentences_per_keyword: Sentences to extract per keyword

        Returns:
            Text with key sentences
        """
        import re

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Score sentences by keyword presence
        scored_sentences = []
        for i, sentence in enumerate(sentences):
            score = sum(
                1 for kw in keywords
                if kw.lower() in sentence.lower()
            )
            if score > 0:
                scored_sentences.append((i, sentence, score))

        # Sort by score and select top sentences
        scored_sentences.sort(key=lambda x: x[2], reverse=True)
        top_sentences = scored_sentences[:sentences_per_keyword * len(keywords)]

        # Sort by original position and join
        top_sentences.sort(key=lambda x: x[0])
        selected = [s[1] for s in top_sentences]

        return '. '.join(selected) + '.' if selected else text
