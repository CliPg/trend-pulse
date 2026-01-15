"""
Logging utility for AI analysis with token tracking.
"""
import logging
import time
from typing import Optional, Dict, Any
from datetime import datetime


class AnalysisLogger:
    """Logger for AI analysis operations with token tracking."""

    def __init__(self, name: str = "ai_analysis"):
        """
        Initialize analysis logger.

        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Console handler
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Token tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_estimate = 0.0
        self.api_calls = 0

        # Operation timing
        self.operation_start_time: Optional[float] = None
        self.operation_durations: Dict[str, float] = {}

    def log_api_call(
        self,
        operation: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an API call with token usage.

        Args:
            operation: Operation name (e.g., "sentiment_analysis")
            model: Model name (e.g., "gpt-4o-mini")
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            duration: Request duration in seconds
            metadata: Additional metadata
        """
        self.api_calls += 1
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        # Estimate cost (OpenAI pricing as of 2025)
        cost_per_1k_input, cost_per_1k_output = self._get_pricing(model)
        cost = (input_tokens / 1000) * cost_per_1k_input + \
               (output_tokens / 1000) * cost_per_1k_output
        self.total_cost_estimate += cost

        # Log the call
        meta_str = ""
        if metadata:
            meta_str = f" | Metadata: {metadata}"

        self.logger.info(
            f"API Call [{operation}] | "
            f"Model: {model} | "
            f"Input: {input_tokens:,} tokens | "
            f"Output: {output_tokens:,} tokens | "
            f"Duration: {duration:.2f}s | "
            f"Cost: ${cost:.4f}{meta_str}"
        )

    def _get_pricing(self, model: str) -> tuple[float, float]:
        """
        Get pricing per 1K tokens for a model.

        Args:
            model: Model name

        Returns:
            (input_cost_per_1k, output_cost_per_1k)
        """
        # OpenAI pricing (as of 2025)
        openai_pricing = {
            "gpt-4o": (2.50, 10.00),
            "gpt-4o-mini": (0.15, 0.60),
            "gpt-4-turbo": (10.00, 30.00),
            "gpt-3.5-turbo": (0.50, 1.50),
        }

        # Tongyi pricing (estimated)
        tongyi_pricing = {
            "qwen-plus": (0.004, 0.006),  # ~¥0.04/1K input, ¥0.06/1K output
            "qwen-turbo": (0.001, 0.002),
            "qwen-max": (0.02, 0.06),
        }

        if model in openai_pricing:
            return openai_pricing[model]
        elif model in tongyi_pricing:
            return tongyi_pricing[model]
        else:
            # Default to conservative estimate
            return (0.50, 1.50)

    def start_operation(self, operation_name: str):
        """
        Start timing an operation.

        Args:
            operation_name: Name of the operation
        """
        self.operation_start_time = time.time()
        self.logger.info(f"Starting operation: {operation_name}")

    def end_operation(self, operation_name: str):
        """
        End timing an operation.

        Args:
            operation_name: Name of the operation
        """
        if self.operation_start_time:
            duration = time.time() - self.operation_start_time
            self.operation_durations[operation_name] = duration
            self.logger.info(
                f"Completed operation: {operation_name} | Duration: {duration:.2f}s"
            )
            self.operation_start_time = None

    def log_batch_progress(
        self,
        operation: str,
        current: int,
        total: int,
        batch_size: int = None
    ):
        """
        Log batch processing progress.

        Args:
            operation: Operation name
            current: Current batch number
            total: Total batches
            batch_size: Size of each batch
        """
        percentage = (current / total) * 100
        batch_str = f" (batch size: {batch_size})" if batch_size else ""
        self.logger.info(
            f"[{operation}] Progress: {current}/{total} "
            f"({percentage:.1f}%){batch_str}"
        )

    def log_token_summary(self):
        """Log summary of token usage and costs."""
        self.logger.info("=" * 60)
        self.logger.info("TOKEN USAGE SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total API Calls: {self.api_calls}")
        self.logger.info(f"Total Input Tokens: {self.total_input_tokens:,}")
        self.logger.info(f"Total Output Tokens: {self.total_output_tokens:,}")
        self.logger.info(f"Total Tokens: {self.total_input_tokens + self.total_output_tokens:,}")
        self.logger.info(f"Estimated Cost: ${self.total_cost_estimate:.4f}")

        if self.operation_durations:
            total_time = sum(self.operation_durations.values())
            self.logger.info(f"Total Time: {total_time:.2f}s")
            self.logger.info("\nOperation Breakdown:")
            for op, duration in self.operation_durations.items():
                self.logger.info(f"  - {op}: {duration:.2f}s")

        self.logger.info("=" * 60)

    def reset_token_tracking(self):
        """Reset token tracking counters."""
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost_estimate = 0.0
        self.api_calls = 0
        self.operation_durations = {}

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)


# Global logger instance
_analysis_logger = None


def get_analysis_logger() -> AnalysisLogger:
    """
    Get or create the global analysis logger.

    Returns:
        AnalysisLogger instance
    """
    global _analysis_logger
    if _analysis_logger is None:
        _analysis_logger = AnalysisLogger()
    return _analysis_logger
