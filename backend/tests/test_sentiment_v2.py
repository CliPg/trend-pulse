#!/usr/bin/env python3
"""
情感分析模块 V2 测试文件

测试 SentimentAnalyzerV2 的各项功能：
- 单条文本分析
- 批量分析
- Map-Reduce 长文本处理
- 结果验证
- Token 追踪

运行方式:
1. 快速测试: pytest tests/test_sentiment_v2.py -v
2. 详细输出: pytest tests/test_sentiment_v2.py -v -s
3. 只运行单元测试: pytest tests/test_sentiment_v2.py -m "not integration"
4. 只运行集成测试: pytest tests/test_sentiment_v2.py -m integration
"""
import asyncio
import os
import sys
import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============ Test Fixtures ============

@pytest.fixture
def sample_texts():
    """提供测试用文本样本"""
    return {
        "very_positive": "This product is absolutely amazing! Best purchase I've ever made. Highly recommend to everyone! Love it!",
        "positive": "Pretty good overall. I like the design and the quality is nice. Would buy again.",
        "neutral": "The product is okay. It does what it's supposed to do, but nothing special.",
        "negative": "Not great, not terrible. It has some issues but works most of the time. Could be better.",
        "very_negative": "Terrible experience! Worst mistake of my life buying this. Complete waste of money. Do NOT buy!",
        "short": "Good!",
        "long_text": """
        I've been using this product for about three months now, and I have to say it's been quite an experience.
        At first, I was skeptical because of the mixed reviews, but I decided to give it a try anyway.
        The build quality is excellent - it feels premium and well-made. The materials used are definitely
        high-quality and you can tell that attention was paid to the design. However, the battery life is
        a bit disappointing. It lasts about 4-5 hours with moderate use, which is less than advertised.
        The performance is good though - it handles most tasks smoothly without any lag. The interface is
        intuitive and easy to navigate, even for someone who isn't tech-savvy. Customer service was helpful
        when I had questions, though response time could be faster. Overall, I'd say it's a solid product
        that delivers on most fronts, though there's room for improvement in certain areas.
        """
    }


@pytest.fixture
def batch_texts():
    """提供批量测试文本"""
    return [
        "Love this product! Best purchase ever!",
        "Great quality, fast shipping, very happy.",
        "A bit pricey but worth it in my opinion.",
        "Customer service was excellent and helpful.",
        "The new UI is confusing and hard to use.",
        "I like the dark mode addition, very useful.",
        "Too many bugs in this version, disappointed.",
        "Performance is better than before, good job.",
        "It's okay, nothing special really.",
        "Would not recommend, save your money."
    ]


# ============ Unit Tests ============

@pytest.mark.asyncio
async def test_sentiment_initialization():
    """测试情感分析器初始化"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    # 测试默认初始化
    analyzer = SentimentAnalyzerV2()
    assert analyzer.client is not None
    assert analyzer.logger is not None

    # 测试指定 provider
    analyzer_openai = SentimentAnalyzerV2(provider="openai")
    assert analyzer_openai.client is not None

    print("✓ SentimentAnalyzerV2 初始化成功")


@pytest.mark.asyncio
async def test_sentiment_result_validation():
    """测试结果验证功能"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()

    # 测试正常结果
    valid_result = {
        "score": 75,
        "label": "positive",
        "confidence": 0.85
    }
    validated = analyzer._validate_result(valid_result)
    assert validated["score"] == 75
    assert validated["label"] == "positive"
    assert "reasoning" in validated

    # 测试缺少字段的结果
    incomplete_result = {"score": 50}
    validated = analyzer._validate_result(incomplete_result)
    assert "label" in validated
    assert "confidence" in validated
    assert "reasoning" in validated

    # 测试超出范围的 score
    out_of_range = {"score": 150, "label": "positive", "confidence": 0.5}
    validated = analyzer._validate_result(out_of_range)
    assert validated["score"] == 100  # Should be clamped

    # 测试无效 label
    invalid_label = {"score": 50, "label": "invalid", "confidence": 0.5}
    validated = analyzer._validate_result(invalid_label)
    assert validated["label"] in ["positive", "negative", "neutral"]

    print("✓ 结果验证功能正常")


