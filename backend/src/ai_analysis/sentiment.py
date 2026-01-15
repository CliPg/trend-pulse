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

            # Debug: Log raw response
            print(f"📝 Raw LLM response (first 200 chars): {response[:200]}")

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{[^{}]*"score"[^{}]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                # Try parsing the whole response
                result = json.loads(response)

            # Validate result structure
            required_keys = ["score", "label", "confidence", "reasoning"]
            for key in required_keys:
                if key not in result:
                    print(f"⚠️  Missing key '{key}' in response, using default")
                    result[key] = {"score": 50, "label": "neutral", "confidence": 0.0, "reasoning": "Missing key"}[key]

            return result

        except json.JSONDecodeError as e:
            print(f"❌ JSON parse error: {e}")
            print(f"   Response was: {response[:300]}")
            return {
                "score": 50,
                "label": "neutral",
                "confidence": 0.0,
                "reasoning": "JSON parse failed",
            }
        except Exception as e:
            print(f"❌ Error analyzing sentiment: {e}")
            import traceback
            traceback.print_exc()
            return {
                "score": 50,
                "label": "neutral",
                "confidence": 0.0,
                "reasoning": f"Analysis failed: {str(e)}",
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

        print(f"📊 Processing {len(texts)} texts in batches of {batch_size}...")

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(texts) + batch_size - 1) // batch_size

            print(f"🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} texts)...")

            # Create batch prompt
            batch_prompt = f"{self.system_prompt}\n\n"
            batch_prompt += (
                "Analyze these texts and return ONLY a JSON array of sentiment objects:\n"
            )
            batch_prompt += "Format: [{\"score\": 0-100, \"label\": \"positive|negative|neutral\", \"confidence\": 0-1, \"reasoning\": \"...\"}, ...]\n\n"

            for j, text in enumerate(batch, 1):
                # Truncate long texts to avoid token limit
                truncated_text = text[:500] if len(text) > 500 else text
                batch_prompt += f"{j}. {truncated_text}\n"

            messages = [
                {"role": "system", "content": "You are a sentiment analysis expert. Always respond with valid JSON only."},
                {"role": "user", "content": batch_prompt},
            ]

            try:
                response = await self.client.chat_completion(
                    messages, temperature=0.3
                )

                print(f"📝 Batch {batch_num} response received (length: {len(response)} chars)")

                # Parse JSON array response
                import json
                import re

                # Try to extract JSON array from response
                json_match = re.search(r'\[.*\]', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    batch_results = json.loads(json_str)
                    results.extend(batch_results)
                    print(f"✓ Batch {batch_num} completed: {len(batch_results)} results")
                else:
                    # Try parsing the whole response
                    batch_results = json.loads(response)
                    results.extend(batch_results)
                    print(f"✓ Batch {batch_num} completed: {len(batch_results)} results")

            except Exception as e:
                print(f"❌ Error in batch {batch_num} analysis: {e}")
                print(f"   Falling back to individual analysis for this batch...")
                # Fallback to individual analysis
                for text in batch:
                    result = await self.analyze_sentiment(text)
                    results.append(result)

        print(f"✅ Batch analysis completed: {len(results)} total results")
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
