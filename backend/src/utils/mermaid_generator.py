"""
Mermaid mind map generator for visualizing opinion clusters.
"""
from typing import List, Dict
from src.utils.logger_config import get_logger


logger = get_logger(__name__)


def generate_mermaid_mindmap(
    keyword: str,
    clusters: List[Dict],
    sentiment_score: float,
    sentiment_label: str
) -> str:
    """
    Generate a Mermaid mind map from opinion clusters.

    Args:
        keyword: Main keyword/topic
        clusters: List of opinion clusters with label, summary, mention_count
        sentiment_score: Overall sentiment score (0-100)
        sentiment_label: Overall sentiment label (positive/neutral/negative)

    Returns:
        Mermaid mind map code
    """
    logger.info(f"Generating Mermaid mind map for keyword: {keyword}")

    # Start with mindmap header
    lines = ["mindmap", f"  root(({_sanitize_text(keyword)}))"]

    # Add sentiment as first branch - use simple node format without icons
    sentiment_emoji = _get_sentiment_emoji(sentiment_label)
    lines.append(f"    {sentiment_emoji} Overall Sentiment")
    lines.append(f"      Score {sentiment_score:.1f}")
    lines.append(f"      {sentiment_label.capitalize()}")

    # Add each opinion cluster as a main branch
    for i, cluster in enumerate(clusters[:5], 1):  # Limit to top 5
        label = cluster.get("label", f"Opinion {i}")
        summary = cluster.get("summary", "")
        mention_count = cluster.get("mention_count", 0)

        # Sanitize and format
        safe_label = _sanitize_text(label)
        safe_summary = _sanitize_text(summary)

        # Add cluster as main branch - use simple text nodes
        lines.append(f"    {safe_label}")
        lines.append(f"      {mention_count} mentions")

        # Add summary as sub-points (split by sentences)
        if safe_summary:
            sentences = _split_into_bullets(safe_summary, max_bullets=2)
            for sentence in sentences:
                lines.append(f"      {sentence}")

    # Close mindmap
    mermaid_code = "\n".join(lines)

    logger.info(f"Generated Mermaid mind map with {len(clusters)} clusters")
    return mermaid_code


