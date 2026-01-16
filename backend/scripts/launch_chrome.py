from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os


def launch_chrome_browser():
    """
    启动 Chrome 浏览器（自动管理驱动版本）

    Args:
        headless: 是否无头模式运行（不显示浏览器窗口）
    """
    print("正在配置 Chrome 选项...")
    chrome_options = Options()
    user_data_dir = os.path.join(os.getcwd(), "chrome_profile")
    print(f"使用用户数据目录: {user_data_dir}")

    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    # 其他常用选项
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 使用 webdriver-manager 自动下载并使用匹配的 ChromeDriver
    print("正在初始化 ChromeDriver...")
    service = Service(ChromeDriverManager().install())
    print("正在启动 Chrome 浏览器...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    print("Chrome 浏览器启动成功！")

    # 设置浏览器窗口大小
    driver.set_window_size(1920, 1080)

    return driver


def main():
    """主函数示例"""
    print("=== Chrome 浏览器启动脚本 ===")
    # 启动浏览器（有界面模式）
    driver = launch_chrome_browser()

    try:
        # 访问网页
        print("正在访问 https://x.com/explore ...")
        driver.get("https://x.com/explore")

        print(f"页面标题: {driver.title}")
        print(f"当前 URL: {driver.current_url}")

        # 保持浏览器打开，等待手动关闭
        print("浏览器已启动，手动关闭浏览器窗口即可退出...")
        input("按 Enter 键退出程序...")

    finally:
        # 关闭浏览器
        print("关闭浏览器...")
        driver.quit()


if __name__ == "__main__":
    main()