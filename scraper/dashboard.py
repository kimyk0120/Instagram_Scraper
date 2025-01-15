import json
import sys

import pandas as pd
import streamlit as st

# 명령줄 인자에서 출력 파일 경로 가져오기
def load_data_from_args():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]  # 첫 번째 명령줄 인자
        return file_path
    else:
        st.error("No data file provided. Please run the script with a JSON file.")
        st.stop()

file_path = load_data_from_args()

# JSON 데이터 로드
def load_data(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error reading the JSON file: {e}")
        st.stop()

data = load_data(file_path)

# 키워드와 스크래핑 날짜 표시
if "search_keyword" in data and "scrape_date" in data:
    st.subheader(f"Search Keyword: {data['search_keyword']}")
    st.write(f"Scrape Date: {data['scrape_date']}")
else:
    st.warning("No keyword or scrape date information available.")

# JSON 데이터를 DataFrame으로 변환
df = pd.DataFrame(data["data"])


# 자료 가공: 숫자 데이터 정리
def normalize_numbers(value):
    if isinstance(value, str) and "만" in value:
        return int(float(value.replace("만", "")) * 10000)
    elif isinstance(value, str) and "억" in value:
        return int(float(value.replace("억", "")) * 100000000)
    elif isinstance(value, str):
        return int(value.replace(",", ""))
    return value


numerical_columns = ["post_count", "follower_count", "follow_count"]
for col in numerical_columns:
    df[col] = df[col].apply(normalize_numbers)

# 표(Table) 표시
st.subheader("User Data")
st.dataframe(df)

# 통계 정보 표시
st.subheader("Statistics")
col1, col2 = st.columns(2)

with col1:
    st.metric("Total Users", len(df))
    st.metric("Total Likes", df["like_count"].sum())
with col2:
    st.metric("Total Comments", df["comment_count"].sum())
    st.metric("Total Followers", df["follower_count"].sum())

# 시각화 - 팔로워와 좋아요 수 비교 (Bar Chart)
st.subheader("Follower vs Likes")
st.bar_chart(df[["username", "follower_count", "like_count"]].set_index("username"))

# 시각화 - 포스트 개수 비교 (Pie Chart)
st.subheader("Post Count Distribution")
st.bar_chart(df[["username", "post_count"]].set_index("username"))
