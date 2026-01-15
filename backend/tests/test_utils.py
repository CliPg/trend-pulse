#!/usr/bin/env python3
"""
AI 分析工具函数测试文件

测试 utils 模块的功能：
- Token 计数和处理
- 文本预处理
- Map-Reduce 处理器
- 日志系统

运行方式:
pytest tests/test_utils.py -v -s
"""
import asyncio
import os
import sys
import pytest
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ============ Token Counter Tests ============

def test_token_counter_basic():
    """测试基础 Token 计数"""
    from src.ai_analysis.utils import TokenCounter

    # 测试简单文本
    text = "This is a test."
    tokens = TokenCounter.count_tokens(text)
    assert tokens > 0
    print(f"✓ Token 计数: '{text}' -> {tokens} tokens")

    # 测试空文本
    assert TokenCounter.count_tokens("") == 0

    # 测试中文文本
    chinese_text = "这是一个测试"
    tokens_cn = TokenCounter.count_tokens(chinese_text)
    assert tokens_cn > 0
    print(f"✓ 中文 Token 计数: {tokens_cn} tokens")


def test_token_counter_batch():
    """测试批量 Token 计数"""
    from src.ai_analysis.utils import TokenCounter

    texts = [
        "First text",
        "Second text",
        "Third text"
    ]

    total = TokenCounter.count_tokens_batch(texts)
    assert total > 0
    print(f"✓ 批量计数: {len(texts)} 条文本 -> {total} tokens")


def test_token_counter_truncate():
    """测试文本截断"""
    from src.ai_analysis.utils import TokenCounter

    long_text = "word " * 1000

    # 截断到 100 tokens
    truncated = TokenCounter.truncate_to_tokens(long_text, max_tokens=100)

    # 验证截断后的 token 数
    truncated_tokens = TokenCounter.count_tokens(truncated)
    assert truncated_tokens <= 100
    print(f"✓ 截断: 1000+ 词 -> {truncated_tokens} tokens")


def test_token_counter_split():
    """测试文本分割"""
    from src.ai_analysis.utils import TokenCounter

    long_text = "word " * 1000

    # 分割成每块 200 tokens
    chunks = TokenCounter.split_text_by_tokens(
        long_text,
        max_tokens_per_chunk=200,
        overlap=20
    )

    assert len(chunks) > 1
    print(f"✓ 分割: 长文本 -> {len(chunks)} 个块")

    # 验证每个块的 token 数
    for i, chunk in enumerate(chunks[:3]):  # 只检查前3个
        tokens = TokenCounter.count_tokens(chunk)
        print(f"  块 {i+1}: {tokens} tokens")


def test_token_counter_cost():
    """测试成本估算"""
    from src.ai_analysis.utils import TokenCounter

    # 测试 OpenAI 模型
    cost = TokenCounter.calculate_cost(
        input_tokens=1000,
        output_tokens=500,
        model="gpt-4o-mini"
    )

    assert cost > 0
    print(f"✓ OpenAI gpt-4o-mini 成本: 1000 input + 500 output = ${cost:.4f}")

    # 测试通义模型
    cost_tongyi = TokenCounter.calculate_cost(
        input_tokens=1000,
        output_tokens=500,
        model="qwen-plus"
    )

    assert cost_tongyi > 0
    print(f"✓ 通义 qwen-plus 成本: 1000 input + 500 output = ${cost_tongyi:.4f}")


# ============ Text Preprocessor Tests ============

def test_text_preprocessor_clean():
    """测试文本清理"""
    from src.ai_analysis.utils import TextPreprocessor

    # 测试移除多余空格
    text = "This    is    a   test"
    cleaned = TextPreprocessor.remove_redundancy(text)
    assert "   " not in cleaned
    print(f"✓ 移除多余空格")

    # 测试移除重复标点
    text = "Great!!!"
    cleaned = TextPreprocessor.remove_redundancy(text)
    assert "!!!" not in cleaned
    print(f"✓ 移除重复标点")


def test_text_preprocessor_extract():
    """测试关键句提取"""
    from src.ai_analysis.utils import TextPreprocessor

    text = (
        "First sentence here. "
        "Second sentence here. "
        "Third sentence here. "
        "Fourth sentence here. "
        "Fifth sentence here. "
        "Sixth sentence here. "
        "Seventh sentence here."
    )

    # 提取 3 个关键句
    extracted = TextPreprocessor.extract_key_sentences(text, max_sentences=3)

    assert len(extracted) < len(text)
    assert "First" in extracted or "Seventh" in extracted
    print(f"✓ 提取关键句: {len(text)} -> {len(extracted)} 字符")


def test_text_preprocessor_clean_for_analysis():
    """测试分析前清理"""
    from src.ai_analysis.utils import TextPreprocessor

    long_text = "word " * 1000

    cleaned = TextPreprocessor.clean_for_analysis(long_text, max_length=100)

    assert len(cleaned) <= 103  # 100 + "..."
    print(f"✓ 分析前清理: {len(long_text)} -> {len(cleaned)} 字符")


