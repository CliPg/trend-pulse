"""
LLM API client for AI analysis.
Supports Tongyi Qianwen (Alibaba's Qwen model) via OpenAI-compatible API.
"""
from typing import List, Dict
import aiohttp
from src.config import Config


class LLMClient:
    """Client for interacting with LLM API (Tongyi Qianwen)."""

    def __init__(self):
        """Initialize LLM client with configuration from environment."""
        self.api_key = Config.LLM_API_KEY
        self.base_url = Config.LLM_API_BASE_URL
        self.model = Config.LLM_MODEL

        if not self.api_key:
            raise ValueError("LLM API key not configured")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        Send chat completion request to LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response

        Returns:
            Response text
        """
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

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"LLM API error: {error_text}")

                data = await response.json()

        return data["choices"][0]["message"]["content"]

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
