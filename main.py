
import argparse
import json
import subprocess
import sys

from scraper.keyword_search import scrape as keyword_search_instagram

if __name__ == '__main__':
    # Argument Parser 생성
    parser = argparse.ArgumentParser(description="Search Keyword for scraper.")

    # # 커맨드라인에서 받을 search keyword 추가
    parser.add_argument("--keyword", type=str, help="Search keyword")

    # 출력 파일 경로 (선택 인자, 기본값 제공)
    parser.add_argument(
        "--output",
        type=str,
        default="./output/test.json",  # 출력 파일 기본값 설정
        help="Path for saving the scraper output (default: 'output.txt')."
    )

    # 대시보드 실행 여부 플래그 추가
    parser.add_argument(
        "--dashboard",
        action="store_true",  # 플래그로 처리, 값 없이 실행하면 True로 설정
        help="Launch the Streamlit dashboard after scraping."
    )

    # 파라미터 파싱
    args = parser.parse_args()

    # 유효성 검사
    if not args.keyword:
        print("Error: Please provide either search keyword")
        sys.exit(1)


    if args.keyword:
        data_result = keyword_search_instagram(args.keyword)
    else:
        print("Error: Please provide either search option")
        sys.exit(1)

    json_data = json.dumps(data_result, ensure_ascii=False, indent=4)

    # 결과를 파일로 저장
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_data)
        print(f"Output successfully written to {args.output}")

    except Exception as e:
        print(f"Error writing to file {args.output}: {e}")
        sys.exit(1)  # 에러 발생 시 종료

    # Streamlit 대시보드 실행 (플래그가 설정된 경우)
    if args.dashboard:
        try:
            # subprocess 활용하여 Streamlit 실행
            print("Launching Streamlit dashboard...")
            subprocess.run(["streamlit", "run", "./scraper/dashboard.py", "--", args.output], check=True)

        except Exception as e:
            print(f"Error launching Streamlit dashboard: {e}")
            sys.exit(1)


