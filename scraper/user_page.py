from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import config_utils

config = config_utils.init_config('../config/config.ini')

# Follower/Follow 값을 가져오는 함수 분리
def get_element_text(driver, selector):
    try:
        return driver.find_element(By.CSS_SELECTOR, selector).text
    except Exception:
        return None


# like count, comment count js에 포함되어있음
def scrape(driver, url,):
    try:
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                                            'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section > ul > li:nth-child(1) > div > span > span'))
        )

        post_count = driver.find_element(By.CSS_SELECTOR,
                                         'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section > ul > li:nth-child(1) > div > span > span').text


        # 공개 계정인 경우
        follower_count = get_element_text(driver,
                                             'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section > ul > li:nth-child(2) > div > a > span > span')
        follow_count = get_element_text(driver,
                                           'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section > ul > li:nth-child(3) > div > a > span > span')

        if follower_count is not None and follow_count is not None:
            print(f"공개 계정 - Follower: {follower_count}, Follow: {follow_count}")
        else:
            # 비공개 계정인 경우
            follower_count = get_element_text(driver,
                                             'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section > ul > li:nth-child(2) > div > button > span > span')
            follow_count = get_element_text(driver,
                                           'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section> ul > li:nth-child(3) > div > button > span > span')
            if follower_count is None or follow_count is None:
                raise Exception("공개/비공개 계정의 Follower/Follow 정보를 가져오지 못했습니다.")
            else:
                print(f"비공개 계정 - Follower: {follower_count}, Follow: {follow_count}")

        results = {'post_count':post_count, 'follower_count':follower_count, 'follow_count':follow_count}
        return results

    except Exception as e:
        print(f"Error occurred: {e}")

