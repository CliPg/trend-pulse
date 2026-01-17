"""
Reddit DOM 结构诊断工具

用于检查 Reddit 页面的实际 DOM 结构和 CSS 选择器
"""
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote


def diagnose_reddit_page():
    """诊断 Reddit 搜索页面的 DOM 结构"""

    keyword = "artificial intelligence"
    search_url = f"https://www.reddit.com/search/?q={quote(keyword)}&type=posts"

    print("=" * 60)
    print("Reddit DOM 结构诊断工具")
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

        print("\n⏳ 等待页面加载（10秒）...")
        print("   请在浏览器中手动登录（如果需要）")
        time.sleep(10)

        print("\n" + "=" * 60)
        print("开始诊断 DOM 结构")
        print("=" * 60)

        # 1. 检查页面标题
        print(f"\n1. 页面标题: {driver.title}")
        print(f"   当前 URL: {driver.current_url}")

        # 2. 尝试不同的帖子容器选择器
        print(f"\n2. 测试不同的帖子容器选择器:")

        selectors_to_test = [
            '[data-testid="post-container"]',
            '[data-testid="post"]',
            'div[data-testid="postcontainer"]',
            '.Post',
            'article',
            '[data-adclicklocation="post"]',
            'div[data-testid="feed"]',
        ]

        found_selector = None
        for selector in selectors_to_test:
            try:
                elements = driver.find_elements("css selector", selector)
                if elements:
                    print(f"   ✅ '{selector}' 找到 {len(elements)} 个元素")
                    if not found_selector:
                        found_selector = selector
                else:
                    print(f"   ❌ '{selector}' 未找到任何元素")
            except Exception as e:
                print(f"   ❌ '{selector}' 出错: {e}")

        # 3. 分析第一个帖子元素的结构
        if found_selector:
            print(f"\n3. 使用选择器 '{found_selector}' 分析第一个帖子:")

            posts = driver.find_elements("css selector", found_selector)
            if posts:
                first_post = posts[0]

                print(f"\n   帖子 HTML (前 500 字符):")
                print(f"   {first_post.get_attribute('innerHTML')[:500]}...")

                # 4. 测试标题选择器
                print(f"\n4. 测试标题选择器:")
                title_selectors = [
                    'h3',
                    '[data-testid="post-content"] h3',
                    'h3[slot="title"]',
                    '.Post-title',
                    'a[data-click-id="title"]',
                    '.title',
                ]

                for selector in title_selectors:
                    try:
                        element = first_post.find_element("css selector", selector)
                        if element:
                            print(f"   ✅ '{selector}' -> {element.text[:50]}")
                    except:
                        print(f"   ❌ '{selector}' 未找到")

                # 5. 测试作者选择器
                print(f"\n5. 测试作者选择器:")
                author_selectors = [
                    '[data-testid="post-author-link"]',
                    'a[href*="/user/"]',
                    '[data-testid="post_author_link"]',
                    '.author',
                    '.username',
                ]

                for selector in author_selectors:
                    try:
                        element = first_post.find_element("css selector", selector)
                        if element:
                            print(f"   ✅ '{selector}' -> {element.text}")
                    except:
                        print(f"   ❌ '{selector}' 未找到")

                # 6. 测试点赞数选择器
                print(f"\n6. 测试点赞数选择器:")
                vote_selectors = [
                    '[data-testid="post-vote-score"]',
                    'div[data-testid="vote-section"]',
                    '.score',
                    '[slot="post-title-container"] div',
                    '.Post-vote-score',
                ]

                for selector in vote_selectors:
                    try:
                        element = first_post.find_element("css selector", selector)
                        if element:
                            print(f"   ✅ '{selector}' -> {element.text}")
                    except:
                        print(f"   ❌ '{selector}' 未找到")

                # 7. 测试评论数选择器
                print(f"\n7. 测试评论数选择器:")
                comment_selectors = [
                    'a[href*="/comments/"]',
                    '[data-testid="comments"]',
                    '.comments',
                ]

                for selector in comment_selectors:
                    try:
                        element = first_post.find_element("css selector", selector)
                        if element:
                            print(f"   ✅ '{selector}' -> {element.text}")
                    except:
                        print(f"   ❌ '{selector}' 未找到")

                # 8. 测试时间选择器
                print(f"\n8. 测试时间选择器:")
                time_selectors = [
                    'time',
                    '[data-testid="post_timestamp"]',
                    'span[data-click-id="timestamp"]',
                    '.Post-timestamp',
                ]

                for selector in time_selectors:
                    try:
                        element = first_post.find_element("css selector", selector)
                        if element:
                            datetime_attr = element.get_attribute('datetime')
                            print(f"   ✅ '{selector}' -> 文本: {element.text}, datetime: {datetime_attr}")
                    except:
                        print(f"   ❌ '{selector}' 未找到")

        # 9. 保存页面源代码到文件
        print(f"\n9. 保存页面源代码到 'reddit_page_source.html'...")
        with open("reddit_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"   ✅ 页面源代码已保存")

        print("\n" + "=" * 60)
        print("诊断完成！")
        print("=" * 60)
        print("\n💡 提示:")
        print("   1. 查看 reddit_page_source.html 了解完整的页面结构")
        print("   2. 根据上面的输出，选择正确的 CSS 选择器")
        print("   3. 按 Ctrl+C 退出")

        # 保持浏览器打开，方便查看
        input("\n按 Enter 键关闭浏览器...")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()


if __name__ == "__main__":
    diagnose_reddit_page()
