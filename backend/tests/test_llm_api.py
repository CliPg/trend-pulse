#!/usr/bin/env python3
"""
测试LLM API配置和连接

用于诊断通义千问API配置是否正确

使用方式:
1. 直接运行: python tests/test_llm_api.py (详细输出)
2. pytest测试: pytest tests/test_llm_api.py -v -s (快速测试)
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

from src.config import Config
from src.ai_analysis.client import LLMClient



@pytest.mark.asyncio
async def test_api_config():
    """测试API配置 (pytest版本)"""
    # Check configuration
    assert Config.LLM_API_KEY, "LLM_API_KEY 未配置! 请在 .env 文件中设置"
    assert Config.LLM_API_BASE_URL, "LLM_API_BASE_URL 未配置"
    assert Config.LLM_MODEL, "LLM_MODEL 未配置"


@pytest.mark.asyncio
async def test_api_connection():
    """测试API连接 (pytest版本)"""
    client = LLMClient()

    # Test simple completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Respond with: {\"status\": \"ok\"}"}
    ]

    response = await client.chat_completion(messages, temperature=0.3)

    # Check response
    assert response, "API返回空响应"
    assert len(response) > 0, "API返回响应为空"


@pytest.mark.asyncio
async def test_sentiment_analysis():
    """测试情感分析功能 (pytest版本)"""
    from src.ai_analysis.sentiment import SentimentAnalyzer

    analyzer = SentimentAnalyzer()
    test_text = "This product is amazing! I love it so much."

    result = await analyzer.analyze_sentiment(test_text)
    print("Sentiment Analysis Result:", result)

    # Validate result structure
    assert "score" in result, "结果缺少 'score' 字段"
    assert "label" in result, "结果缺少 'label' 字段"
    assert "confidence" in result, "结果缺少 'confidence' 字段"
    assert "reasoning" in result, "结果缺少 'reasoning' 字段"

    # Validate result values
    assert 0 <= result["score"] <= 100, f"Score应该为0-100, 实际为{result['score']}"
    assert result["label"] in ["positive", "negative", "neutral"], f"Label应该为positive/negative/neutral, 实际为{result['label']}"
    assert 0 <= result["confidence"] <= 1, f"Confidence应该为0-1, 实际为{result['confidence']}"


@pytest.mark.asyncio
async def test_batch_analysis():
    """测试批量分析功能 (pytest版本)"""
    from src.ai_analysis.sentiment import SentimentAnalyzer

    analyzer = SentimentAnalyzer()

    test_texts = [
        "I love this product! It's amazing!",
        "This is terrible. Worst purchase ever.",
        "It's okay, nothing special."
    ]

    results = await analyzer.analyze_batch(test_texts)

    # Validate results
    assert len(results) == len(test_texts), f"期望{len(test_texts)}个结果, 实际{len(results)}个"

    for result in results:
        assert "score" in result, "结果缺少 'score' 字段"
        assert "label" in result, "结果缺少 'label' 字段"
        assert 0 <= result["score"] <= 100, f"Score应该为0-100, 实际为{result['score']}"

