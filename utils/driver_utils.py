from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def create_driver(headless=False, proxy=None):
    """드라이버를 안전하게 생성하고 반환"""
    options = Options()
    options.add_argument('--no-sandbox')  # 보안 기능 비활성
    options.add_argument("--disable-extensions")  # 확장 프로그램 비활성
    options.add_argument("disable-blink-features=AutomationControlled")  # 자동화 탐지 방지
    options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
    options.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 기능 사용 안 함

    # browser 콘솔 창에서 navigator.userAgent
    user_agent = "'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'"
    options.add_argument('user-agent=' + user_agent)

    # 프록시 설정 추가
    if proxy:
        options.add_argument(f'--proxy-server={proxy}')

    if headless:
        options.add_argument('--headless')

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )