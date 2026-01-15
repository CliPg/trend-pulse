#!/usr/bin/env python3
"""
AI 分析管道 V2 测试文件

测试 AnalysisPipelineV2 的完整功能：
- 端到端分析流程
- 模块组合
- Token 追踪
- 性能测试

运行方式:
pytest tests/test_pipeline_v2.py -v -s
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
        {
            "content": "Love this product! Best purchase ever! Amazing quality and fast shipping!",
            "author": "user1",
            "platform": "reddit",
            "url": "https://reddit.com/post1"
        },
        {
            "content": "Great quality, though a bit expensive. Worth it though.",
            "author": "user2",
            "platform": "reddit",
            "url": "https://reddit.com/post2"
        },
        {
            "content": "Not great, not terrible. It's okay for the price.",
            "author": "user3",
            "platform": "reddit",
            "url": "https://reddit.com/post3"
        },
        {
            "content": "Terrible experience! Worst purchase ever. Do NOT buy!",
            "author": "user4",
            "platform": "reddit",
            "url": "https://reddit.com/post4"
        },
        {
            "content": "The battery life is excellent. Lasts all day!",
            "author": "user5",
            "platform": "reddit",
            "url": "https://reddit.com/post5"
        },
    ]


@pytest.fixture
def large_posts():
    """提供大批量测试帖子"""
    posts = []
    for i in range(50):
        sentiment = ["good", "bad", "okay"][i % 3]
        posts.append({
            "content": f"This product is {sentiment}. Feature {i%5} is nice. Post number {i+1}.",
            "author": f"user{i+1}",
            "platform": "reddit",
            "url": f"https://reddit.com/post{i+1}"
        })
    return posts


# ============ Unit Tests ============

@pytest.mark.asyncio
async def test_pipeline_initialization():
    """测试管道初始化"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    # 测试默认初始化
    pipeline = AnalysisPipelineV2()
    assert pipeline.sentiment_analyzer is not None
    assert pipeline.opinion_clusterer is not None
    assert pipeline.summarizer is not None

    # 测试指定 provider
    pipeline_openai = AnalysisPipelineV2(provider="openai")
    assert pipeline_openai.sentiment_analyzer is not None

    # 测试启用 Map-Reduce
    pipeline_map_reduce = AnalysisPipelineV2(use_map_reduce=True)
    assert pipeline_map_reduce.use_map_reduce == True

    print("✓ AnalysisPipelineV2 初始化成功")


