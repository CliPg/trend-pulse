#!/usr/bin/env python3
"""
观点聚类模块 V2 测试文件

测试 OpinionClustererV2 的各项功能：
- 观点聚类
- 垃圾内容过滤
- Map-Reduce 处理
- 结果合并

运行方式:
pytest tests/test_clustering_v2.py -v -s
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
        {"content": "The price is too high for what you get", "author": "user1"},
        {"content": "Way too expensive, not worth the money", "author": "user2"},
        {"content": "Pricing is reasonable for the quality", "author": "user3"},
        {"content": "Cost is a bit steep but acceptable", "author": "user4"},
        {"content": "Great build quality, very sturdy materials", "author": "user5"},
        {"content": "The materials feel cheap and break easily", "author": "user6"},
        {"content": "Excellent construction, feels premium", "author": "user7"},
        {"content": "Poor build quality, fell apart after a week", "author": "user8"},
        {"content": "Buy now!!! Click here for amazing deal!!!", "author": "spammer1"},
        {"content": "Subscribe to my channel for more!!!", "author": "spammer2"},
        {"content": "Short", "author": "user9"},  # Too short
    ]


@pytest.fixture
def large_posts():
    """提供大批量测试帖子"""
    posts = []
    topics = ["price", "quality", "service", "features", "design"]
    sentiments = ["good", "bad", "okay"]

    for i in range(100):
        topic = topics[i % len(topics)]
        sentiment = sentiments[i % len(sentiments)]
        posts.append({
            "content": f"The {topic} is {sentiment}. This is post number {i+1}.",
            "author": f"user{i+1}"
        })

    return posts


# ============ Unit Tests ============

@pytest.mark.asyncio
async def test_clustering_initialization():
    """测试聚类器初始化"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()
    assert clusterer.client is not None
    assert clusterer.logger is not None

    print("✓ OpinionClustererV2 初始化成功")


@pytest.mark.asyncio
async def test_spam_detection():
    """测试垃圾内容检测"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()

    # 测试垃圾内容
    spam_content = "Buy now!!! Click here!!!"
    assert clusterer._is_spam(spam_content) == True

    # 测试正常内容
    normal_content = "This product is good quality"
    assert clusterer._is_spam(normal_content) == False

    print("✓ 垃圾内容检测正确")


@pytest.mark.asyncio
async def test_post_filtering(sample_posts):
    """测试帖子过滤"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()
    filtered = clusterer._filter_posts(sample_posts)

    print(f"\n原始帖子: {len(sample_posts)}")
    print(f"过滤后: {len(filtered)}")

    # 验证过滤结果
    assert len(filtered) < len(sample_posts), "应该过滤掉部分帖子"

    # 验证没有垃圾内容
    for post in filtered:
        assert not clusterer._is_spam(post["content"]), "不应该包含垃圾内容"
        assert len(post["content"]) >= 50, "不应该包含过短内容"

    print("✓ 帖子过滤正确")


