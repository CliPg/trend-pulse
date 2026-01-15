"""
Sentiment analysis module using LangChain with enhanced features.
Analyzes sentiment of social media posts on a 0-100 scale.
"""
from typing import List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.runnables import RunnableParallel

from .langchain_client import LangChainLLMClient
from .prompts import (
    create_sentiment_prompt_template,
    create_batch_sentiment_prompt_template,
    get_sentiment_system_prompt
)
from .utils import get_analysis_logger, TokenCounter, TextPreprocessor


class SentimentAnalyzerV2:
    """Enhanced sentiment analyzer using LangChain."""

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize sentiment analyzer with LangChain client.

        Args:
            provider: LLM provider ('openai', 'tongyi')
        """
        self.client = LangChainLLMClient(provider=provider, temperature=0.3)
        self.logger = get_analysis_logger()
        self.system_prompt = get_sentiment_system_prompt()

        # Preconfigure chains for better performance
        self._single_chain = self._create_single_analysis_chain()
        self._batch_chain = self._create_batch_analysis_chain()

    def _create_single_analysis_chain(self):
        """Create chain for single text sentiment analysis."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{text}")
        ])

        # Use JSON output parser for structured output
        parser = JsonOutputParser()
        chain = prompt | self.client.llm | parser
        return chain

    def _create_batch_analysis_chain(self):
        """Create chain for batch sentiment analysis."""
        prompt_template = create_batch_sentiment_prompt_template()
        chain = prompt_template | self.client.llm | StrOutputParser()
        return chain

    async def analyze_sentiment(
        self,
        text: str,
        use_map_reduce: bool = False
    ) -> Dict:
        """
        Analyze sentiment of a single text.

        Args:
            text: Text to analyze
            use_map_reduce: Use Map-Reduce for long texts (>3000 tokens)

        Returns:
            Dict with score, label, confidence, reasoning
        """
        # Preprocess text
        cleaned_text = TextPreprocessor.clean_for_analysis(text, max_length=2000)

        # Check if text is too long
        token_count = TokenCounter.count_tokens(cleaned_text, self.client.model)

        if token_count > 3000 and use_map_reduce:
            return await self._analyze_with_map_reduce(cleaned_text)

        # Use single analysis chain
        try:
            self.client.logger.start_operation("sentiment_analysis_single")

            result = await self._single_chain.ainvoke({"text": cleaned_text})

            # Validate and normalize result
            result = self._validate_result(result)

            self.client.logger.end_operation("sentiment_analysis_single")
            return result

        except Exception as e:
            self.logger.error(f"Error analyzing sentiment: {e}")
            return self._get_default_result("Analysis failed")

    async def _analyze_with_map_reduce(self, text: str) -> Dict:
        """
        Analyze long text using Map-Reduce pattern.

        Args:
            text: Long text to analyze

        Returns:
            Aggregated sentiment analysis
        """
        from .utils import MapReduceProcessor

        self.logger.info("Using Map-Reduce for long text sentiment analysis")

        processor = MapReduceProcessor(
            max_tokens_per_chunk=1500,
            overlap=100
        )

        # Map phase: analyze each chunk
        async def map_sentiment(chunk: str) -> Dict:
            try:
                result = await self._single_chain.ainvoke({"text": chunk})
                return self._validate_result(result)
            except Exception as e:
                self.logger.error(f"Error in map phase: {e}")
                return {"score": 50, "label": "neutral", "confidence": 0.0}

        # Reduce phase: aggregate results
        async def reduce_sentiment(results: List[Dict]) -> Dict:
            if not results:
                return self._get_default_result("No results")

            # Average scores
            avg_score = sum(r["score"] for r in results) / len(results)

            # Determine label based on average
            if avg_score >= 60:
                label = "positive"
            elif avg_score >= 40:
                label = "neutral"
            else:
                label = "negative"

            # Average confidence
            avg_confidence = sum(r.get("confidence", 0.5) for r in results) / len(results)

            return {
                "score": int(avg_score),
                "label": label,
                "confidence": round(avg_confidence, 2),
                "reasoning": f"Aggregated from {len(results)} chunks"
            }

        # Execute Map-Reduce
        result = await processor.process(text, map_sentiment, reduce_sentiment, "sentiment_map_reduce")
        return result

    async def analyze_batch(
        self,
        texts: List[str],
        use_map_reduce: bool = False
    ) -> List[Dict]:
        """
        Analyze sentiment for multiple texts efficiently.

        Args:
            texts: List of texts to analyze
            use_map_reduce: Use Map-Reduce for large batches

        Returns:
            List of sentiment analysis results
        """
        if not texts:
            return []

        self.client.logger.start_operation("sentiment_analysis_batch")

        # Preprocess texts
        cleaned_texts = [
            TextPreprocessor.clean_for_analysis(text, max_length=1000)
            for text in texts
        ]

        # Estimate total tokens
        total_tokens = TokenCounter.count_tokens_batch(cleaned_texts, self.client.model)

        # Decide on strategy based on token count
        if total_tokens > 4000 or use_map_reduce:
            results = await self._analyze_batch_map_reduce(cleaned_texts)
        else:
            results = await self._analyze_batch_direct(cleaned_texts)

        self.client.logger.end_operation("sentiment_analysis_batch")
        return results

    async def _analyze_batch_direct(self, texts: List[str]) -> List[Dict]:
        """Analyze batch using single API call."""
        # Build batch prompt
        posts_text = "\n".join(f"{i+1}. {text}" for i, text in enumerate(texts))

        try:
            prompt = self._batch_chain.invoke({"posts": posts_text})

            # Parse JSON array
            import json
            import re

            json_match = re.search(r'\[.*\]', prompt, re.DOTALL)
            if json_match:
                results = json.loads(json_match.group(0))
            else:
                results = json.loads(prompt)

            # Validate results
            return [self._validate_result(r) for r in results]

        except Exception as e:
            self.logger.error(f"Error in direct batch analysis: {e}")
            # Fallback to individual analysis
            return await self._analyze_individually(texts)

    async def _analyze_batch_map_reduce(self, texts: List[str]) -> List[Dict]:
        """Analyze batch using Map-Reduce pattern."""
        from .utils import MapReduceProcessor

        self.logger.info("Using Map-Reduce for batch sentiment analysis")

        processor = MapReduceProcessor(
            max_tokens_per_chunk=2000,
            batch_size=5
        )

        # Split texts into batches
        batches = processor.split_posts(
            [{"content": text} for text in texts]
        )

        # Map phase: analyze each batch
        async def map_batch(posts: List[Dict]) -> List[Dict]:
            batch_texts = [p["content"] for p in posts]
            return await self._analyze_batch_direct(batch_texts)

        # Reduce phase: flatten results
        async def reduce_batch(results: List[List[Dict]]) -> List[Dict]:
            flattened = []
            for batch_results in results:
                flattened.extend(batch_results)
            return flattened

        # Execute Map-Reduce
        final_results = await processor.reduce_phase(
            batches,
            map_batch,
            "sentiment_batch_map"
        )

        # Flatten results
        all_results = []
        for batch_result in final_results:
            all_results.extend(batch_result)

        return all_results

    async def _analyze_individually(self, texts: List[str]) -> List[Dict]:
        """Fallback: analyze each text individually."""
        results = []
        for i, text in enumerate(texts):
            self.logger.log_batch_progress("individual_analysis", i + 1, len(texts))
            result = await self.analyze_sentiment(text)
            results.append(result)
        return results

    def _validate_result(self, result: Dict) -> Dict:
        """Validate and normalize sentiment result."""
        required_keys = ["score", "label", "confidence"]

        for key in required_keys:
            if key not in result:
                self.logger.warning(f"Missing key '{key}' in result")
                result[key] = {"score": 50, "label": "neutral", "confidence": 0.5}[key]

        # Add reasoning if missing
        if "reasoning" not in result:
            result["reasoning"] = "Sentiment analysis completed"

        # Ensure score is in valid range
        result["score"] = max(0, min(100, int(result.get("score", 50))))

        # Ensure valid label
        valid_labels = ["positive", "negative", "neutral"]
        if result["label"] not in valid_labels:
            # Infer label from score
            score = result["score"]
            if score >= 60:
                result["label"] = "positive"
            elif score >= 40:
                result["label"] = "neutral"
            else:
                result["label"] = "negative"

        return result

    def _get_default_result(self, reasoning: str) -> Dict:
        """Get default sentiment result."""
        return {
            "score": 50,
            "label": "neutral",
            "confidence": 0.0,
            "reasoning": reasoning
        }

    def calculate_overall_sentiment(self, sentiment_scores: List[float]) -> float:
        """
        Calculate overall sentiment from multiple scores.

        Args:
            sentiment_scores: List of sentiment scores (0-100)

        Returns:
            Weighted average sentiment score
        """
        if not sentiment_scores:
            return 50.0

        return round(sum(sentiment_scores) / len(sentiment_scores), 1)

    def log_summary(self):
        """Log token usage summary."""
        self.client.log_summary()
