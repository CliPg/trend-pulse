"""
Twitter Collector 实际爬取测试

使用真实的 TwitterCollector 爬取指定关键词的推文
用于验证 Selenium 爬虫的功能

运行方法:
    python backend/tests/test_twitter_scrap.py
"""
import asyncio
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.collectors.twitter import TwitterCollector


async def test_twitter_collector():
    """测试 TwitterCollector 爬取功能"""

    print("=" * 60)
    print("Twitter Collector 实际爬取测试")
    print("=" * 60)

    # 配置
    config = {}
    collector = TwitterCollector(config)

    # 测试参数
    keyword = "chatgpt"  # 可以修改为其他关键词
    language = "en"      # 可以修改为 "zh" 测试中文
    limit = 10           # 爬取数量

    print(f"\n📋 测试配置:")
    print(f"   关键词: {keyword}")
    print(f"   语言: {language}")
    print(f"   数量: {limit}")
    print(f"\n⏱️  开始爬取...\n")

    try:
        # 执行爬取
        posts = await collector.search(
            keyword=keyword,
            language=language,
            limit=limit
        )

        print(f"\n✅ 爬取完成！共获取 {len(posts)} 条推文")
        print("=" * 60)

        if posts:
            # 保存结果到 JSON 文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"tweets_{keyword}_{timestamp}.json"

            # 转换 PostData 对象为字典
            posts_dict = [
                {
                    "platform": post.platform,
                    "post_id": post.post_id,
                    "author": post.author,
                    "content": post.content,
                    "url": post.url,
                    "likes": post.likes,
                    "shares": post.shares,
                    "comments_count": post.comments_count,
                    "created_at": post.created_at
                }
                for post in posts
            ]

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(posts_dict, f, ensure_ascii=False, indent=2)

            print(f"\n💾 结果已保存到: {output_file}")

            # 显示前 5 条推文预览
            print(f"\n📰 前 5 条推文预览:")
            print("=" * 60)

            for i, post in enumerate(posts[:5], 1):
                print(f"\n--- 推文 {i} ---")
                print(f"作者: {post.author}")
                print(f"内容: {post.content[:150]}{'...' if len(post.content) > 150 else ''}")
                print(f"链接: {post.url}")
                print(f"互动: 👍 {post.likes} | 🔄 {post.shares} | 💬 {post.comments_count}")
                if post.created_at:
                    print(f"时间: {post.created_at}")

            # 统计信息
            print(f"\n📊 统计信息:")
            print("=" * 60)
            total_likes = sum(post.likes for post in posts)
            total_shares = sum(post.shares for post in posts)
            total_comments = sum(post.comments_count for post in posts)

            print(f"总推文数: {len(posts)}")
            print(f"总点赞数: {total_likes}")
            print(f"总转发数: {total_shares}")
            print(f"总评论数: {total_comments}")
            print(f"平均点赞: {total_likes // len(posts) if posts else 0}")
            print(f"平均转发: {total_shares // len(posts) if posts else 0}")
            print(f"平均评论: {total_comments // len(posts) if posts else 0}")

        else:
            print("\n⚠️  未获取到任何推文")
            print("可能的原因:")
            print("  1. 需要登录 Twitter（请设置 SHOW_BROWSER=true 并手动登录）")
            print("  2. 网络连接问题")
            print("  3. Twitter 反爬虫检测")
            print("  4. 关键词无搜索结果")

    except Exception as e:
        print(f"\n❌ 爬取失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试结束")
    print("=" * 60)


def test_sync_wrapper():
    """同步包装器，用于直接运行"""
    asyncio.run(test_twitter_collector())


if __name__ == "__main__":
    test_sync_wrapper()
