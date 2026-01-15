"""
Token counting utilities for cost estimation and optimization.
"""
import tiktoken
from typing import List, Dict


class TokenCounter:
    """Token counter for text analysis."""

    # Average token-to-character ratios for different languages
    TOKEN_RATIO = {
        "en": 0.25,  # 1 token ≈ 4 characters for English
        "zh": 0.6,   # 1 token ≈ 1.7 characters for Chinese
        "mixed": 0.4,
    }

    @staticmethod
    def count_tokens(text: str, model: str = "gpt-4") -> int:
        """
        Count tokens in text using tiktoken.

        Args:
            text: Text to count
            model: Model name for encoding

        Returns:
            Number of tokens
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback to rough estimate
            return int(len(text) * TokenCounter.TOKEN_RATIO["en"])

    @staticmethod
    def count_tokens_batch(texts: List[str], model: str = "gpt-4") -> int:
        """
        Count total tokens in multiple texts.

        Args:
            texts: List of texts
            model: Model name

        Returns:
            Total token count
        """
        return sum(TokenCounter.count_tokens(text, model) for text in texts)

    @staticmethod
    def estimate_tokens_from_chars(char_count: int, language: str = "en") -> int:
        """
        Estimate tokens from character count.

        Args:
            char_count: Number of characters
            language: Language code (en, zh, mixed)

        Returns:
            Estimated token count
        """
        ratio = TokenCounter.TOKEN_RATIO.get(language, TokenCounter.TOKEN_RATIO["en"])
        return int(char_count * ratio)

    @staticmethod
    def truncate_to_tokens(text: str, max_tokens: int, model: str = "gpt-4") -> str:
        """
        Truncate text to fit within max tokens.

        Args:
            text: Text to truncate
            max_tokens: Maximum tokens allowed
            model: Model name

        Returns:
            Truncated text
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)

            if len(tokens) <= max_tokens:
                return text

            # Truncate and decode
            truncated_tokens = tokens[:max_tokens]
            return encoding.decode(truncated_tokens)
        except Exception:
            # Fallback to character-based truncation
            max_chars = int(max_tokens / TokenCounter.TOKEN_RATIO["en"])
            return text[:max_chars]

    @staticmethod
    def split_text_by_tokens(
        text: str,
        max_tokens_per_chunk: int,
        overlap: int = 0,
        model: str = "gpt-4"
    ) -> List[str]:
        """
        Split text into chunks by token count.

        Args:
            text: Text to split
            max_tokens_per_chunk: Maximum tokens per chunk
            overlap: Token overlap between chunks
            model: Model name

        Returns:
            List of text chunks
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
            tokens = encoding.encode(text)

            chunks = []
            start = 0

            while start < len(tokens):
                end = start + max_tokens_per_chunk
                chunk_tokens = tokens[start:end]

                # Decode chunk
                chunk_text = encoding.decode(chunk_tokens)
                chunks.append(chunk_text)

                # Move start position with overlap
                start = end - overlap

            return chunks
        except Exception:
            # Fallback to character-based splitting
            chars_per_chunk = int(max_tokens_per_chunk / TokenCounter.TOKEN_RATIO["en"])
            overlap_chars = int(overlap / TokenCounter.TOKEN_RATIO["en"])

            chunks = []
            start = 0

            while start < len(text):
                end = start + chars_per_chunk
                chunk = text[start:end]
                chunks.append(chunk)
                start = end - overlap_chars

            return chunks

    @staticmethod
    def calculate_cost(
        input_tokens: int,
        output_tokens: int,
        model: str = "gpt-4o-mini"
    ) -> float:
        """
        Calculate API cost in USD.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model name

        Returns:
            Cost in USD
        """
        # OpenAI pricing (as of 2025)
        pricing = {
            "gpt-4o": (2.50, 10.00),
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4-turbo": (10.00, 30.00),
            "gpt-3.5-turbo": (0.50, 1.50),
        }

        # Tongyi pricing (estimated)
        tongyi_pricing = {
            "qwen-plus": (0.004, 0.006),
            "qwen-turbo": (0.001, 0.002),
            "qwen-max": (0.02, 0.06),
        }

        if model in pricing:
            input_cost, output_cost = pricing[model]
        elif model in tongyi_pricing:
            input_cost, output_cost = tongyi_pricing[model]
        else:
            # Default conservative estimate
            input_cost, output_cost = (0.50, 1.50)

        total_cost = (input_tokens / 1000) * input_cost + \
                    (output_tokens / 1000) * output_cost
        return total_cost


class TextPreprocessor:
    """Text preprocessing for token optimization."""

    @staticmethod
    def extract_key_sentences(text: str, max_sentences: int = 5) -> str:
        """
        Extract key sentences using simple heuristics.

        Args:
            text: Input text
            max_sentences: Maximum sentences to extract

        Returns:
            Text with key sentences
        """
        import re

        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) <= max_sentences:
            return text

        # Simple heuristic: extract first, middle, last sentences
        indices = set()
        indices.add(0)  # First
        indices.add(len(sentences) - 1)  # Last

        # Add evenly spaced sentences
        step = len(sentences) // (max_sentences - 1)
        for i in range(1, max_sentences - 1):
            indices.add(min(i * step, len(sentences) - 1))

        selected = [sentences[i] for i in sorted(indices)]
        return '. '.join(selected) + '.'

    @staticmethod
    def remove_redundancy(text: str) -> str:
        """
        Remove redundant content (repeated phrases, etc.).

        Args:
            text: Input text

        Returns:
            Cleaned text
        """
        import re

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove repeated punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)

        return text.strip()

    @staticmethod
    def clean_for_analysis(text: str, max_length: int = 1000) -> str:
        """
        Clean text for AI analysis.

        Args:
            text: Input text
            max_length: Maximum length

        Returns:
            Cleaned text
        """
        # Remove redundancy
        text = TextPreprocessor.remove_redundancy(text)

        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length] + "..."

        return text
