"""
LangChain-based LLM client with token tracking and cost estimation.
Supports OpenAI and Tongyi Qianwen providers.
"""
from typing import List, Dict, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import Runnable
import time
import json

from src.config import Config
from .utils import get_analysis_logger, TokenCounter


class LangChainLLMClient:
    """LangChain-based LLM client with enhanced features."""

    def __init__(
        self,
        provider: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        """
        Initialize LangChain LLM client.

        Args:
            provider: LLM provider ('openai', 'tongyi')
            temperature: Default temperature
            max_tokens: Default max tokens
        """
        self.provider = provider or Config.LLM_PROVIDER
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.logger = get_analysis_logger()

        # Configure LLM based on provider
        self.llm = self._create_llm()
        self.model = self.llm.model_name

        self.logger.info(f"Initialized LangChain client with provider: {self.provider}, model: {self.model}")

    def _create_llm(self) -> ChatOpenAI:
        """Create ChatOpenAI instance based on provider configuration."""
        if self.provider == "openai":
            api_key = Config.OPENAI_API_KEY or Config.LLM_API_KEY
            base_url = Config.OPENAI_BASE_URL
            model = Config.OPENAI_MODEL
            self.logger.info("🔧 Using OpenAI LLM provider")
        else:  # tongyi (default)
            api_key = Config.TONGYI_API_KEY or Config.LLM_API_KEY
            base_url = Config.TONGYI_BASE_URL
            model = Config.TONGYI_MODEL
            self.logger.info("🔧 Using Tongyi LLM provider")

        if not api_key:
            raise ValueError(f"LLM API key not configured for provider '{self.provider}'")

        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=30.0,
        )

    async def invoke(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        operation: str = "llm_invoke"
    ) -> str:
        """
        Invoke LLM with a simple prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override temperature
            max_tokens: Override max tokens
            operation: Operation name for logging

        Returns:
            LLM response text
        """
        # Build messages
        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        return await self.chat(messages, temperature, max_tokens, operation)

    async def chat(
        self,
        messages: List[BaseMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        operation: str = "llm_chat"
    ) -> str:
        """
        Send chat messages to LLM.

        Args:
            messages: List of LangChain messages
            temperature: Override temperature
            max_tokens: Override max tokens
            operation: Operation name for logging

        Returns:
            LLM response text
        """
        # Create LLM with custom parameters if provided
        llm = self.llm
        if temperature is not None or max_tokens is not None:
            llm = self.llm.bind(
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )

        # Estimate input tokens
        input_text = "\n".join(m.content for m in messages)
        input_tokens = TokenCounter.count_tokens(input_text, self.model)

        # Start timing
        start_time = time.time()

        try:
            # Invoke LLM
            response: AIMessage = await llm.ainvoke(messages)

            # Calculate metrics
            duration = time.time() - start_time

            # Estimate tokens (LangChain doesn't always return token usage)
            output_tokens = TokenCounter.count_tokens(response.content, self.model)

            # Log API call
            self.logger.log_api_call(
                operation=operation,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration=duration
            )

            return response.content

        except Exception as e:
            self.logger.error(f"LLM invocation error: {e}")
            raise

    async def invoke_with_retry(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_retries: int = 3,
        operation: str = "llm_invoke_retry"
    ) -> str:
        """
        Invoke LLM with automatic retry on failure.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_retries: Maximum retry attempts
            operation: Operation name for logging

        Returns:
            LLM response text
        """
        for attempt in range(max_retries):
            try:
                return await self.invoke(prompt, system_prompt, operation=operation)
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}"
                    )
                    import asyncio
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Failed after {max_retries} attempts: {e}")
                    raise

        raise Exception("Should not reach here")

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        operation: str = "llm_json"
    ) -> Dict[str, Any]:
        """
        Invoke LLM and parse response as JSON.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override temperature
            operation: Operation name for logging

        Returns:
            Parsed JSON response
        """
        # Build messages with JSON instructions
        messages: List[BaseMessage] = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))

        # Invoke LLM
        response_text = await self.chat(messages, temperature, operation=operation)

        # Parse JSON
        try:
            # Try direct parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            # Try JSON array
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            # If all fails, raise error
            self.logger.error(f"Failed to parse JSON from response: {response_text[:200]}")
            raise ValueError(f"Could not parse JSON from LLM response")

    def create_chain(
        self,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Runnable:
        """
        Create a LangChain chain for repeated use.

        Args:
            system_prompt: Optional system prompt
            temperature: Override temperature

        Returns:
            Configured LangChain chain
        """
        parser = StrOutputParser()

        if system_prompt:
            template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
        else:
            template = ChatPromptTemplate.from_messages([
                ("human", "{input}")
            ])

        llm = self.llm
        if temperature is not None:
            llm = llm.bind(temperature=temperature)

        chain = template | llm | parser
        return chain

    async def run_chain(
        self,
        chain: Runnable,
        inputs: Dict[str, Any],
        operation: str = "chain_run"
    ) -> str:
        """
        Run a pre-configured chain.

        Args:
            chain: LangChain chain
            inputs: Input values for the chain
            operation: Operation name for logging

        Returns:
            Chain output
        """
        # Estimate input tokens
        input_text = str(inputs)
        input_tokens = TokenCounter.count_tokens(input_text, self.model)

        start_time = time.time()

        try:
            result = await chain.ainvoke(inputs)

            duration = time.time() - start_time
            output_tokens = TokenCounter.count_tokens(str(result), self.model)

            self.logger.log_api_call(
                operation=operation,
                model=self.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration=duration
            )

            return result

        except Exception as e:
            self.logger.error(f"Chain execution error: {e}")
            raise

    async def batch_process(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        operation: str = "batch_process"
    ) -> List[str]:
        """
        Process multiple prompts in batch.

        Args:
            prompts: List of user prompts
            system_prompt: Optional system prompt
            operation: Operation name for logging

        Returns:
            List of responses
        """
        results = []

        for i, prompt in enumerate(prompts):
            self.logger.log_batch_progress(operation, i + 1, len(prompts))
            try:
                result = await self.invoke(
                    prompt,
                    system_prompt,
                    operation=f"{operation}_{i}"
                )
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error processing prompt {i}: {e}")
                results.append(None)

        return results

    def get_token_summary(self) -> Dict[str, int]:
        """
        Get token usage summary.

        Returns:
            Dict with total_input_tokens, total_output_tokens, total_cost
        """
        return {
            "total_input_tokens": self.logger.total_input_tokens,
            "total_output_tokens": self.logger.total_output_tokens,
            "total_tokens": self.logger.total_input_tokens + self.logger.total_output_tokens,
            "estimated_cost": self.logger.total_cost_estimate,
            "api_calls": self.logger.api_calls
        }

    def log_summary(self):
        """Log token usage summary."""
        self.logger.log_token_summary()