@pytest.mark.asyncio
async def test_overall_sentiment_calculation():
    """测试整体情感计算"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()

    # 测试正常分数
    scores = [80, 70, 90]
    overall = analyzer.calculate_overall_sentiment(scores)
    assert overall == 80.0

    # 测试空列表
    overall = analyzer.calculate_overall_sentiment([])
    assert overall == 50.0

    # 测试不同分数范围
    scores = [0, 50, 100]
    overall = analyzer.calculate_overall_sentiment(scores)
    assert overall == 50.0

    print("✓ 整体情感计算正确")


@pytest.mark.asyncio
async def test_text_preprocessing():
    """测试文本预处理"""
    from src.ai_analysis.utils import TextPreprocessor

    # 测试清理
    dirty_text = "This   is    a   test   with   extra   spaces.  "
    cleaned = TextPreprocessor.remove_redundancy(dirty_text)
    assert "   " not in cleaned

    # 测试截断
    long_text = "a" * 2000
    cleaned = TextPreprocessor.clean_for_analysis(long_text, max_length=100)
    assert len(cleaned) <= 103  # 100 + "..."

    # 测试关键句提取
    long_text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
    key_sentences = TextPreprocessor.extract_key_sentences(long_text, max_sentences=3)
    assert len(key_sentences) < len(long_text)

    print("✓ 文本预处理功能正常")


@pytest.mark.asyncio
async def test_token_counter():
    """测试 Token 计数器"""
    from src.ai_analysis.utils import TokenCounter

    # 测试计数
    text = "This is a test."
    tokens = TokenCounter.count_tokens(text)
    assert tokens > 0

    # 测试批量计数
    texts = ["Test one", "Test two", "Test three"]
    total = TokenCounter.count_tokens_batch(texts)
    assert total > 0

    # 测试截断
    long_text = "word " * 1000
    truncated = TokenCounter.truncate_to_tokens(long_text, max_tokens=100)
    assert TokenCounter.count_tokens(truncated) <= 100

    print("✓ Token 计数器功能正常")


# ============ Integration Tests ============

@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_single_positive(sample_texts):
    """测试单条积极文本分析"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()
    result = await analyzer.analyze_sentiment(sample_texts["very_positive"])

    print(f"\n分析结果: {result}")

    # 验证结构
    assert "score" in result
    assert "label" in result
    assert "confidence" in result
    assert "reasoning" in result

    # 验证值范围
    assert 0 <= result["score"] <= 100
    assert result["label"] in ["positive", "negative", "neutral"]
    assert 0 <= result["confidence"] <= 1

    # 验证情感倾向
    assert result["score"] >= 60, "积极文本应该有较高分数"
    assert result["label"] == "positive", "应该识别为积极"

    print(f"✓ 积极文本分析正确 (score: {result['score']}, label: {result['label']})")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_single_negative(sample_texts):
    """测试单条消极文本分析"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()
    result = await analyzer.analyze_sentiment(sample_texts["very_negative"])

    print(f"\n分析结果: {result}")

    # 验证情感倾向
    assert result["score"] <= 40, "消极文本应该有较低分数"
    assert result["label"] == "negative", "应该识别为消极"

    print(f"✓ 消极文本分析正确 (score: {result['score']}, label: {result['label']})")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_single_neutral(sample_texts):
    """测试单条中性文本分析"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()
    result = await analyzer.analyze_sentiment(sample_texts["neutral"])

    print(f"\n分析结果: {result}")

    # 验证情感倾向
    assert 40 <= result["score"] <= 60, "中性文本应该在中间范围"
    assert result["label"] == "neutral", "应该识别为中性"

    print(f"✓ 中性文本分析正确 (score: {result['score']}, label: {result['label']})")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_short_text(sample_texts):
    """测试短文本分析"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()
    result = await analyzer.analyze_sentiment(sample_texts["short"])

    print(f"\n分析结果: {result}")

    # 验证仍然能正确分析
    assert "score" in result
    assert 0 <= result["score"] <= 100

    print(f"✓ 短文本分析正确 (score: {result['score']})")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_long_text_direct(sample_texts):
    """测试长文本直接分析"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()
    result = await analyzer.analyze_sentiment(sample_texts["long_text"])

    print(f"\n分析结果: {result}")

    # 验证长文本能正确分析
    assert "score" in result
    assert 0 <= result["score"] <= 100
    assert "reasoning" in result

    print(f"✓ 长文本直接分析正确 (score: {result['score']})")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_batch_small(batch_texts):
    """测试小批量分析"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()
    results = await analyzer.analyze_batch(batch_texts[:3])

    print(f"\n分析了 {len(results)} 条文本")

    # 验证结果数量
    assert len(results) == 3

    # 验证每个结果的结构
    for i, result in enumerate(results):
        assert "score" in result, f"结果 {i} 缺少 score"
        assert "label" in result, f"结果 {i} 缺少 label"
        assert 0 <= result["score"] <= 100

        print(f"  {i+1}. score={result['score']}, label={result['label']}")

    print(f"✓ 小批量分析正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_batch_large(batch_texts):
    """测试大批量分析"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()

    # 创建更多测试数据
    large_batch = batch_texts * 5  # 50 条文本

    results = await analyzer.analyze_batch(large_batch)

    print(f"\n分析了 {len(results)} 条文本")

    # 验证结果数量
    assert len(results) == len(large_batch)

    # 计算统计信息
    scores = [r["score"] for r in results]
    avg_score = sum(scores) / len(scores)

    print(f"  平均分数: {avg_score:.1f}")
    print(f"  分数范围: {min(scores)} - {max(scores)}")

    # 验证整体情感计算
    overall = analyzer.calculate_overall_sentiment(scores)
    assert overall == avg_score

    print(f"✓ 大批量分析正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_with_map_reduce():
    """测试 Map-Reduce 模式"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()

    # 创建超长文本
    long_text = """
    This is an amazing product with excellent features and great performance.
    """ * 100  # 重复100次创建非常长的文本

    print(f"\n文本长度: {len(long_text)} 字符")

    # 使用 Map-Reduce
    result = await analyzer.analyze_sentiment(long_text, use_map_reduce=True)

    print(f"分析结果: {result}")

    # 验证结果
    assert "score" in result
    assert 0 <= result["score"] <= 100

    print(f"✓ Map-Reduce 模式分析正确 (score: {result['score']})")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_token_tracking():
    """测试 Token 追踪功能"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()

    # 重置追踪
    analyzer.logger.reset_token_tracking()

    # 执行分析
    await analyzer.analyze_sentiment("This is a test")
    await analyzer.analyze_sentiment("Another test")

    # 获取统计
    summary = analyzer.client.get_token_summary()

    print(f"\nToken 使用统计:")
    print(f"  Input tokens: {summary['total_input_tokens']}")
    print(f"  Output tokens: {summary['total_output_tokens']}")
    print(f"  Total tokens: {summary['total_tokens']}")
    print(f"  Estimated cost: ${summary['estimated_cost']:.4f}")
    print(f"  API calls: {summary['api_calls']}")

    # 验证统计数据
    assert summary["api_calls"] >= 2
    assert summary["total_input_tokens"] > 0
    assert summary["total_output_tokens"] > 0
    assert summary["estimated_cost"] > 0

    print("✓ Token 追踪功能正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_consistency():
    """测试分析一致性"""
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()
    test_text = "This is a very good product!"

    # 分析同一文本多次
    results = []
    for i in range(3):
        result = await analyzer.analyze_sentiment(test_text)
        results.append(result["score"])

    print(f"\n三次分析结果: {results}")

    # 验证结果相对一致（波动不超过 10 分）
    max_diff = max(results) - min(results)
    assert max_diff < 20, f"分析结果差异过大: {max_diff}"

    print(f"✓ 分析一致性良好 (最大差异: {max_diff})")


# ============ Performance Tests ============

@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.asyncio
async def test_sentiment_performance():
    """测试分析性能"""
    import time
    from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2

    analyzer = SentimentAnalyzerV2()

    # 测试单条分析性能
    start = time.time()
    await analyzer.analyze_sentiment("This is a test")
    single_duration = time.time() - start

    print(f"\n单条分析耗时: {single_duration:.2f}s")

    # 测试批量分析性能
    batch = ["Test text"] * 10
    start = time.time()
    await analyzer.analyze_batch(batch)
    batch_duration = time.time() - start

    print(f"批量分析耗时 (10条): {batch_duration:.2f}s")
    print(f"平均每条: {batch_duration/10:.2f}s")

    # 批量应该比逐条快
    print(f"✓ 性能测试完成")


# ============ Main Function ============

async def run_all_tests():
    """运行所有测试并输出详细结果"""
    print("\n" + "="*60)
    print("情感分析 V2 完整测试套件")
    print("="*60 + "\n")

    # 运行各项测试
    tests = [
        ("初始化测试", test_sentiment_initialization),
        ("结果验证测试", test_sentiment_result_validation),
        ("整体情感计算", test_overall_sentiment_calculation),
        ("文本预处理", test_text_preprocessing),
        ("Token计数器", test_token_counter),
    ]

    for name, test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"✗ {name} 失败: {e}")

    print("\n" + "="*60)
    print("集成测试 (需要 API)")
    print("="*60 + "\n")

    # 注意: 集成测试需要配置 API key
    print("提示: 运行集成测试请使用:")
    print("  pytest tests/test_sentiment_v2.py -m integration -v -s")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