def _sanitize_text(text: str) -> str:
    """
    Sanitize text for Mermaid syntax.

    Args:
        text: Raw text

    Returns:
        Sanitized text safe for Mermaid
    """
    if not text:
        return ""

    # Remove problematic characters
    text = text.strip()

    # Replace quotes and special characters that break mermaid syntax
    replacements = {
        '"': "",
        "'": "",
        "(": "",
        ")": "",
        "{": "",
        "}": "",
        "[": "",
        "]": "",
        "<": "",
        ">": "",
        "&": "and",
        "#": "",
        "`": "",
        "|": "-",
        "\\": "",
        "\n": " ",
        "\r": " ",
        "\t": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove multiple spaces
    import re
    text = re.sub(r'\s+', ' ', text)

    # Limit length
    if len(text) > 40:
        text = text[:37] + "..."

    return text.strip()


def _split_into_bullets(text: str, max_bullets: int = 3) -> List[str]:
    """
    Split text into bullet points.

    Args:
        text: Text to split
        max_bullets: Maximum number of bullets

    Returns:
        List of bullet point strings
    """
    # Split by sentence endings
    import re
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    # Limit to max_bullets
    bullets = sentences[:max_bullets]

    # Limit each bullet length
    return [b[:40] + "..." if len(b) > 40 else b for b in bullets]


def _get_sentiment_emoji(label: str) -> str:
    """Get emoji for sentiment label."""
    mapping = {
        "positive": "😊",
        "neutral": "😐",
        "negative": "😟",
    }
    return mapping.get(label.lower(), "📊")


def _get_sentiment_icon(label: str) -> str:
    """Get Font Awesome icon name for sentiment."""
    mapping = {
        "positive": "smile",
        "neutral": "meh",
        "negative": "frown",
    }
    return mapping.get(label.lower(), "chart-line")


def generate_mermaid_flowchart(
    keyword: str,
    posts: List[Dict],
    top_n: int = 10
) -> str:
    """
    Generate a Mermaid flow chart showing post flow by sentiment.

    Args:
        keyword: Main keyword
        posts: List of posts with sentiment scores
        top_n: Number of posts to include

    Returns:
        Mermaid flow chart code
    """
    logger.info(f"Generating Mermaid flow chart for {len(posts)} posts")

    lines = ["graph TD"]

    # Add keyword node
    lines.append(f"  KeyNode[{keyword}]")

    # Filter out posts with None sentiment scores
    valid_posts = [p for p in posts if p.get("sentiment_score") is not None]

    if not valid_posts:
        logger.warning("No valid posts with sentiment scores found")
        return "graph TD\n  KeyNode[No Data Available]"

    # Sort posts by sentiment score
    sorted_posts = sorted(
        valid_posts,
        key=lambda x: x.get("sentiment_score", 50) or 50,
        reverse=True
    )[:top_n]

    # Group by sentiment category (use default 50 for None, though we filtered already)
    positive_posts = [p for p in sorted_posts if (p.get("sentiment_score") or 50) >= 60]
    neutral_posts = [p for p in sorted_posts if 40 <= (p.get("sentiment_score") or 50) < 60]
    negative_posts = [p for p in sorted_posts if (p.get("sentiment_score") or 50) < 40]

    # Add sentiment category nodes
    if positive_posts:
        lines.append("  Positive[😊 Positive]")
        for i, post in enumerate(positive_posts[:3], 1):
            content = _sanitize_text(post.get("content", ""))[:30]
            lines.append(f"    Pos{i}[{content}]")
            lines.append(f"  Positive --> Pos{i}")

    if neutral_posts:
        lines.append("  Neutral[😐 Neutral]")
        for i, post in enumerate(neutral_posts[:3], 1):
            content = _sanitize_text(post.get("content", ""))[:30]
            lines.append(f"    Neu{i}[{content}]")
            lines.append(f"  Neutral --> Neu{i}")

    if negative_posts:
        lines.append("  Negative[😟 Negative]")
        for i, post in enumerate(negative_posts[:3], 1):
            content = _sanitize_text(post.get("content", ""))[:30]
            lines.append(f"    Neg{i}[{content}]")
            lines.append(f"  Negative --> Neg{i}")

    # Connect keyword to categories
    if positive_posts:
        lines.append("  KeyNode --> Positive")
    if neutral_posts:
        lines.append("  KeyNode --> Neutral")
    if negative_posts:
        lines.append("  KeyNode --> Negative")

    # Add styling
    lines.append("  classDef positive fill:#90EE90")
    lines.append("  classDef neutral fill:#FFD700")
    lines.append("  classDef negative fill:#FFB6C1")

    mermaid_code = "\n".join(lines)

    logger.info(f"Generated Mermaid flow chart")
    return mermaid_code


def generate_mermaid_pie_chart(
    keyword: str,
    clusters: List[Dict]
) -> str:
    """
    Generate a Mermaid pie chart showing opinion distribution.

    Args:
        keyword: Main keyword
        clusters: Opinion clusters with mention counts

    Returns:
        Mermaid pie chart code
    """
    logger.info(f"Generating Mermaid pie chart for {len(clusters)} clusters")

    lines = ["pie title {} - Opinion Distribution".format(_sanitize_text(keyword))]

    total_mentions = sum(c.get("mention_count", 0) for c in clusters)

    for cluster in clusters:
        label = cluster.get("label", "Unknown")
        count = cluster.get("mention_count", 0)
        percentage = (count / total_mentions * 100) if total_mentions > 0 else 0

        safe_label = _sanitize_text(label)
        lines.append(f"  \"{safe_label}\" : {percentage:.1f}")

    mermaid_code = "\n".join(lines)

    logger.info(f"Generated Mermaid pie chart")
    return mermaid_code
