from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from utils import config_utils

config = config_utils.init_config('../config/config.ini')

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
        follower_count = driver.find_element(By.CSS_SELECTOR,
                                             'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section > ul > li:nth-child(2) > div > a > span > span').text
        follow_count = driver.find_element(By.CSS_SELECTOR,
                                           'div > div > div > div > div > div > div:nth-child(2) > div > div > section > main > div > header > section > ul > li:nth-child(3) > div > a > span > span').text

        results = {'post_count':post_count, 'follower_count':follower_count, 'follow_count':follow_count}
        return results

    except Exception as e:
        print(f"Error occurred: {e}")

