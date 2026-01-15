#!/usr/bin/env python3
"""
快速测试 Token 追踪功能
"""
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.ai_analysis.sentiment import SentimentAnalyzer
from src.ai_analysis.utils import get_analysis_logger


async def test_token_tracking():
    """测试 Token 追踪功能"""
    print("=" * 60)
    print("测试 Token 追踪功能")
    print("=" * 60)

    # 重置追踪
    logger = get_analysis_logger()
    logger.reset_token_tracking()

    # 创建分析器
    analyzer = SentimentAnalyzer()

    # 执行分析
    print("\n1. 分析第一条文本...")
    result1 = await analyzer.analyze_sentiment("This is amazing!")
    print(f"   Score: {result1['score']}, Label: {result1['label']}")

    print("\n2. 分析第二条文本...")
    result2 = await analyzer.analyze_sentiment("This is terrible!")
    print(f"   Score: {result2['score']}, Label: {result2['label']}")

    # 获取统计
    summary = analyzer.client.get_token_summary()

    print("\n" + "=" * 60)
    print("Token 使用统计:")
    print("=" * 60)
    print(f"  API calls: {summary['api_calls']}")
    print(f"  Input tokens: {summary['total_input_tokens']}")
    print(f"  Output tokens: {summary['total_output_tokens']}")
    print(f"  Total tokens: {summary['total_tokens']}")
    print(f"  Estimated cost: ${summary['estimated_cost']:.4f}")

    # 验证
    if summary['api_calls'] >= 2:
        print("\n✅ Token 追踪功能正常!")
        print(f"   正确记录了 {summary['api_calls']} 次 API 调用")
        return 0
    else:
        print(f"\n❌ Token 追踪功能异常!")
        print(f"   应该至少有 2 次 API 调用，但只记录了 {summary['api_calls']} 次")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(test_token_tracking()))
