"""
Reddit Collector 实际爬取测试

使用真实的 RedditCollector 爬取指定关键词的帖子
用于验证 Selenium 爬虫的功能

运行方法:
    # 普通模式（headless）
    python backend/tests/test_reddit_scrap.py

    # 调试模式（显示浏览器窗口）
    SHOW_BROWSER=true python backend/tests/test_reddit_scrap.py
"""
import asyncio
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.collectors.reddit import RedditCollector


async def test_reddit_collector():
    """测试 RedditCollector 爬取功能"""

    print("=" * 60)
    print("Reddit Collector 实际爬取测试")
    print("=" * 60)

    # 配置（不需要 API credentials）
    config = {
        "REDDIT_FETCH_FULL_CONTENT": True  # 设置为 False 可以只获取标题，速度更快
    }
    collector = RedditCollector(config)

    # 测试参数
    keyword = "chatgpt"  # 可以修改为其他关键词
    language = "en"      # Reddit 不使用语言过滤，但保持接口一致性
    limit = 10           # 爬取数量

    print(f"\n📋 测试配置:")
    print(f"   关键词: {keyword}")
    print(f"   数量: {limit}")
    print(f"   获取完整内容: {'是' if config['REDDIT_FETCH_FULL_CONTENT'] else '否'}")
    print(f"\n⏱️  开始爬取...")
    if config['REDDIT_FETCH_FULL_CONTENT']:
        print(f"注意: 获取完整内容需要访问每个帖子页面，会比较慢（每个帖子约3-5秒）")
    print()

    try:
        # 执行爬取
        posts = await collector.search(
            keyword=keyword,
            language=language,
            limit=limit
        )

        print(f"\n✅ 爬取完成！共获取 {len(posts)} 条帖子")
        print("=" * 60)

        if posts:
            # 保存结果到 JSON 文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"reddit_{keyword.replace(' ', '_')}_{timestamp}.json"

            # 转换 PostData 对象为字典
            posts_dict = [
                {
                    "platform": post.platform,
                    "post_id": post.post_id,
                    "author": post.author,
                    "content": post.content[:200] + "..." if len(post.content) > 200 else post.content,
                    "url": post.url,
                    "upvotes": post.upvotes,
                    "comments_count": post.comments_count,
                    "created_at": post.created_at
                }
                for post in posts
            ]

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(posts_dict, f, ensure_ascii=False, indent=2)

            print(f"\n💾 结果已保存到: {output_file}")

            # 显示前 5 条帖子预览
            print(f"\n📰 前 5 条帖子预览:")
            print("=" * 60)

            for i, post in enumerate(posts[:5], 1):
                print(f"\n--- 帖子 {i} ---")
                print(f"作者: {post.author}")
                print(f"内容: {post.content[:150]}{'...' if len(post.content) > 150 else ''}")
                print(f"链接: {post.url}")
                print(f"互动: 👍 {post.upvotes} | 💬 {post.comments_count}")
                if post.created_at:
                    print(f"时间: {post.created_at}")

            # 统计信息
            print(f"\n📊 统计信息:")
            print("=" * 60)
            total_upvotes = sum(post.upvotes for post in posts)
            total_comments = sum(post.comments_count for post in posts)

            print(f"总帖子数: {len(posts)}")
            print(f"总点赞数: {total_upvotes}")
            print(f"总评论数: {total_comments}")
            print(f"平均点赞: {total_upvotes // len(posts) if posts else 0}")
            print(f"平均评论: {total_comments // len(posts) if posts else 0}")

        else:
            print("\n⚠️  未获取到任何帖子")
            print("可能的原因:")
            print("  1. 网络连接问题")
            print("  2. 关键词无搜索结果")
            print("  3. Reddit 页面结构变化")

    except Exception as e:
        print(f"\n❌ 爬取失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试结束")
    print("=" * 60)


def test_sync_wrapper():
    """同步包装器，用于直接运行"""
    asyncio.run(test_reddit_collector())


if __name__ == "__main__":
    test_sync_wrapper()