@pytest.mark.asyncio
async def test_pipeline_reset_tracking():
    """测试重置 Token 追踪"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()

    # 重置追踪
    pipeline.reset_tracking()

    stats = pipeline.logger.total_input_tokens
    assert stats == 0

    print("✓ Token 追踪重置功能正常")


# ============ Integration Tests ============

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_full_analysis(sample_posts):
    """测试完整分析流程"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()

    print(f"\n分析 {len(sample_posts)} 条帖子...")

    result = await pipeline.analyze_posts(sample_posts)

    print(f"\n分析结果:")
    print(f"  整体情感: {result['overall_sentiment']:.1f}/100")
    print(f"  情感结果数: {len(result['sentiment_results'])}")
    print(f"  聚类数: {len(result['clusters'])}")
    print(f"  摘要长度: {len(result['summary'])} 字符")
    print(f"\nToken 使用:")
    print(f"  总计: {result['token_usage']['total']}")
    print(f"  成本: ${result['token_usage']['cost']:.4f}")

    # 验证结果结构
    assert "sentiment_results" in result
    assert "overall_sentiment" in result
    assert "clusters" in result
    assert "summary" in result
    assert "token_usage" in result

    # 验证情感分析
    assert len(result["sentiment_results"]) == len(sample_posts)
    assert 0 <= result["overall_sentiment"] <= 100

    # 验证聚类
    assert isinstance(result["clusters"], list)

    # 验证摘要
    assert isinstance(result["summary"], str)
    assert len(result["summary"]) > 0

    # 验证 Token 使用
    assert result["token_usage"]["total"] > 0
    assert result["token_usage"]["cost"] > 0

    print("\n✓ 完整分析流程正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_empty_posts():
    """测试空帖子列表"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()
    result = await pipeline.analyze_posts([])

    print(f"\n空帖子分析结果:")
    print(f"  整体情感: {result['overall_sentiment']}")
    print(f"  情感结果: {len(result['sentiment_results'])}")
    print(f"  聚类: {len(result['clusters'])}")

    # 验证默认值
    assert result["overall_sentiment"] == 50.0
    assert len(result["sentiment_results"]) == 0
    assert result["summary"] == "No posts to analyze."

    print("✓ 空帖子处理正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_sentiment_only(sample_posts):
    """测试仅情感分析模式"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()

    result = await pipeline.analyze_sentiment_only(sample_posts)

    print(f"\n仅情感分析结果:")
    print(f"  整体情感: {result['overall_sentiment']:.1f}/100")
    print(f"  情感结果数: {len(result['sentiment_results'])}")

    # 验证结果
    assert "sentiment_results" in result
    assert "overall_sentiment" in result
    assert len(result["sentiment_results"]) == len(sample_posts)

    # 验证没有聚类和摘要
    assert "clusters" not in result
    assert "summary" not in result

    print("✓ 仅情感分析模式正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_options(sample_posts):
    """测试带选项的分析"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()

    # 跳过聚类
    result = await pipeline.analyze_posts(sample_posts, options={
        "skip_clustering": True
    })

    print(f"\n跳过聚类:")
    print(f"  聚类数: {len(result['clusters'])}")
    assert len(result["clusters"]) == 0

    # 跳过摘要
    result = await pipeline.analyze_posts(sample_posts, options={
        "skip_summary": True
    })

    print(f"\n跳过摘要:")
    print(f"  摘要: {result['summary']}")
    assert result["summary"] is None

    # 修改聚类数量
    result = await pipeline.analyze_posts(sample_posts, options={
        "top_n_clusters": 1
    })

    print(f"\nTop 1 聚类:")
    print(f"  聚类数: {len(result['clusters'])}")
    assert len(result["clusters"]) <= 1

    print("✓ 选项功能正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_with_map_reduce():
    """测试 Map-Reduce 模式"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2(use_map_reduce=True)

    # 创建大数据集
    large_dataset = [
        {"content": f"Post {i}: " + "This is content. " * 50}
        for i in range(30)
    ]

    print(f"\n使用 Map-Reduce 处理 {len(large_dataset)} 条帖子...")

    result = await pipeline.analyze_posts(large_dataset)

    print(f"\n分析结果:")
    print(f"  整体情感: {result['overall_sentiment']:.1f}/100")
    print(f"  Token 使用: {result['token_usage']['total']}")

    # 验证结果
    assert isinstance(result, dict)
    assert "sentiment_results" in result

    print("✓ Map-Reduce 模式正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_large_dataset(large_posts):
    """测试大数据集处理"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()

    print(f"\n处理 {len(large_posts)} 条帖子...")

    result = await pipeline.analyze_posts(large_posts)

    print(f"\n分析结果:")
    print(f"  整体情感: {result['overall_sentiment']:.1f}/100")
    print(f"  情感结果数: {len(result['sentiment_results'])}")
    print(f"  聚类数: {len(result['clusters'])}")
    print(f"  摘要长度: {len(result['summary'])} 字符")
    print(f"  Token 总计: {result['token_usage']['total']}")
    print(f"  API 调用: {result['token_usage']['api_calls']}")

    # 验证结果
    assert len(result["sentiment_results"]) == len(large_posts)
    assert result["token_usage"]["api_calls"] > 0

    print("✓ 大数据集处理正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_different_providers(sample_posts):
    """测试不同提供商"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    providers = ["openai", "tongyi"]

    for provider in providers:
        print(f"\n测试 provider: {provider}")

        try:
            pipeline = AnalysisPipelineV2(provider=provider)
            result = await pipeline.analyze_sentiment_only(sample_posts)

            print(f"  整体情感: {result['overall_sentiment']:.1f}/100")
            print(f"  ✓ {provider} 工作正常")

        except Exception as e:
            print(f"  ✗ {provider} 失败: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_result_structure(sample_posts):
    """测试结果结构的完整性"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()
    result = await pipeline.analyze_posts(sample_posts)

    print(f"\n验证结果结构:")

    # 验证情感结果
    assert isinstance(result["sentiment_results"], list)
    for i, sentiment in enumerate(result["sentiment_results"]):
        assert "score" in sentiment, f"情感结果 {i} 缺少 score"
        assert "label" in sentiment, f"情感结果 {i} 缺少 label"
        assert "confidence" in sentiment, f"情感结果 {i} 缺少 confidence"
        print(f"  情感 {i}: ✓")

    # 验证聚类
    assert isinstance(result["clusters"], list)
    for i, cluster in enumerate(result["clusters"]):
        assert "label" in cluster, f"聚类 {i} 缺少 label"
        assert "summary" in cluster, f"聚类 {i} 缺少 summary"
        assert "mention_count" in cluster, f"聚类 {i} 缺少 mention_count"
        print(f"  聚类 {i}: ✓")

    # 验证 Token 使用
    token_usage = result["token_usage"]
    assert "total" in token_usage
    assert "input" in token_usage
    assert "output" in token_usage
    assert "cost" in token_usage
    assert "api_calls" in token_usage
    print(f"  Token 使用: ✓")

    print("✓ 结果结构完整")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_sentiment_distribution(sample_posts):
    """测试情感分布"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()
    result = await pipeline.analyze_posts(sample_posts)

    # 统计情感分布
    labels = [r["label"] for r in result["sentiment_results"]]
    positive_count = labels.count("positive")
    negative_count = labels.count("negative")
    neutral_count = labels.count("neutral")

    print(f"\n情感分布:")
    print(f"  积极: {positive_count}")
    print(f"  消极: {negative_count}")
    print(f"  中性: {neutral_count}")
    print(f"  总计: {len(labels)}")

    # 验证总数
    assert positive_count + negative_count + neutral_count == len(labels)

    print("✓ 情感分布统计正常")


# ============ Performance Tests ============

@pytest.mark.performance
@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_performance():
    """测试管道性能"""
    import time
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    pipeline = AnalysisPipelineV2()

    # 测试小数据集
    small_posts = [{"content": f"Test post {i}"} for i in range(5)]

    start = time.time()
    result_small = await pipeline.analyze_posts(small_posts)
    small_duration = time.time() - start

    print(f"\n小数据集 (5条):")
    print(f"  耗时: {small_duration:.2f}s")
    print(f"  Token: {result_small['token_usage']['total']}")
    print(f"  平均每条: {small_duration/5:.2f}s")

    # 测试中等数据集
    medium_posts = [{"content": f"Test post {i} with more content. " * 10} for i in range(20)]

    start = time.time()
    result_medium = await pipeline.analyze_posts(medium_posts)
    medium_duration = time.time() - start

    print(f"\n中等数据集 (20条):")
    print(f"  耗时: {medium_duration:.2f}s")
    print(f"  Token: {result_medium['token_usage']['total']}")
    print(f"  平均每条: {medium_duration/20:.2f}s")

    print("\n✓ 性能测试完成")


# ============ End-to-End Tests ============

@pytest.mark.integration
@pytest.mark.asyncio
async def test_pipeline_end_to_end():
    """端到端测试：模拟真实使用场景"""
    from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2

    print("\n" + "="*60)
    print("端到端测试：模拟真实使用场景")
    print("="*60)

    # 创建模拟数据（Reddit 产品讨论）
    reddit_posts = [
        {
            "content": "Just got my new MacBook Pro M3 Max. Absolutely blown away by the performance! The battery life is incredible - getting 15+ hours easily.",
            "author": "techfan123",
            "platform": "reddit",
            "url": "https://reddit.com/r/apple/post1"
        },
        {
            "content": "The M3 Max is overpriced for what you get. My M1 Pro still runs circles around most tasks. Not worth upgrading unless you do heavy video work.",
            "author": "budget_user",
            "platform": "reddit",
            "url": "https://reddit.com/r/apple/post2"
        },
        {
            "content": "The screen is gorgeous but I'm disappointed by the RAM pricing. 8GB should not be the base in 2024. Otherwise solid machine.",
            "author": "designer_pro",
            "platform": "reddit",
            "url": "https://reddit.com/r/apple/post3"
        },
        {
            "content": "Coming from a PC, this is my first Mac. The build quality is premium but macOS is taking some getting used to. Overall happy with the purchase!",
            "author": "switcher_2024",
            "platform": "reddit",
            "url": "https://reddit.com/r/apple/post4"
        },
        {
            "content": "Had heating issues under heavy load. Apple Care replaced it - new unit runs much cooler. Great customer service!",
            "author": "video_editor",
            "platform": "reddit",
            "url": "https://reddit.com/r/apple/post5"
        },
    ]

    print(f"\n分析来源: Reddit r/apple")
    print(f"帖子数量: {len(reddit_posts)}")
    print(f"主题: MacBook Pro M3 Max\n")

    # 执行分析
    pipeline = AnalysisPipelineV2(provider="openai")
    result = await pipeline.analyze_posts(reddit_posts)

    # 显示结果
    print("\n" + "="*60)
    print("分析结果")
    print("="*60)

    print(f"\n📊 整体情感: {result['overall_sentiment']:.1f}/100")

    print(f"\n🎯 主要观点聚类 ({len(result['clusters'])}个):")
    for i, cluster in enumerate(result['clusters'], 1):
        print(f"\n  {i}. {cluster['label']}")
        print(f"     {cluster['summary'][:80]}...")
        print(f"     提及数: {cluster['mention_count']}")

    print(f"\n📝 讨论摘要:")
    print(f"  {result['summary']}")

    print(f"\n💰 Token 使用:")
    print(f"  总 Tokens: {result['token_usage']['total']:,}")
    print(f"  输入: {result['token_usage']['input']:,}")
    print(f"  输出: {result['token_usage']['output']:,}")
    print(f"  API 调用: {result['token_usage']['api_calls']}")
    print(f"  预估成本: ${result['token_usage']['cost']:.4f}")

    # 验证结果质量
    assert result['overall_sentiment'] > 0
    assert len(result['clusters']) > 0
    assert len(result['summary']) > 50

    print("\n" + "="*60)
    print("✅ 端到端测试成功")
    print("="*60 + "\n")


# ============ Main Function ============

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("AI 分析管道 V2 完整测试套件")
    print("="*60 + "\n")

    # 运行单元测试
    tests = [
        ("初始化测试", test_pipeline_initialization),
        ("Token 追踪重置", test_pipeline_reset_tracking),
    ]

    for name, test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"✗ {name} 失败: {e}")

    print("\n提示: 运行集成测试请使用:")
    print("  pytest tests/test_pipeline_v2.py -m integration -v -s")
    print("\n运行端到端测试:")
    print("  pytest tests/test_pipeline_v2.py::test_pipeline_end_to_end -v -s")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
