"""
Summarization prompts with Few-shot examples.
"""
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from typing import List, Dict


# Few-shot examples for summarization
SUMMARIZATION_EXAMPLES = [
    {
        "context": "Product review discussion with overall sentiment of positive (75/100)",
        "posts": """
        - "Love this product! Best purchase ever"
        - "Great quality, fast shipping"
        - "A bit pricey but worth it"
        - "Customer service was excellent"
        """,
        "summary": """Customers are overwhelmingly positive about this product, frequently praising its quality and the fast shipping experience. While some mention the premium pricing, most feel the value justifies the cost. The exceptional customer service also stands out as a key factor in customer satisfaction."""
    },
    {
        "context": "Software feature discussion with overall sentiment of neutral (50/100)",
        "posts": """
        - "The new UI is confusing"
        - "I like the dark mode addition"
        - "Too many bugs in this version"
        - "Performance is better than before"
        """,
        "summary": """User reactions to the latest software update are mixed, with opinions divided across several aspects. The redesigned user interface has drawn criticism for being confusing, though the new dark mode feature has been well received. Technical issues, particularly bugs, remain a concern, while performance improvements have been noted as a positive step."""
    },
]


def create_summarization_prompt_template() -> PromptTemplate:
    """
    Create prompt template for discussion summarization.

    Returns:
        PromptTemplate configured for summarization
    """
    template = """You are an expert at synthesizing social media discussions into clear, concise summaries. Your task is to create a 2-3 paragraph summary that captures the essence of the conversation.

Summary requirements:
1. Main topics and themes being discussed
2. Overall sentiment and emotional tone
3. Key points of consensus or controversy
4. Notable trends, patterns, or frequently mentioned aspects
5. Write in natural, flowing paragraphs (NOT bullet points)
6. Keep it concise but comprehensive

Context:
- Overall sentiment: {sentiment_description} ({sentiment_score}/100)
- Number of posts: {post_count}
- Platform: {platform}

Representative posts to analyze:
{posts}

Generate a 2-3 paragraph summary:"""

    return PromptTemplate(
        template=template,
        input_variables=["sentiment_description", "sentiment_score", "post_count", "platform", "posts"]
    )


def create_map_prompt() -> PromptTemplate:
    """
    Create prompt for Map phase of Map-Reduce summarization.

    Returns:
        PromptTemplate for map phase
    """
    template = """Analyze the following social media posts and extract key points:

Posts:
{posts}

Provide a structured summary of the main points, themes, and opinions in these posts. Focus on:
- Main topics discussed
- Key opinions expressed
- Notable sentiment indicators

Structured summary:"""

    return PromptTemplate(
        template=template,
        input_variables=["posts"]
    )


def create_reduce_prompt() -> PromptTemplate:
    """
    Create prompt for Reduce phase of Map-Reduce summarization.

    Returns:
        PromptTemplate for reduce phase
    """
    template = """You are synthesizing a social media discussion from multiple analyses.

Overall sentiment: {sentiment_description} ({sentiment_score}/100)

Individual summaries from different post groups:
{summaries}

Create a coherent 2-3 paragraph summary that:
1. Synthesizes all the key points
2. Identifies main themes and trends
3. Captures the overall sentiment and emotional tone
4. Highlights areas of agreement and controversy
5. Flows naturally (not a bulleted list)

Final summary:"""

    return PromptTemplate(
        template=template,
        input_variables=["sentiment_description", "sentiment_score", "summaries"]
    )


def get_summarization_system_prompt() -> str:
    """
    Get system prompt for summarization.

    Returns:
        System prompt string
    """
    return """You are an expert at analyzing and synthesizing social media discussions. Your role is to create clear, engaging summaries that capture the essence of online conversations.

Writing principles:
1. Start with the big picture (main themes, overall sentiment)
2. Dive into specific points of discussion
3. Highlight consensus and disagreement
4. Use natural transitions between topics
5. Avoid jargon and overly technical language
6. Keep it readable and engaging

Style guidelines:
- Write in flowing paragraphs (2-3 paragraphs total)
- Use varied sentence structure for readability
- Include representative quotes when relevant
- Balance objectivity with capturing the emotional tone
- Be concise but comprehensive

Your goal is to give readers a clear understanding of what people are saying and how they feel about the topic."""