@pytest.mark.asyncio
async def test_cluster_merging():
    """测试聚类合并"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()

    # 创建相似聚类
    clusters = [
        {
            "label": "Price Discussion",
            "summary": "Users discussing pricing",
            "mention_count": 10,
            "sample_quotes": ["Too expensive", "Good price"]
        },
        {
            "label": "Price Concerns",
            "summary": "Price concerns mentioned",
            "mention_count": 8,
            "sample_quotes": ["Price is high", "Cost worries"]
        },
        {
            "label": "Quality",
            "summary": "Build quality feedback",
            "mention_count": 15,
            "sample_quotes": ["Good quality", "Poor quality"]
        }
    ]

    merged = clusterer._merge_similar_clusters(clusters, max_clusters=2)

    print(f"\n原始聚类: {len(clusters)}")
    print(f"合并后: {len(merged)}")

    # 验证合并结果
    assert len(merged) <= 2, "应该合并到最多2个聚类"

    # 验证按 mention_count 排序
    if len(merged) > 1:
        assert merged[0]["mention_count"] >= merged[1]["mention_count"], "应该按提及数排序"

    print("✓ 聚类合并正确")


# ============ Integration Tests ============

@pytest.mark.integration
@pytest.mark.asyncio
async def test_clustering_basic(sample_posts):
    """测试基础聚类功能"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()
    clusters = await clusterer.cluster_opinions(sample_posts, top_n=3)

    print(f"\n找到 {len(clusters)} 个聚类:")

    # 验证结果
    assert isinstance(clusters, list), "应该返回列表"
    assert len(clusters) <= 3, "最多返回3个聚类"

    for i, cluster in enumerate(clusters):
        print(f"\n聚类 {i+1}:")
        print(f"  标签: {cluster.get('label', 'N/A')}")
        print(f"  摘要: {cluster.get('summary', 'N/A')[:80]}...")
        print(f"  提及数: {cluster.get('mention_count', 0)}")

        # 验证结构
        assert "label" in cluster, f"聚类 {i} 缺少 label"
        assert "summary" in cluster, f"聚类 {i} 缺少 summary"
        assert "mention_count" in cluster, f"聚类 {i} 缺少 mention_count"

    print("✓ 基础聚类功能正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clustering_empty_posts():
    """测试空帖子列表"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()
    clusters = await clusterer.cluster_opinions([], top_n=3)

    print(f"\n空帖子聚类结果: {clusters}")

    # 验证返回空列表
    assert clusters == [], "空帖子应该返回空列表"

    print("✓ 空帖子处理正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clustering_spam_only():
    """测试全部是垃圾内容的情况"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()
    spam_posts = [
        {"content": "Buy now!!!", "author": "spammer1"},
        {"content": "Click here!!!", "author": "spammer2"},
        {"content": "Subscribe now!!!", "author": "spammer3"},
    ]

    clusters = await clusterer.cluster_opinions(spam_posts, top_n=3)

    print(f"\n垃圾内容聚类结果: {len(clusters)} 个聚类")

    # 应该返回空列表或很少的聚类
    assert len(clusters) == 0, "垃圾内容应该被过滤"

    print("✓ 垃圾内容过滤正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clustering_large_dataset(large_posts):
    """测试大数据集聚类"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()

    print(f"\n聚类 {len(large_posts)} 条帖子...")

    clusters = await clusterer.cluster_opinions(large_posts, top_n=5)

    print(f"找到 {len(clusters)} 个主要聚类")

    # 验证结果
    assert len(clusters) <= 5, "最多返回5个聚类"
    assert len(clusters) >= 1, "应该至少找到1个聚类"

    for i, cluster in enumerate(clusters):
        print(f"\n聚类 {i+1}:")
        print(f"  标签: {cluster.get('label', 'N/A')}")
        print(f"  提及数: {cluster.get('mention_count', 0)}")

    print("✓ 大数据集聚类正确")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clustering_with_map_reduce():
    """测试 Map-Reduce 模式聚类"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()

    # 创建大数据集
    posts = [
        {"content": f"Topic {i % 10} discussion here with more text to make it longer. " * 10}
        for i in range(50)
    ]

    print(f"\n使用 Map-Reduce 聚类 {len(posts)} 条帖子...")

    clusters = await clusterer.cluster_opinions(
        posts,
        top_n=3,
        use_map_reduce=True
    )

    print(f"找到 {len(clusters)} 个聚类")

    # 验证结果
    assert isinstance(clusters, list)

    print("✓ Map-Reduce 聚类功能正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clustering_different_top_n(sample_posts):
    """测试不同的 top_n 参数"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()

    for top_n in [1, 2, 3, 5]:
        clusters = await clusterer.cluster_opinions(sample_posts, top_n=top_n)

        print(f"\ntop_n={top_n}: 找到 {len(clusters)} 个聚类")

        assert len(clusters) <= top_n, f"聚类数不应超过 top_n={top_n}"

    print("✓ top_n 参数功能正常")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_clustering_token_tracking():
    """测试 Token 追踪"""
    from src.ai_analysis.clustering_v2 import OpinionClustererV2

    clusterer = OpinionClustererV2()

    # 重置追踪
    clusterer.logger.reset_token_tracking()

    # 执行聚类
    posts = [
        {"content": "Good product with nice features"},
        {"content": "Bad experience with poor quality"},
        {"content": "Okay product, nothing special"}
    ]

    await clusterer.cluster_opinions(posts, top_n=2)

    # 获取统计
    summary = clusterer.client.get_token_summary()

    print(f"\nToken 使用统计:")
    print(f"  API calls: {summary['api_calls']}")
    print(f"  Total tokens: {summary['total_tokens']}")
    print(f"  Estimated cost: ${summary['estimated_cost']:.4f}")

    # 验证有数据
    assert summary["api_calls"] > 0
    assert summary["total_tokens"] > 0

    print("✓ Token 追踪功能正常")


# ============ Main Function ============

async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("观点聚类 V2 完整测试套件")
    print("="*60 + "\n")

    # 运行单元测试
    tests = [
        ("初始化测试", test_clustering_initialization),
        ("垃圾内容检测", test_spam_detection),
        ("帖子过滤", test_post_filtering),
        ("聚类合并", test_cluster_merging),
    ]

    for name, test_func in tests:
        try:
            await test_func()
        except Exception as e:
            print(f"✗ {name} 失败: {e}")

    print("\n提示: 运行集成测试请使用:")
    print("  pytest tests/test_clustering_v2.py -m integration -v -s")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
