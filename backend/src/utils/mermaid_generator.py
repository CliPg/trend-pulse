"""
Visualization generators for opinion clusters.
Supports Mermaid and ECharts formats.
"""
import json
from typing import List, Dict
from src.utils.logger_config import get_logger


logger = get_logger(__name__)


def generate_echarts_tree(
    keyword: str,
    clusters: List[Dict],
    sentiment_score: float,
    sentiment_label: str
) -> str:
    """
    Generate ECharts tree data JSON for beautiful mind map visualization.

    Args:
        keyword: Main keyword/topic
        clusters: List of opinion clusters with label, summary, mention_count
        sentiment_score: Overall sentiment score (0-100)
        sentiment_label: Overall sentiment label (positive/neutral/negative)

    Returns:
        JSON string for ECharts tree configuration
    """
    logger.info(f"Generating ECharts tree for keyword: {keyword}")

    # Build tree data structure
    children = []

    # Add sentiment node
    sentiment_color = _get_sentiment_color(sentiment_label)
    sentiment_emoji = _get_sentiment_emoji(sentiment_label)
    children.append({
        "name": f"{sentiment_emoji} Sentiment",
        "value": sentiment_score,
        "itemStyle": {"color": sentiment_color},
        "children": [
            {"name": f"Score: {sentiment_score:.1f}", "value": sentiment_score},
            {"name": sentiment_label.capitalize(), "value": 1}
        ]
    })

    # Define colors for clusters
    cluster_colors = ["#6366f1", "#8b5cf6", "#ec4899", "#f59e0b", "#10b981"]

    # Add each opinion cluster
    for i, cluster in enumerate(clusters[:5], 0):
        label = cluster.get("label", f"Opinion {i+1}")
        summary = cluster.get("summary", "")
        mention_count = cluster.get("mention_count", 0)

        # Create cluster children
        cluster_children = [
            {"name": f"📊 {mention_count} mentions", "value": mention_count}
        ]

        # Add summary points
        if summary:
            sentences = _split_into_bullets(summary, max_bullets=2)
            for sentence in sentences:
                cluster_children.append({
                    "name": f"💬 {sentence}",
                    "value": 1
                })

        children.append({
            "name": _clean_text(label),
            "value": mention_count,
            "itemStyle": {"color": cluster_colors[i % len(cluster_colors)]},
            "children": cluster_children
        })

    tree_data = {
        "name": _clean_text(keyword),
        "children": children
    }

    logger.info(f"Generated ECharts tree with {len(clusters)} clusters")
    return json.dumps(tree_data, ensure_ascii=False)


def generate_mermaid_mindmap(
    keyword: str,
    clusters: List[Dict],
    sentiment_score: float,
    sentiment_label: str
) -> str:
    """
    Generate a Mermaid mind map from opinion clusters.
    (Legacy - kept for backward compatibility)

    Args:
        keyword: Main keyword/topic
        clusters: List of opinion clusters with label, summary, mention_count
        sentiment_score: Overall sentiment score (0-100)
        sentiment_label: Overall sentiment label (positive/neutral/negative)

    Returns:
        Mermaid mind map code
    """
    # Return ECharts JSON format instead for better visualization
    return generate_echarts_tree(keyword, clusters, sentiment_score, sentiment_label)


def _clean_text(text: str) -> str:
    """Clean text for display, preserving readability."""
    if not text:
        return ""

    text = text.strip()

    # Only remove characters that would break JSON
    text = text.replace('"', "'")
    text = text.replace("\\", "")
    text = text.replace("\n", " ")
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")

    # Remove multiple spaces
    import re
    text = re.sub(r'\s+', ' ', text)

    # Limit length
    if len(text) > 50:
        text = text[:47] + "..."

    return text.strip()


def _get_sentiment_color(label: str) -> str:
    """Get color for sentiment label."""
    mapping = {
        "positive": "#10b981",  # Green
        "neutral": "#f59e0b",   # Amber
        "negative": "#ef4444",  # Red
    }
    return mapping.get(label.lower(), "#6366f1")


def _get_sentiment_emoji(label: str) -> str:
    """Get emoji for sentiment label."""
    mapping = {
        "positive": "😊",
        "neutral": "😐",
        "negative": "😟",
    }
    return mapping.get(label.lower(), "📊")


def _split_into_bullets(text: str, max_bullets: int = 3) -> List[str]:
    """
    Split text into bullet points.

    Args:
        text: Text to split
        max_bullets: Maximum number of bullets

    Returns:
        List of bullet point strings
    """
    import re
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    bullets = sentences[:max_bullets]
    return [_clean_text(b) for b in bullets]


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
            content = _clean_text(post.get("content", ""))[:30]
            lines.append(f"    Pos{i}[{content}]")
            lines.append(f"  Positive --> Pos{i}")

    if neutral_posts:
        lines.append("  Neutral[😐 Neutral]")
        for i, post in enumerate(neutral_posts[:3], 1):
            content = _clean_text(post.get("content", ""))[:30]
            lines.append(f"    Neu{i}[{content}]")
            lines.append(f"  Neutral --> Neu{i}")

    if negative_posts:
        lines.append("  Negative[😟 Negative]")
        for i, post in enumerate(negative_posts[:3], 1):
            content = _clean_text(post.get("content", ""))[:30]
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

    lines = ["pie title {} - Opinion Distribution".format(_clean_text(keyword))]

    total_mentions = sum(c.get("mention_count", 0) for c in clusters)

    for cluster in clusters:
        label = cluster.get("label", "Unknown")
        count = cluster.get("mention_count", 0)
        percentage = (count / total_mentions * 100) if total_mentions > 0 else 0

        safe_label = _clean_text(label)
        lines.append(f"  \"{safe_label}\" : {percentage:.1f}")

    mermaid_code = "\n".join(lines)

    logger.info(f"Generated Mermaid pie chart")
    return mermaid_code