def test_text_preprocessor_extract_by_keywords():
    """测试按关键词提取"""
    from src.ai_analysis.utils import TextPreprocessor

    text = (
        "The price is very high. "
        "Quality is good but price is concerning. "
        "Features are nice. "
        "Customer service is excellent. "
        "Delivery was fast. "
        "Overall satisfied."
    )

    keywords = ["price", "quality"]
    extracted = TextPreprocessor.extract_by_keywords(
        text,
        keywords=keywords,
        sentences_per_keyword=2
    )

    assert len(extracted) < len(text)
    assert any(kw in extracted.lower() for kw in keywords)
    print(f"✓ 按关键词提取: 找到包含 '{', '.join(keywords)}' 的句子")


# ============ Logger Tests ============

def test_logger_initialization():
    """测试日志器初始化"""
    from src.ai_analysis.utils import get_analysis_logger

    logger = get_analysis_logger()
    assert logger is not None
    print("✓ 日志器初始化成功")


def test_logger_token_tracking():
    """测试 Token 追踪"""
    from src.ai_analysis.utils import get_analysis_logger

    logger = get_analysis_logger()
    logger.reset_token_tracking()

    # 记录一些 API 调用
    logger.log_api_call(
        operation="test_operation",
        model="gpt-4o-mini",
        input_tokens=1000,
        output_tokens=200,
        duration=1.5
    )

    logger.log_api_call(
        operation="test_operation_2",
        model="gpt-4o-mini",
        input_tokens=500,
        output_tokens=100,
        duration=0.8
    )

    # 验证统计
    assert logger.total_input_tokens == 1500
    assert logger.total_output_tokens == 300
    assert logger.api_calls == 2

    print(f"✓ Token 追踪: {logger.api_calls} 次调用, "
          f"{logger.total_input_tokens + logger.total_output_tokens} 总 tokens")


def test_logger_operation_timing():
    """测试操作计时"""
    import time
    from src.ai_analysis.utils import get_analysis_logger

    logger = get_analysis_logger()

    # 开始操作
    logger.start_operation("test_operation")
    time.sleep(0.1)
    logger.end_operation("test_operation")

    # 验证计时
    assert "test_operation" in logger.operation_durations
    duration = logger.operation_durations["test_operation"]
    assert duration >= 0.1

    print(f"✓ 操作计时: {duration:.2f}s")


def test_logger_batch_progress():
    """测试批次进度日志"""
    from src.ai_analysis.utils import get_analysis_logger

    logger = get_analysis_logger()

    # 不实际打印，只验证不报错
    logger.log_batch_progress("test_op", 1, 5, batch_size=10)
    logger.log_batch_progress("test_op", 3, 5)

    print("✓ 批次进度日志正常")


# ============ Map-Reduce Tests ============

@pytest.mark.asyncio
async def test_map_reduce_initialization():
    """测试 Map-Reduce 处理器初始化"""
    from src.ai_analysis.utils import MapReduceProcessor

    processor = MapReduceProcessor(
        max_tokens_per_chunk=2000,
        overlap=200,
        batch_size=5
    )

    assert processor is not None
    print("✓ Map-Reduce 处理器初始化成功")


@pytest.mark.asyncio
async def test_map_reduce_split_text():
    """测试文本分割"""
    from src.ai_analysis.utils import MapReduceProcessor

    processor = MapReduceProcessor(max_tokens_per_chunk=500)

    long_text = "word " * 1000

    chunks = processor.split_text(long_text)

    assert len(chunks) > 1
    print(f"✓ 文本分割: {len(chunks)} 个块")

    # 验证每个块
    for i, chunk in enumerate(chunks[:3]):
        print(f"  块 {i+1}: {len(chunk)} 字符")


@pytest.mark.asyncio
async def test_map_reduce_split_posts():
    """测试帖子分割"""
    from src.ai_analysis.utils import MapReduceProcessor

    processor = MapReduceProcessor(max_tokens_per_chunk=1000)

    posts = [
        {"content": f"Post content {i} " * 50}
        for i in range(20)
    ]

    batches = processor.split_posts(posts)

    assert len(batches) > 0
    assert len(batches) <= len(posts)

    print(f"✓ 帖子分割: {len(posts)} 帖子 -> {len(batches)} 批次")

    for i, batch in enumerate(batches[:3]):
        print(f"  批次 {i+1}: {len(batch)} 帖子")


@pytest.mark.asyncio
async def test_map_reduce_process():
    """测试 Map-Reduce 处理流程"""
    from src.ai_analysis.utils import MapReduceProcessor

    processor = MapReduceProcessor(
        max_tokens_per_chunk=200,
        batch_size=2
    )

    # 创建测试文本
    text = "word " * 500

    # Map 函数：计数词数
    async def map_func(chunk: str) -> int:
        return len(chunk.split())

    # Reduce 函数：求和
    async def reduce_func(results: list) -> int:
        return sum(results)

    result = await processor.process(
        text,
        map_func,
        reduce_func,
        "test_operation"
    )

    assert result > 0
    print(f"✓ Map-Reduce 处理: 总词数 = {result}")


