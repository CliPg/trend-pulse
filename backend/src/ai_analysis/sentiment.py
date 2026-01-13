"""
Sentiment analysis module using LLM.
Analyzes sentiment of social media posts on a 0-100 scale.
"""
from typing import List, Dict
from src.ai_analysis.client import LLMClient


class SentimentAnalyzer:
    """Analyzes sentiment of social media posts."""

    def __init__(self):
        """Initialize sentiment analyzer with LLM client."""
        self.client = LLMClient()
        self.system_prompt = """You are a sentiment analysis expert.
Analyze the sentiment of the given text and respond with ONLY a JSON object in this format:
{
  "score": <0-100 integer>,
  "label": "<positive|negative|neutral>",
  "confidence": <0-1 float>,
  "reasoning": "<brief explanation>"
}

Score guide:
- 0-20: Extremely negative
- 21-40: Negative
- 41-60: Neutral
- 61-80: Positive
- 81-100: Extremely positive

Consider:
- Overall emotional tone
- Specific keywords and phrases
- Context and intent
- Sarcasm and nuance"""

    async def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text.

        Args:
            text: Text to analyze

        Returns:
            Dict with score, label, confidence, reasoning
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Analyze sentiment: {text}"},
        ]

        try:
            response = await self.client.chat_completion(
                messages, temperature=0.3  # Low temperature for consistency
            )

            # Parse JSON response
            import json

            result = json.loads(response)
            return result

        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                "score": 50,
                "label": "neutral",
                "confidence": 0.0,
                "reasoning": "Analysis failed",
            }

    async def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment for multiple texts efficiently.

        Args:
            texts: List of texts to analyze

        Returns:
            List of sentiment analysis results
        """
        # Process in batches to control token usage
        batch_size = 10
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            # Create batch prompt
            batch_prompt = f"{self.system_prompt}\n\n"
            batch_prompt += (
                "Analyze these texts and return a JSON array of sentiment objects:\n"
            )

            for j, text in enumerate(batch, 1):
                batch_prompt += f"\n{j}. {text[:500]}"

            messages = [
                {"role": "system", "content": "You are a sentiment analysis expert."},
                {"role": "user", "content": batch_prompt},
            ]

            try:
                response = await self.client.chat_completion(
                    messages, temperature=0.3
                )

                # Parse JSON array response
                import json

                batch_results = json.loads(response)
                results.extend(batch_results)

            except Exception as e:
                print(f"Error in batch analysis: {e}")
                # Fallback to individual analysis
                for text in batch:
                    result = await self.analyze_sentiment(text)
                    results.append(result)

        return results

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

        # Simple average (can be enhanced with engagement weighting)
        return sum(sentiment_scores) / len(sentiment_scores)
