import json
import re
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import config_utils, driver_utils

config = config_utils.init_config('../config/config.ini')

def structured_extraction(json_data):
    try:
        # 단계별로 JSON 구조를 탐색하며 추출
        # 1. 최상단 "require" 키 확인 및 리스트의 첫 번째 요소 접근
        require_data = json_data.get("require")
        if not require_data or len(require_data) == 0:
            return None  # 조건 불만족

        # 2. 첫 번째 배열의 [0][3][0] 접근
        step_1 = require_data[0][3][0].get("__bbox")
        if not step_1:
            return None  # 조건 불만족

        # 3. "__bbox" 내부 "require" 키 탐색
        step_2 = step_1.get("require")
        if not step_2 or len(step_2) == 0:
            return None  # 조건 불만족

        # 4. "RelayPrefetchedStreamCache"나 "adp_PolarisPostRootQueryRelayPreloader_*" 키 데이터 확인
        preloader_data = step_2[0][3][1].get("__bbox")
        if not preloader_data:
            return None  # 조건 불만족

        # 5. "__bbox" 내부 "result" 키 확인
        result_data = preloader_data.get("result")
        if not result_data:
            return None  # 조건 불만족

        # 6. "result" 내부 "data" 확인
        data = result_data.get("data")
        if not data:
            return None  # 조건 불만족

        # 7. "data" 내부 "xdt_api__v1__media__shortcode__web_info" 탐색
        media_info = data.get("xdt_api__v1__media__shortcode__web_info")
        if not media_info:
            return None  # 조건 불만족

        # 8. 최종적으로 "items" 데이터 추출
        items = media_info.get("items")
        if not items:
            return None  # 조건 불만족

        # 데이터 추출 성공
        return items

    except Exception as e:
        print(f" at structured_extraction - Error during extraction: {e}")
        return None


# like count, comment count js에 포함되어있음
def scrape(driver, url,):
    try:
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[role=link][tabindex="0"]'))
        )
        time.sleep(2)

        # 페이지 소스 가져오기
        page_html = driver.page_source

        # 만약 분석이 필요하다면 BeautifulSoup을 사용할 수 있음
        soup = BeautifulSoup(page_html, 'html.parser')

        # 스크립트 태그 찾기
        script_tags = soup.find_all('script', attrs={'data-content-len': True})
        keyword = "adp_PolarisPostRootQueryRelayPreloader"

        results = {}  # 결과를 저장할 딕셔너리

        for script in script_tags:
            if script.string and keyword in script.string:
                # JSON 문자열 추출
                match = re.search(r'{.*}', script.string)  # 중괄호로 JSON을 매칭
                if match:
                    json_data = match.group()
                    parsed_json = json.loads(json_data)  # JSON 파싱

                    # 구조화된 탐색
                    items = structured_extraction(parsed_json)
                    if items is not None:

                        username = items[0]['owner']['username']
                        comment_count = items[0]['comment_count']
                        like_count = items[0]['like_count']

                        results = {'username':username, 'comment_count':comment_count, 'like_count':like_count}

                        # 디버깅 출력
                        # print(f"username : {username} , comment_count : {comment_count} , like_count : {like_count}")
                        # print(json.dumps(parsed_json, indent=4, ensure_ascii=False))
                        break  # 첫 번째 매칭된 JSON에서 결과를 찾으면 중단

        return results

    except Exception as e:
        print(f"Error occurred: {e}")

