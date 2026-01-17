"""
Reddit 滚动诊断工具

用于诊断为什么只能爬取少量帖子
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote


def diagnose_reddit_scrolling():
    """诊断 Reddit 滚动加载"""

    keyword = "artificial intelligence"
    search_url = f"https://www.reddit.com/search/?q={quote(keyword)}&type=posts"

    print("=" * 60)
    print("Reddit 滚动诊断工具")
    print("=" * 60)
    print(f"\n搜索 URL: {search_url}")
    print("\n正在启动浏览器...\n")

    # 配置 Chrome
    chrome_options = Options()
    chrome_options.add_argument("--user-data-dir=chrome_profile")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 启动浏览器
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_window_size(1920, 1080)

    try:
        print("正在访问 Reddit 搜索页面...")
        driver.get(search_url)

        print("\n⏳ 等待页面加载（5秒）...")
        time.sleep(5)

        print("\n" + "=" * 60)
        print("开始测试滚动加载")
        print("=" * 60)

        # 测试多次滚动
        for scroll_iteration in range(5):
            print(f"\n--- 滚动迭代 {scroll_iteration + 1} ---")

            # 查找帖子元素
            posts1 = driver.find_elements("css selector", '[data-testid="search-post-unit"]')
            posts2 = driver.find_elements("css selector", '[data-testid="search-post-with-content-preview"]')

            print(f"  [data-testid=\"search-post-unit\"] 找到: {len(posts1)} 个")
            print(f"  [data-testid=\"search-post-with-content-preview\"] 找到: {len(posts2)} 个")
            print(f"  总计: {len(posts1) + len(posts2)} 个帖子")

            # 显示前3个帖子的标题
            all_posts = posts1 + posts2
            if all_posts:
                print(f"\n  前3个帖子标题:")
                for i, post in enumerate(all_posts[:3], 1):
                    try:
                        title = post.find_element("css selector", '[data-testid="post-title-text"]')
                        print(f"    {i}. {title.text[:60]}...")
                    except:
                        print(f"    {i}. (无法获取标题)")

            # 滚动到底部
            print(f"\n  滚动到页面底部...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # 等待加载
            print(f"  等待3秒...")
            time.sleep(3)

            # 检查页面高度
            scroll_height = driver.execute_script("return document.body.scrollHeight")
            current_scroll = driver.execute_script("return window.pageYOffset")
            print(f"  页面高度: {scroll_height}px")
            print(f"  当前滚动位置: {current_scroll}px")

        print("\n" + "=" * 60)
        print("诊断完成！")
        print("=" * 60)
        print("\n💡 分析:")
        print("   如果帖子数量没有增加，可能是因为:")
        print("   1. Reddit 需要更长的等待时间")
        print("   2. 需要登录才能查看更多内容")
        print("   3. 页面使用了虚拟滚动，元素会被复用")
        print("   4. 选择器不正确")

        input("\n按 Enter 键关闭浏览器...")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()


if __name__ == "__main__":
    diagnose_reddit_scrolling()
