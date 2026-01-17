"""
诊断 Reddit 帖子跳过问题

查看为什么很多帖子被跳过
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote


def diagnose_skipping():
    """诊断为什么帖子被跳过"""

    keyword = "artificial intelligence"
    search_url = f"https://www.reddit.com/search/?q={quote(keyword)}&type=posts"

    print("=" * 60)
    print("Reddit 帖子跳过诊断")
    print("=" * 60)

    # 配置 Chrome
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=chrome_profile")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920, 1080)

    try:
        driver.get(search_url)
        print("\n等待页面加载...")
        time.sleep(5)

        print("\n" + "=" * 60)
        print("分析帖子元素")
        print("=" * 60)

        # 查找帖子
        posts1 = driver.find_elements("css selector", '[data-testid="search-post-unit"]')
        posts2 = driver.find_elements("css selector", '[data-testid="search-post-with-content-preview"]')

        print(f"\n选择器1: [data-testid=\"search-post-unit\"] - {len(posts1)} 个")
        print(f"选择器2: [data-testid=\"search-post-with-content-preview\"] - {len(posts2)} 个")

        # 检查是否有重复
        all_posts = posts1 + posts2
        print(f"总计: {len(all_posts)} 个元素")

        # 分析每个帖子
        print(f"\n" + "=" * 60)
        print("详细分析每个帖子元素")
        print("=" * 60)

        valid_posts = 0
        no_url = 0
        no_title = 0
        duplicate_urls = []

        seen_urls = {}

        for i, post in enumerate(all_posts[:20], 1):  # 只看前20个
            print(f"\n--- 帖子 {i} ---")

            # 尝试获取 URL
            try:
                link = post.find_element("css selector", '[data-testid="post-title"]')
                url = link.get_attribute('href')
                if url:
                    print(f"✅ URL: {url}")
                    if url in seen_urls:
                        duplicate_urls.append(url)
                        print(f"⚠️  重复的 URL (之前是帖子 {seen_urls[url]})")
                    else:
                        seen_urls[url] = i
                else:
                    print(f"❌ URL 元素存在但 href 为空")
                    no_url += 1
            except Exception as e:
                print(f"❌ 无法获取 URL: {e}")
                no_url += 1

            # 尝试获取标题
            try:
                title_elem = post.find_element("css selector", '[data-testid="post-title-text"]')
                title = title_elem.text
                print(f"✅ 标题: {title[:50]}")
                valid_posts += 1
            except Exception as e:
                print(f"❌ 无法获取标题: {e}")
                no_title += 1

            # 尝试获取子版
            try:
                sub_link = post.find_element("css selector", 'a[href^="/r/"]')
                subreddit = sub_link.text
                print(f"✅ 子版: {subreddit}")
            except Exception as e:
                print(f"❌ 无法获取子版: {e}")

        print(f"\n" + "=" * 60)
        print("统计结果")
        print("=" * 60)
        print(f"有效帖子: {valid_posts}")
        print(f"没有 URL: {no_url}")
        print(f"没有标题: {no_title}")
        print(f"重复 URL 数量: {len(duplicate_urls)}")

        if duplicate_urls:
            print(f"\n重复的 URLs:")
            for url in set(duplicate_urls):
                print(f"  - {url}")

        print(f"\n💡 问题分析:")
        if no_url > 0:
            print(f"  ⚠️  {no_url} 个帖子没有 URL，会被跳过")
        if len(duplicate_urls) > 0:
            print(f"  ⚠️  两个选择器返回了相同的元素！")
            print(f"      这是主要问题 - 使用两个选择器会导致重复")

        print(f"\n🔧 建议的修复:")
        print(f"  1. 只使用一个选择器")
        print(f"  2. 或者合并两个选择器的结果并去重")

        input("\n按 Enter 键关闭浏览器...")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()


if __name__ == "__main__":
    diagnose_skipping()
