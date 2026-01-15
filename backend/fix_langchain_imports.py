#!/usr/bin/env python3
"""
LangChain 导入修复脚本

自动修复所有 langchain 相关的导入问题
"""
import os
import re
from pathlib import Path


def fix_imports(file_path):
    """修复单个文件的导入"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 修复导入
    replacements = [
        # langchain.schema -> langchain_core.documents / langchain_core.messages
        (r'from langchain\.schema import Document', 'from langchain_core.documents import Document'),
        (r'from langchain\.schema import', 'from langchain_core.messages import'),

        # langchain.prompts -> langchain_core.prompts
        (r'from langchain\.prompts import', 'from langchain_core.prompts import'),
        (r'from langchain\.prompts\.example_selector import', 'from langchain_core.prompts.example_selector import'),

        # langchain.text_splitter -> langchain_text_splitters
        (r'from langchain\.text_splitter import', 'from langchain_text_splitters import'),

        # langchain.output_parsers -> langchain_core.output_parsers
        (r'from langchain\.output_parsers import', 'from langchain_core.output_parsers'),

        # langchain.runnables -> langchain_core.runnables
        (r'from langchain\.runnables import', 'from langchain_core.runnables'),

        # langchain.chat_models -> langchain_openai
        (r'from langchain\.chat_models import', 'from langchain_openai import'),
        (r'from langchain\.llms import', 'from langchain_openai import'),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # 如果内容有变化，写回文件
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    """主函数"""
    print("LangChain 导入修复脚本")
    print("=" * 60)

    # 获取脚本所在目录
    script_dir = Path(__file__).parent
    src_dir = script_dir / "src" / "ai_analysis"

    if not src_dir.exists():
        print(f"错误: 找不到目录 {src_dir}")
        return 1

    # 查找所有 Python 文件
    python_files = list(src_dir.rglob("*.py"))

    print(f"找到 {len(python_files)} 个 Python 文件")
    print()

    fixed_count = 0

    for file_path in python_files:
        if fix_imports(file_path):
            print(f"✓ 修复: {file_path.relative_to(script_dir)}")
            fixed_count += 1

    print()
    print("=" * 60)
    print(f"修复完成! 共修复 {fixed_count} 个文件")
    print()

    # 检查 requirements.txt
    requirements_file = script_dir / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, 'r') as f:
            content = f.read()

        required_packages = [
            'langchain-core',
            'langchain-text-splitters',
        ]

        missing = []
        for package in required_packages:
            if package not in content:
                missing.append(package)

        if missing:
            print("⚠️  建议: 在 requirements.txt 中添加以下包:")
            for package in missing:
                print(f"   {package}>=0.1.0")
            print()

    print("下一步:")
    print("1. 运行: pip install -r requirements.txt")
    print("2. 验证: python -c 'from langchain_core.prompts import PromptTemplate'")
    print("3. 测试: pytest tests/test_utils.py -v")

    return 0


if __name__ == "__main__":
    exit(main())
