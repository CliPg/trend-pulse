"""
Sentiment analysis prompts with Few-shot examples.
"""
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from typing import List, Dict


# Few-shot examples for sentiment analysis
SENTIMENT_EXAMPLES = [
    {
        "text": "This product is absolutely amazing! Best purchase I've ever made. Highly recommend to everyone!",
        "score": 95,
        "label": "positive",
        "reasoning": "Strong positive words (amazing, best, highly recommend) with exclamation marks indicate very positive sentiment"
    },
    {
        "text": "Terrible experience. The product broke after one day and customer service was unhelpful.",
        "score": 15,
        "label": "negative",
        "reasoning": "Negative words (terrible, broke, unhelpful) with specific complaints indicate extremely negative sentiment"
    },
    {
        "text": "The product is okay. It does what it's supposed to do, but nothing special.",
        "score": 50,
        "label": "neutral",
        "reasoning": "Moderate language (okay, supposed to do) without strong emotion indicates neutral sentiment"
    },
    {
        "text": "Pretty good overall. I like the design but the price is a bit high.",
        "score": 68,
        "label": "positive",
        "reasoning": "Positive elements (pretty good, like design) outweigh negative (price high), resulting in mildly positive sentiment"
    },
    {
        "text": "Not great, not terrible. It has some issues but works most of the time.",
        "score": 42,
        "label": "neutral",
        "reasoning": "Balanced positive and negative elements with moderate language suggest slightly below neutral sentiment"
    },
    {
        "text": "Worst mistake of my life buying this. Complete waste of money. Do NOT buy!",
        "score": 5,
        "label": "negative",
        "reasoning": "Extreme negative language (worst mistake, waste of money, do not buy) with caps indicates extremely negative sentiment"
    },
    {
        "text": "I'm so happy with this! Exceeded all my expectations. Will definitely buy again!",
        "score": 90,
        "label": "positive",
        "reasoning": "Strong positive emotional language (happy, exceeded expectations) with future commitment indicates very positive sentiment"
    },
    {
        "text": "Could be better. There are some good features but too many bugs.",
        "score": 35,
        "label": "negative",
        "reasoning": "Mixed sentiment leaning negative, with acknowledgment of good features but emphasis on problems"
    },
]


def create_sentiment_prompt_template() -> FewShotPromptTemplate:
    """
    Create Few-shot prompt template for sentiment analysis.

    Returns:
        FewShotPromptTemplate configured for sentiment analysis
    """
    # Example template
    example_template = PromptTemplate(
        input_variables=["text", "score", "label", "reasoning"],
        template="Text: {text}\nAnalysis: Score={score}, Label={label}\nReasoning: {reasoning}\n"
    )

    # Few-shot prompt template
    prompt = FewShotPromptTemplate(
        examples=SENTIMENT_EXAMPLES,
        example_prompt=example_template,
        prefix="You are a sentiment analysis expert. Analyze the sentiment of social media posts on a 0-100 scale.\n\n",
        suffix="Text: {text}\nAnalysis:",
        input_variables=["text"],
        example_separator="\n"
    )

    return prompt


def create_batch_sentiment_prompt_template() -> PromptTemplate:
    """
    Create prompt template for batch sentiment analysis.

    Returns:
        PromptTemplate for batch analysis
    """
    template = """You are a sentiment analysis expert. Analyze the sentiment of each social media post and provide a JSON array response.

Score guide (0-100):
- 0-20: Extremely negative (hate, anger, disgust)
- 21-40: Negative (disappointment, frustration)
- 41-60: Neutral (objective, balanced, mild opinions)
- 61-80: Positive (satisfaction, approval)
- 81-100: Extremely positive (love, excitement, enthusiasm)

Requirements:
1. Consider overall emotional tone, specific keywords, context, and sarcasm
2. Respond with ONLY a valid JSON array
3. Each object must have: score (0-100), label (positive/negative/neutral), confidence (0-1), reasoning (brief)

Examples:
Text: "This is amazing!"
{{"score": 90, "label": "positive", "confidence": 0.95, "reasoning": "Strong positive word with exclamation"}}

Text: "Not good, not bad."
{{"score": 50, "label": "neutral", "confidence": 0.7, "reasoning": "Balanced neutral statement"}}

Now analyze these posts:
{posts}

Response (JSON array only):"""

    return PromptTemplate(
        template=template,
        input_variables=["posts"]
    )


def get_sentiment_system_prompt() -> str:
    """
    Get system prompt for sentiment analysis.

    Returns:
        System prompt string
    """
    return """You are a sentiment analysis expert specializing in social media content. Your task is to analyze the emotional tone and sentiment of text on a 0-100 scale.

Key guidelines:
- 0-20: Extremely negative (hate, anger, disgust, outrage)
- 21-40: Negative (disappointment, frustration, dissatisfaction)
- 41-60: Neutral (objective facts, balanced views, mild opinions)
- 61-80: Positive (satisfaction, approval, recommendation)
- 81-100: Extremely positive (love, excitement, enthusiasm, enthusiasm)

Analysis considerations:
1. Overall emotional tone (not just individual words)
2. Context and intent behind the message
3. Sarcasm, irony, and nuanced expressions
4. Cultural and platform-specific language patterns
5. Emojis and punctuation as emotional indicators

Always respond with valid JSON in the format:
{{
  "score": <0-100 integer>,
  "label": "<positive|negative|neutral>",
  "confidence": <0.0-1.0 float>,
  "reasoning": "<brief explanation of the analysis>"
}}"""
