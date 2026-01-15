"""
Prompt templates for AI analysis modules.
"""
from .sentiment_prompts import (
    create_sentiment_prompt_template,
    create_batch_sentiment_prompt_template,
    get_sentiment_system_prompt,
    SENTIMENT_EXAMPLES
)
from .clustering_prompts import (
    create_clustering_prompt_template,
    get_clustering_system_prompt,
    CLUSTERING_EXAMPLES
)
from .summarization_prompts import (
    create_summarization_prompt_template,
    create_map_prompt,
    create_reduce_prompt,
    get_summarization_system_prompt,
    SUMMARIZATION_EXAMPLES
)

__all__ = [
    # Sentiment
    "create_sentiment_prompt_template",
    "create_batch_sentiment_prompt_template",
    "get_sentiment_system_prompt",
    "SENTIMENT_EXAMPLES",

    # Clustering
    "create_clustering_prompt_template",
    "get_clustering_system_prompt",
    "CLUSTERING_EXAMPLES",

    # Summarization
    "create_summarization_prompt_template",
    "create_map_prompt",
    "create_reduce_prompt",
    "get_summarization_system_prompt",
    "SUMMARIZATION_EXAMPLES",
]
