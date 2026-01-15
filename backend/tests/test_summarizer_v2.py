#!/usr/bin/env python3
"""
摘要生成模块 V2 测试文件

测试 SummarizerV2 的各项功能：
- 讨论摘要生成
- 关键点提取
- Map-Reduce 长文本处理

运行方式:
pytest tests/test_summarizer_v2.py -v -s
"""
import asyncio
import os
import sys
import pytest
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============ Test Fixtures ============

@pytest.fixture
def sample_posts():
    """提供测试用帖子样本"""
    return [
        {"content": "Love this product! Best purchase ever! Amazing quality!", "platform": "reddit"},
        {"content": "Great quality, fast shipping. Very happy with the service.", "platform": "reddit"},
        {"content": "A bit pricey but worth it. Good value overall.", "platform": "reddit"},
        {"content": "Customer service was excellent. They helped me quickly.", "platform": "reddit"},
        {"content": "The battery life could be better but overall satisfied.", "platform": "reddit"},
    ]


@pytest.fixture
def diverse_posts():
    """提供多样化的测试帖子"""
    return [
        {"content": "The new UI is confusing and hard to navigate. Not user friendly.", "platform": "twitter"},
        {"content": "I really like the dark mode addition. Very useful feature!", "platform": "twitter"},
        {"content": "Too many bugs in this version. Disappointed with the quality.", "platform": "twitter"},
        {"content": "Performance is much better than before. Good improvements!", "platform": "twitter"},
        {"content": "It's okay, nothing special. Does what it should.", "platform": "twitter"},
        {"content": "Would not recommend. Save your money for something better.", "platform": "twitter"},
        {"content": "Absolutely love it! Exceeded all my expectations!", "platform": "twitter"},
        {"content": "Build quality is premium. Feels great in hand.", "platform": "twitter"},
    ]


@pytest.fixture
def large_posts():
    """提供大批量测试帖子"""
    posts = []
    for i in range(50):
        posts.append({
            "content": f"This is post number {i+1} discussing various aspects of the product. " +
                     f"Users have different opinions about feature {i%5}. " +
                     f"Some think it's good, others think it needs improvement.",
            "platform": "reddit"
        })
    return posts


# ============ Unit Tests ============

@pytest.mark.asyncio
async def test_summarizer_initialization():
    """测试摘要器初始化"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()
    assert summarizer.client is not None
    assert summarizer.logger is not None

    print("✓ SummarizerV2 初始化成功")


@pytest.mark.asyncio
async def test_sentiment_description():
    """测试情感描述映射"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    test_cases = [
        (90, "very positive"),
        (70, "positive"),
        (50, "neutral"),
        (30, "negative"),
        (10, "very negative")
    ]

    for score, expected in test_cases:
        result = summarizer._describe_sentiment(score)
        assert result == expected, f"Score {score} 应该映射为 '{expected}'"
        print(f"  Score {score}: {result}")

    print("✓ 情感描述映射正确")


