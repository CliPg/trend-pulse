from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import json


def launch_chrome_browser():
    """
    启动 Chrome 浏览器（自动管理驱动版本，保存登录状态）
    """
    chrome_options = Options()

    # 用户数据目录，用于保存登录状态
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    print(f"使用用户数据目录: {user_data_dir}")

    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    # 反检测配置
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 设置真实的 User-Agent
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36")

    # 稳定性选项
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-infobars")

    print("正在启动浏览器...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # 设置浏览器窗口大小
    driver.set_window_size(1920, 1080)

    return driver


def scrape_tweets(driver, count=30):
    """
    爬取推文

    Args:
        driver: Selenium WebDriver 实例
        count: 要爬取的推文数量

    Returns:
        list: 推文列表
    """
    tweets = []
    last_height = 0

    print(f"开始爬取前 {count} 条推文...")

    while len(tweets) < count:
        # 查找所有推文元素
        tweet_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')

        for tweet_element in tweet_elements[len(tweets):count]:
            try:
                # 提取推文文本
                text_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="tweetText"]')
                text = text_element.text

                # 提取作者信息
                try:
                    author_element = tweet_element.find_element(By.CSS_SELECTOR, '[data-testid="User-Name"]')
                    author = author_element.text.split('\n')[0]
                except:
                    author = "未知用户"

                # 提取时间戳
                try:
                    time_element = tweet_element.find_element(By.CSS_SELECTOR, 'time')
                    timestamp = time_element.get_attribute('datetime')
                except:
                    timestamp = ""

                tweets.append({
                    'author': author,
                    'text': text,
                    'timestamp': timestamp
                })

                print(f"已爬取 {len(tweets)}/{count} 条推文")

            except Exception as e:
                print(f"提取推文时出错: {e}")
                continue

        if len(tweets) >= count:
            break

        # 滚动页面加载更多推文
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 检查是否到达底部
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("已到达页面底部")
            break
        last_height = new_height

    print(f"爬取完成！共获取 {len(tweets)} 条推文")
    return tweets


def search_twitter(driver, keyword):
    """
    在推特上搜索关键词

    Args:
        driver: Selenium WebDriver 实例
        keyword: 搜索关键词
    """
    # 构建搜索 URL
    from urllib.parse import quote
    search_url = f"https://x.com/search?q={quote(keyword)}&src=typed_query"
    driver.get(search_url)

    print(f"正在搜索: {keyword}")
    print(f"搜索 URL: {search_url}")

    # 等待页面加载
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]'))
        )
        print("搜索结果已加载")
    except:
        print("等待搜索结果超时")


def main():
    """主函数示例"""
    driver = launch_chrome_browser()
    print("浏览器启动成功！")

    try:
        # 获取搜索关键词
        keyword = "chatgpt"

        if keyword:
            search_twitter(driver, keyword)

            # 等待页面完全加载
            time.sleep(3)

            # 爬取前30条推文
            tweets = scrape_tweets(driver, count=30)

            # 保存到JSON文件
            output_file = f"tweets_{keyword}_{int(time.time())}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(tweets, f, ensure_ascii=False, indent=2)

            print(f"\n推文已保存到: {output_file}")

            # 打印前5条推文预览
            print("\n前5条推文预览:")
            for i, tweet in enumerate(tweets[:5], 1):
                print(f"\n--- 推文 {i} ---")
                print(f"作者: {tweet['author']}")
                print(f"内容: {tweet['text'][:100]}...")
        else:
            print("未输入关键词，直接访问探索页面")
            driver.get("https://x.com/explore")

        print(f"\n页面标题: {driver.title}")
        print(f"当前 URL: {driver.current_url}")

        # 保持浏览器打开，等待手动关闭
        print("\n浏览器已启动，手动关闭浏览器窗口即可退出...")
        input("按 Enter 键退出程序...")

    finally:
        # 关闭浏览器
        print("关闭浏览器...")
        driver.quit()


if __name__ == "__main__":
    main()
