"""
LLM API client for AI analysis.
Supports Tongyi Qianwen (Alibaba's Qwen model) via OpenAI-compatible API.
"""
from typing import List, Dict
import aiohttp
import asyncio
import json
from src.config import Config


class LLMClient:
    """Client for interacting with LLM API (Tongyi Qianwen)."""

    def __init__(self):
        """Initialize LLM client with configuration from environment."""
        self.api_key = Config.LLM_API_KEY
        self.base_url = Config.LLM_API_BASE_URL
        self.model = Config.LLM_MODEL

        if not self.api_key:
            print("⚠️  Warning: LLM API key not configured in environment")
            print("   Please set LLM_API_KEY in your .env file")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        retry_count: int = 3,
    ) -> str:
        """
        Send chat completion request to LLM with retry mechanism.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            retry_count: Number of retries on failure

        Returns:
            Response text
        """
        if not self.api_key:
            raise ValueError("LLM API key not configured. Please set LLM_API_KEY in .env file")

        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        for attempt in range(retry_count):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            print(f"❌ LLM API error (status {response.status}): {error_text[:200]}")
                            if attempt < retry_count - 1:
                                print(f"   Retrying... ({attempt + 1}/{retry_count})")
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                                continue
                            raise Exception(f"LLM API error after {retry_count} attempts: {error_text}")

                        data = await response.json()

                        # Extract response content
                        if "choices" not in data or not data["choices"]:
                            print(f"❌ Invalid API response format: {json.dumps(data, indent=2)[:500]}")
                            if attempt < retry_count - 1:
                                print(f"   Retrying... ({attempt + 1}/{retry_count})")
                                await asyncio.sleep(2 ** attempt)
                                continue
                            raise Exception("Invalid API response: missing 'choices' field")

                        content = data["choices"][0]["message"]["content"]

                        # Debug: Log response length
                        if len(content) < 50:
                            print(f"⚠️  Short response from LLM: '{content}'")

                        return content

            except aiohttp.ClientError as e:
                print(f"❌ Network error: {e}")
                if attempt < retry_count - 1:
                    print(f"   Retrying... ({attempt + 1}/{retry_count})")
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"Network error after {retry_count} attempts: {e}")

            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                if attempt < retry_count - 1:
                    print(f"   Retrying... ({attempt + 1}/{retry_count})")
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise Exception(f"JSON decode error after {retry_count} attempts: {e}")

        raise Exception(f"Failed after {retry_count} retry attempts")

    async def analyze_batch(
        self, texts: List[str], system_prompt: str, temperature: float = 0.7
    ) -> List[str]:
        """
        Analyze multiple texts in batch (more efficient).

        Args:
            texts: List of texts to analyze
            system_prompt: System prompt for analysis
            temperature: Sampling temperature

        Returns:
            List of analysis results
        """
        # Combine texts into single request for efficiency
        combined_prompt = f"{system_prompt}\n\nAnalyze these texts:\n"
        for i, text in enumerate(texts, 1):
            combined_prompt += f"\n{i}. {text[:500]}"  # Truncate long texts

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": combined_prompt},
        ]

        response = await self.chat_completion(messages, temperature)
        return response
