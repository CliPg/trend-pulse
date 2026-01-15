#!/usr/bin/env python3
"""
快速验证脚本 - 检查 LangChain 是否正确安装
"""
import sys


def test_imports():
    """测试所有必需的导入"""
    print("测试 LangChain 相关导入...")
    print("=" * 60)

    tests = [
        ("langchain-core", "from langchain_core.prompts import PromptTemplate"),
        ("langchain-core messages", "from langchain_core.messages import HumanMessage, SystemMessage"),
        ("langchain-core documents", "from langchain_core.documents import Document"),
        ("langchain-core output parsers", "from langchain_core.output_parsers import StrOutputParser, JsonOutputParser"),
        ("langchain-core runnables", "from langchain_core.runnables import Runnable"),
        ("langchain-openai", "from langchain_openai import ChatOpenAI"),
        ("langchain-text-splitters", "from langchain_text_splitters import RecursiveCharacterTextSplitter"),
    ]

    passed = 0
    failed = 0

    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✓ {name}")
            passed += 1
        except ImportError as e:
            print(f"✗ {name}: {e}")
            failed += 1

    print("=" * 60)
    print(f"结果: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n✅ 所有导入测试通过!")
        return 0
    else:
        print(f"\n❌ {failed} 个导入失败")
        print("\n请运行: pip install -r requirements.txt")
        return 1


def test_module_structure():
    """测试模块结构"""
    print("\n测试模块结构...")
    print("=" * 60)

    try:
        from src.ai_analysis.pipeline_v2 import AnalysisPipelineV2
        print("✓ AnalysisPipelineV2")

        from src.ai_analysis.sentiment_v2 import SentimentAnalyzerV2
        print("✓ SentimentAnalyzerV2")

        from src.ai_analysis.clustering_v2 import OpinionClustererV2
        print("✓ OpinionClustererV2")

        from src.ai_analysis.summarizer_v2 import SummarizerV2
        print("✓ SummarizerV2")

        from src.ai_analysis.utils import TokenCounter, TextPreprocessor, MapReduceProcessor
        print("✓ Utils (TokenCounter, TextPreprocessor, MapReduceProcessor)")

        print("=" * 60)
        print("✅ 模块结构正常!")
        return 0

    except ImportError as e:
        print(f"✗ 模块导入失败: {e}")
        print("=" * 60)
        return 1


def main():
    """主函数"""
    print("\nLangChain 安装验证脚本")
    print("=" * 60)
    print()

    # 测试导入
    result1 = test_imports()

    # 测试模块结构
    result2 = test_module_structure()

    if result1 == 0 and result2 == 0:
        print("\n" + "=" * 60)
        print("🎉 所有验证通过! 可以开始使用了")
        print("=" * 60)
        print("\n下一步:")
        print("1. 运行单元测试: pytest tests/test_utils.py -v")
        print("2. 运行集成测试: pytest tests/test_sentiment_v2.py -m integration -v -s")
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ 验证失败，请检查安装")
        print("=" * 60)
        print("\n故障排查:")
        print("1. 查看: docs/LANGCHAIN_FIX.md")
        print("2. 运行: pip install -r requirements.txt")
        print("3. 参考: docs/INSTALLATION.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
