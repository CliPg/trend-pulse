"""
Opinion clustering prompts with Few-shot examples.
"""
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from typing import List, Dict


# Few-shot examples for opinion clustering
CLUSTERING_EXAMPLES = [
    {
        "posts": """
        1. "The price is too high for what you get"
        2. "Way too expensive, not worth it"
        3. "Pricing is reasonable for the quality"
        4. "Cost is a bit steep but acceptable"
        """,
        "clusters": [
            {
                "label": "Price Concerns",
                "summary": "Users discussing the high price and questioning value for money",
                "mention_count": 3
            }
        ]
    },
    {
        "posts": """
        1. "Build quality is excellent, very sturdy"
        2. "The materials feel cheap and break easily"
        3. "Great construction, feels premium"
        4. "Poor build quality, fell apart after a week"
        """,
        "clusters": [
            {
                "label": "Build Quality",
                "summary": "Mixed opinions on product construction and material quality",
                "mention_count": 4
            }
        ]
    },
]


def create_clustering_prompt_template() -> PromptTemplate:
    """
    Create prompt template for opinion clustering.

    Returns:
        PromptTemplate configured for clustering
    """
    template = """You are an expert at identifying and clustering opinions from social media discussions. Your task is to analyze the posts and identify the main themes and discussion points.

Guidelines:
1. Focus on DISTINCT themes and topics (not sentiment)
2. Identify points of agreement, controversy, or debate
3. Extract common concerns, praise, or questions
4. Each cluster should represent a unique discussion topic

Output format (JSON only):
{{
  "clusters": [
    {{
      "label": "<brief 2-4 word theme label>",
      "summary": "<2-3 sentence description of this opinion cluster>",
      "mention_count": <estimated number of posts about this topic>,
      "sample_quotes": ["<representative quote 1>", "<representative quote 2>"]
    }}
  ],
  "dominant_sentiment": "<overall positive/negative/neutral/mixed>"
}}

Example:
Posts: [
  "The battery life is terrible, dies in 2 hours",
  "Great battery, lasts all day",
  "Battery could be better but it's okay"
]

Response:
{{
  "clusters": [
    {{
      "label": "Battery Life",
      "summary": "Users have mixed opinions about battery performance, with some experiencing poor life and others satisfied",
      "mention_count": 3,
      "sample_quotes": ["battery life is terrible", "Great battery, lasts all day"]
    }}
  ],
  "dominant_sentiment": "mixed"
}}

Now analyze these {post_count} social media posts and identify the top {top_n} opinion clusters:

{posts}

Response (JSON only):"""

    return PromptTemplate(
        template=template,
        input_variables=["post_count", "top_n", "posts"]
    )


def get_clustering_system_prompt() -> str:
    """
    Get system prompt for opinion clustering.

    Returns:
        System prompt string
    """
    return """You are an expert conversation analyst specializing in social media discussions. Your role is to identify and group similar opinions, themes, and discussion points.

Key principles:
1. Thematic coherence: Group posts discussing the same topic
2. Semantic similarity: Look for similar concepts (not exact word matches)
3. Sentiment independence: clusters can contain mixed opinions
4. Relevance: Filter out spam, ads, and off-topic content

Best practices:
- Create 3-5 distinct clusters maximum
- Ensure clusters are mutually exclusive
- Use clear, descriptive labels
- Extract representative quotes that capture the essence
- Count mentions based on relevance, not just keyword presence

Output a structured JSON response with clusters array and dominant sentiment."""
