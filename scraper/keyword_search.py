import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from scraper.feed import scrape as insta_feed_scrape
from scraper.user_page import scrape as user_page_scrape

from utils import config_utils, driver_utils, file_utils

config = config_utils.init_config('../config/config.ini')
proxy = config['PROXY']['proxy_server']

def scrape(search_keyword,):
    try:
        if proxy:
            driver = driver_utils.create_driver(headless=False, proxy=proxy)
        else:
            driver = driver_utils.create_driver(headless=False)
        driver.implicitly_wait(10)  # 동기화
        driver.set_window_position(2048, 0)  # 우측 세컨 모니터를 이용하기 위해 왼쪽 메인 모니터 width 만큼 이동

        driver.get('https://www.instagram.com/explore/search/keyword/?q={}'.format(search_keyword))

        # login
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))
        )

        # input search word
        search_input = driver.find_element(By.CSS_SELECTOR, 'input[name="username"]')
        search_input.send_keys(config['INSTAGRAM']['id'])

        search_input = driver.find_element(By.CSS_SELECTOR, 'input[name="password"]')
        search_input.send_keys(config['INSTAGRAM']['password'])

        search_input.submit()

        time.sleep(3)

        # !주의!
        # 1. 프록시 사용시에는 로그인 이후에 인증 코드를 요구하는 경우가 있음, 이메일 또는 휴대폰으로.
        # 2. 계정이 차단이 되어버림
        # 따라서, 단 건으로 처리 할 때 말고 오토메이션에는 적당하지 않을 듯.

        # URL이 'https://www.instagram.com/accounts/onetap/'을 포함할 때까지 대기
        WebDriverWait(driver, 15).until(
            lambda driver: "https://www.instagram.com/accounts/onetap/" in driver.current_url)

        driver.get('https://www.instagram.com/explore/search/keyword/?q={}'.format(search_keyword))

        print("driver.current_url : ", driver.current_url)
        time.sleep(2)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[role=link][tabindex="0"][href^="/p/"]'))
        )

        # 페이징 처리
        limit_count = int(config['CONFIG']['video_limit_cnt'])
        timeout_sec = int(config['CONFIG']['timeout_sec'])
        start_time = time.time()  # 현재 시간을 기록
        total_listings = []
        visited_urls = set()  # 중복 방지를 위한 Set
        previous_list_size = 0
        scroll_position = 500
        scroll_increment = 300

        while True:
            try:
                scroll_position += scroll_increment
                driver.execute_script(f"window.scrollTo(0, {scroll_position});")

                time.sleep(2)

                target_els = driver.find_elements(By.CSS_SELECTOR, 'a[role=link][tabindex="0"][href^="/p/"]')
                print("len(targer_els) : " , len(target_els))

                for el in target_els[previous_list_size:]:
                    feed_url = el.get_attribute('href')
                    if feed_url not in visited_urls:
                        start_time = time.time()
                        visited_urls.add(feed_url)  # Set에 추가
                        total_listings.append(feed_url)
                        print("appended url total len : ", len(total_listings))

                # # 가져옥 목록 수가 이전 목록수와 동일하면서 시간이 리미트 시간이 경과했을때 break
                if len(target_els) == previous_list_size and time.time() - start_time > timeout_sec:
                    print("len(target_els) == previous_list_size and time.time() - start_time > timeout_sec")
                    break

                # limit count
                if len(total_listings) >= limit_count:
                    print("len(total_listings) >= limit_count")
                    total_listings = total_listings[:limit_count]
                    break

                # !!!insta는 end message 없음
                # page_html = driver.page_source
                # if "결과가 더 이상 없습니다" in page_html:
                #     print("더 이상 결과가 없습니다. 반복문 종료.")
                #     break
                # else:
                #     print("'결과가 더 이상 없습니다' 메시지가 발견되지 않았습니다. 계속 진행.")

                previous_list_size = len(target_els)

            except Exception as e:
                print("error scrolling down: {}".format(e))
                break

        print("test : ", total_listings)

        result_info = []

        for idx, feed_url in enumerate(total_listings):
            if "legal" not in feed_url and "location" not in feed_url:
                # feed
                insta_feed = insta_feed_scrape(driver, feed_url)
                # page
                user_page = user_page_scrape(driver, 'https://www.instagram.com/' + insta_feed['username'])

                result_info.append(
                    {
                        'username':insta_feed['username'],
                        'comment_count':insta_feed['comment_count'],
                        'like_count':insta_feed['like_count'],
                        'post_count':user_page['post_count'],
                        'follower_count':user_page['follower_count'],
                        'follow_count':user_page['follow_count'],
                     }
                )

        result = {'search_keyword': search_keyword, 'data': result_info, 'scrape_date': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))}
        return result

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # 리소스 정리
        if driver:
            print("Driver closed")
            driver.close()
            driver.quit()  # 드라이버 종료



if __name__ == "__main__":
    result_info = scrape('강아지사료')
    file_utils.make_result_json(result_info, output_path='../output/output2.json')