@pytest.mark.asyncio
async def test_map_reduce_process_posts():
    """测试帖子 Map-Reduce 处理"""
    from src.ai_analysis.utils import MapReduceProcessor

    processor = MapReduceProcessor(
        max_tokens_per_chunk=1000,
        batch_size=3
    )

    posts = [
        {"content": f"Post {i}: " + "word " * 50}
        for i in range(10)
    ]

    # Map 函数：返回帖子数
    async def map_func(batch: list) -> int:
        return len(batch)

    # Reduce 函数：求和
    async def reduce_func(results: list) -> int:
        return sum(results)

    result = await processor.process_posts(
        posts,
        map_func,
        reduce_func,
        "test_posts_operation"
    )

    assert result == len(posts)
    print(f"✓ 帖子 Map-Reduce: 处理了 {result} 个帖子")


# ============ Key Sentence Extractor Tests ============

def test_key_sentence_extractor_position():
    """测试基于位置的关键句提取"""
    from src.ai_analysis.utils import KeySentenceExtractor

    text = (
        "Sentence one here. "
        "Sentence two here. "
        "Sentence three here. "
        "Sentence four here. "
        "Sentence five here. "
        "Sentence six here. "
        "Sentence seven here. "
        "Sentence eight here. "
        "Sentence nine here. "
        "Sentence ten here."
    )

    extracted = KeySentenceExtractor.extract_by_position(text, num_sentences=5)

    assert len(extracted) < len(text)
    assert "Sentence" in extracted
    print(f"✓ 基于位置提取: {len(text)} -> {len(extracted)} 字符")


def test_key_sentence_extractor_keywords():
    """测试基于关键词的关键句提取"""
    from src.ai_analysis.utils import KeySentenceExtractor

    text = (
        "The price is very affordable. "
        "Quality exceeds expectations. "
        "Features are comprehensive. "
        "Customer service is responsive. "
        "Delivery was prompt. "
        "Packaging was secure."
    )

    keywords = ["price", "quality", "service"]
    extracted = KeySentenceExtractor.extract_by_keywords(
        text,
        keywords=keywords,
        sentences_per_keyword=2
    )

    assert len(extracted) > 0
    assert any(kw in extracted.lower() for kw in keywords)
    print(f"✓ 基于关键词提取: 找到包含关键词的句子")


# ============ Integration Tests ============

@pytest.mark.asyncio
async def test_utils_integration():
    """集成测试：组合使用多个工具"""
    from src.ai_analysis.utils import (
        TokenCounter,
        TextPreprocessor,
        MapReduceProcessor
    )

    # 1. 清理长文本
    long_text = "word " * 1000 + "\n" + "sentence. " * 100
    cleaned = TextPreprocessor.clean_for_analysis(long_text, max_length=2000)

    # 2. 计数 tokens
    token_count = TokenCounter.count_tokens(cleaned)
    assert token_count > 0

    # 3. 使用 Map-Reduce 处理
    processor = MapReduceProcessor(max_tokens_per_chunk=500)

    async def map_func(chunk):
        return TokenCounter.count_tokens(chunk)

    async def reduce_func(results):
        return sum(results)

    result = await processor.process(
        cleaned,
        map_func,
        reduce_func,
        "integration_test"
    )

    assert result >= token_count  # 应该接近原始计数

    print(f"✓ 集成测试:")
    print(f"  原始文本: {len(long_text)} 字符")
    print(f"  清理后: {len(cleaned)} 字符")
    print(f"  Token 估算: {token_count}")
    print(f"  Map-Reduce 结果: {result}")


# ============ Main Function ============

def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("AI 分析工具函数完整测试套件")
    print("="*60 + "\n")

    # 运行同步测试
    test_groups = [
        ("Token Counter 基础", [
            test_token_counter_basic,
            test_token_counter_batch,
            test_token_counter_truncate,
            test_token_counter_split,
            test_token_counter_cost,
        ]),
        ("Text Preprocessor", [
            test_text_preprocessor_clean,
            test_text_preprocessor_extract,
            test_text_preprocessor_clean_for_analysis,
            test_text_preprocessor_extract_by_keywords,
        ]),
        ("Logger", [
            test_logger_initialization,
            test_logger_token_tracking,
            test_logger_operation_timing,
            test_logger_batch_progress,
        ]),
        ("Key Sentence Extractor", [
            test_key_sentence_extractor_position,
            test_key_sentence_extractor_keywords,
        ]),
    ]

    for group_name, tests in test_groups:
        print(f"\n{group_name}:")
        for test_func in tests:
            try:
                test_func()
            except AssertionError as e:
                print(f"  ✗ {test_func.__name__}: {e}")
            except Exception as e:
                print(f"  ✗ {test_func.__name__}: {type(e).__name__}: {e}")

    print("\n提示: 运行异步测试请使用:")
    print("  pytest tests/test_utils.py -v -s")


if __name__ == "__main__":
    run_all_tests()
