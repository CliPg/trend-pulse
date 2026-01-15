#!/usr/bin/env python3
"""
测试YouTube字幕API代理配置

使用方法：
1. 配置Webshare代理（推荐）：
   在.env文件中设置：
   WEBSHARE_PROXY_USERNAME=your_username
   WEBSHARE_PROXY_PASSWORD=your_password

2. 或者设置环境变量：
   export HTTP_PROXY=http://127.0.0.1:7890

3. 运行此脚本：
   python test_youtube_proxy.py
"""
import asyncio
import os
from dotenv import load_dotenv
from src.collectors.youtube import YouTubeCollector

# Load environment variables from .env file
load_dotenv()


async def test_transcript_with_current_config():
    """测试使用当前配置获取字幕"""

    # 检查代理配置
    webshare_username = os.getenv("WEBSHARE_PROXY_USERNAME")
    webshare_password = os.getenv("WEBSHARE_PROXY_PASSWORD")
    http_proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")

    if webshare_username and webshare_password:
        print(f"✓ 检测到Webshare代理配置")
        print(f"   用户名: {webshare_username}")
    elif http_proxy:
        print(f"✓ 检测到HTTP代理配置: {http_proxy}")
    else:
        print("⚠️  未检测到代理配置")
        print("💡 如果遇到IP封锁，请在.env文件中配置：")
        print("   # Webshare代理（推荐）")
        print("   WEBSHARE_PROXY_USERNAME=your_username")
        print("   WEBSHARE_PROXY_PASSWORD=your_password")
        print("   # 或使用HTTP代理")
        print("   HTTP_PROXY=http://127.0.0.1:7890")
        print()

    # 测试视频ID（您可以替换成任何YouTube视频ID）
    test_video_id = "xIFkrVU5Krk"

    print(f"📺 测试获取视频字幕...")
    print(f"   视频ID: {test_video_id}")
    print(f"   视频URL: https://www.youtube.com/watch?v={test_video_id}")
    print()

    # 创建collector实例
    config = {"YOUTUBE_API_KEY": "test"}  # API key不需要用于字幕测试
    collector = YouTubeCollector(config)

    # 测试视频对象
    video = {
        "id": test_video_id,
        "title": "Test Video",
        "channel_title": "Test Channel",
    }

    try:
        # 尝试获取字幕
        transcript = await collector._fetch_transcript(video, "en")

        if transcript:
            print("✓ 成功获取字幕！")
            print(f"   字幕长度: {len(transcript)} 字符")
            print(f"   前300字符预览:")
            print(f"   {transcript[:300]}...")
            print()
            print("🎉 代理配置正常工作！")
            return True
        else:
            print("✗ 无法获取字幕")
            print()
            print("可能的原因：")
            print("1. 视频没有字幕")
            print("2. IP被YouTube封锁（即使配置了代理）")
            print("3. 代理配置不正确")
            print()
            print("💡 解决方案：")
            print("   - 检查Webshare账号余额")
            print("   - 确认购买的是Residential代理套餐")
            print("   - 参考 docs/PROXY_SETUP.md 获取详细帮助")
            return False

    except Exception as e:
        print(f"✗ 发生错误: {str(e)}")
        print()
        print("💡 请检查：")
        print("   1. 是否正确设置了.env文件")
        print("   2. Webshare代理余额是否充足")
        print("   3. 网络连接是否正常")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("YouTube字幕API代理配置测试")
    print("=" * 60)
    print()

    success = asyncio.run(test_transcript_with_current_config())

    print()
    print("=" * 60)
    if success:
        print("✓ 测试通过")
    else:
        print("✗ 测试失败")
    print("=" * 60)