@pytest.mark.asyncio
async def test_post_filtering():
    """测试帖子过滤"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    posts = [
        {"content": "Good product with nice features"},
        {"content": "Short"},  # Too short
        {"content": "A" * 1000},  # Long post
    ]

    filtered = summarizer._filter_posts(posts)

    print(f"\n原始帖子: {len(posts)}")
    print(f"过滤后: {len(filtered)}")

    # 验证过滤
    assert len(filtered) <= len(posts)
    assert len(filtered) >= 1  # 至少保留一条

    # 验证长度限制
    for post in filtered:
        assert len(post["content"]) <= 600, "帖子应该被截断"

    print("✓ 帖子过滤正确")


# ============ Integration Tests ============

@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_basic(sample_posts):
    """测试基础摘要生成"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()
    sentiment_score = 75.0

    summary = await summarizer.summarize_discussion(sample_posts, sentiment_score)

    print(f"\n生成的摘要:\n{summary}\n")
    print(f"摘要长度: {len(summary)} 字符")

    # 验证结果
    assert isinstance(summary, str), "应该返回字符串"
    assert len(summary) > 50, "摘要应该有实质内容"
    assert len(summary) < 5000, "摘要不应该过长"

    print("✓ 基础摘要生成正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_different_sentiments(sample_posts):
    """测试不同情感分数的摘要"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    sentiments = [20.0, 50.0, 80.0]

    for sentiment in sentiments:
        summary = await summarizer.summarize_discussion(sample_posts, sentiment)

        print(f"\n情感分数 {sentiment}:")
        print(f"  摘要长度: {len(summary)} 字符")

        assert isinstance(summary, str)
        assert len(summary) > 0

    print("✓ 不同情感分数摘要生成正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_empty_posts():
    """测试空帖子列表"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()
    summary = await summarizer.summarize_discussion([], 50.0)

    print(f"\n空帖子摘要: {summary}")

    # 应该返回默认消息
    assert isinstance(summary, str)
    assert len(summary) > 0

    print("✓ 空帖子处理正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_all_short_posts():
    """测试全是短帖子的场景"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    short_posts = [
        {"content": "Good"},
        {"content": "Bad"},
        {"content": "Okay"}
    ]

    summary = await summarizer.summarize_discussion(short_posts, 50.0)

    print(f"\n短帖子摘要: {summary}")

    # 应该返回无法总结的消息
    assert isinstance(summary, str)

    print("✓ 短帖子处理正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_with_map_reduce():
    """测试 Map-Reduce 模式摘要"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    # 创建长文本
    long_posts = [
        {"content": f"This is post {i} with enough content to be considered. " * 20}
        for i in range(30)
    ]

    print(f"\n使用 Map-Reduce 处理 {len(long_posts)} 条帖子...")

    summary = await summarizer.summarize_discussion(
        long_posts,
        60.0,
        use_map_reduce=True
    )

    print(f"\n生成的摘要:\n{summary}\n")
    print(f"摘要长度: {len(summary)} 字符")

    # 验证结果
    assert isinstance(summary, str)
    assert len(summary) > 50

    print("✓ Map-Reduce 摘要生成正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_extract_key_points(sample_posts):
    """测试关键点提取"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    key_points = await summarizer.extract_key_points(sample_posts, max_points=5)

    print(f"\n提取的关键点:")
    for i, point in enumerate(key_points, 1):
        print(f"  {i}. {point}")

    # 验证结果
    assert isinstance(key_points, list)
    assert len(key_points) <= 5

    for point in key_points:
        assert isinstance(point, str)
        assert len(point) > 0

    print("✓ 关键点提取正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_large_dataset(large_posts):
    """测试大数据集摘要"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    print(f"\n处理 {len(large_posts)} 条帖子...")

    summary = await summarizer.summarize_discussion(large_posts, 55.0)

    print(f"\n生成的摘要:\n{summary}\n")
    print(f"摘要长度: {len(summary)} 字符")

    # 验证结果
    assert isinstance(summary, str)
    assert len(summary) > 100

    print("✓ 大数据集摘要生成正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_diverse_opinions(diverse_posts):
    """测试多样化观点的摘要"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    print(f"\n处理 {len(diverse_posts)} 条多样化观点帖子...")

    summary = await summarizer.summarize_discussion(diverse_posts, 50.0)

    print(f"\n生成的摘要:\n{summary}\n")

    # 验证摘要捕捉了多样性
    assert isinstance(summary, str)
    assert len(summary) > 50

    # 摘要应该提到不同观点
    # (这里不做强制断言，因为内容是生成的)

    print("✓ 多样化观点摘要生成正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_token_tracking():
    """测试 Token 追踪"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    # 重置追踪
    summarizer.logger.reset_token_tracking()

    # 执行摘要
    await summarizer.summarize_discussion(sample_posts, 60.0)

    # 获取统计
    summary_stats = summarizer.client.get_token_summary()

    print(f"\nToken 使用统计:")
    print(f"  API calls: {summary_stats['api_calls']}")
    print(f"  Total tokens: {summary_stats['total_tokens']}")
    print(f"  Estimated cost: ${summary_stats['estimated_cost']:.4f}")

    # 验证有数据
    assert summary_stats["api_calls"] > 0
    assert summary_stats["total_tokens"] > 0

    print("✓ Token 追踪功能正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_quality():
    """测试摘要质量"""
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    # 创建有明显主题的帖子
    themed_posts = [
        {"content": "The battery life is excellent, lasts all day"},
        {"content": "Great battery performance, very satisfied"},
        {"content": "Battery could be better, drains quickly"},
        {"content": "The build quality feels premium and sturdy"},
        {"content": "Cheap materials, poor construction quality"},
    ]

    summary = await summarizer.summarize_discussion(themed_posts, 60.0)

    print(f"\n生成的摘要:\n{summary}\n")

    # 验证摘要长度合理
    assert 100 < len(summary) < 2000, "摘要长度应该合理"

    # 验证是自然语言（不是列表）
    assert not summary.startswith("-"), "不应该以列表形式呈现"
    assert not summary.startswith("*"), "不应该以列表形式呈现"

    print("✓ 摘要质量良好")


# ============ Performance Tests ============

@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.asyncio
async def test_summarization_performance():
    """测试摘要生成性能"""
    import time
    from src.ai_analysis.summarizer_v2 import SummarizerV2

    summarizer = SummarizerV2()

    # 测试小数据集性能
    small_posts = [{"content": f"Test post {i}"} for i in range(5)]

    start = time.time()
    await summarizer.summarize_discussion(small_posts, 50.0)
    small_duration = time.time() - start

    print(f"\n小数据集摘要耗时 (5条): {small_duration:.2f}s")

    # 测试中等数据集性能
    medium_posts = [{"content": f"Test post {i} with more content. " * 10} for i in range(20)]

    start = time.time()
    await summarizer.summarize_discussion(medium_posts, 50.0)
    medium_duration = time.time() - start

    print(f"中等数据集摘要耗时 (20条): {medium_duration:.2f}s")

    print("✓ 性能测试完成")


# ============ Main Function ============

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("摘要生成 V2 完整测试套件")
    print("="*60 + "\n")

    # 运行单元测试
    tests = [
        ("初始化测试", test_summarizer_initialization),
        ("情感描述映射", test_sentiment_description),
        ("帖子过滤", test_post_filtering),
    ]

    for name, test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"✗ {name} 失败: {e}")

    print("\n提示: 运行集成测试请使用:")
    print("  pytest tests/test_summarizer_v2.py -m integration -v -s")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
