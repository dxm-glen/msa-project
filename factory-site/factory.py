import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# API에서 데이터 가져오기
def fetch_data():
    url = "https://pdpklswsdfvhq5mccofnngi6ta0ohmnm.lambda-url.ap-northeast-2.on.aws/log"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("데이터를 가져오는데 실패했습니다.")
        return []

# 데이터 가져오기
data = fetch_data()

if data:
    # DataFrame으로 변환
    df = pd.DataFrame(data)

    # datetime 형식 변환
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # 최근 20개의 로그
    recent_logs = df.tail(20)

    # 제목
    st.header('공장 로그', divider='rainbow')

    # 레이아웃 설정
    col1, col2 = st.columns(2)

    with col1:
        st.header("최근 20개의 로그", divider="blue")
        st.dataframe(recent_logs[['log_id', 'requester', 'item_name', 'quantity', 'datetime']].rename(columns={
            'log_id': '로그 ID', 
            'requester': '요청자', 
            'item_name': '요청 아이템 이름', 
            'quantity': '수량', 
            'datetime': '신청 시간'
        }))

    with col2:
        st.header("요청자 이름으로 검색", divider="orange")
        requester_name = st.text_input("요청자 이름")
        
        if requester_name:
            filtered_logs = df[df['requester'].str.contains(requester_name, case=False, na=False)]
            st.dataframe(filtered_logs[['log_id', 'requester', 'item_name', 'quantity', 'datetime']].rename(columns={
                'log_id': '로그 ID', 
                'requester': '요청자', 
                'item_name': '요청 아이템 이름', 
                'quantity': '수량', 
                'datetime': '신청 시간'
            }))
        else:
            st.write("검색할 요청자 이름을 입력하세요.")

    # Streamlit 내장 divider 사용
    st.divider()

    # 요청 숫자가 가장 많은 요청자와 합계 수량이 가장 많은 요청자
    col3, col4 = st.columns(2)

    with col3:
        st.header("요청 횟수가 가장 많은 요청자", divider="green")
        requester_count = df['requester'].value_counts().reset_index()
        requester_count.columns = ['요청자', '요청 횟수']

        # Streamlit 내장 bar_chart 이용
        st.bar_chart(requester_count.head(10).set_index('요청자')['요청 횟수'])

    with col4:
        st.header("합계 수량이 가장 많은 요청자", divider="violet")
        requester_quantity = df.groupby('requester')['quantity'].sum().reset_index()
        requester_quantity = requester_quantity.sort_values(by='quantity', ascending=False)
        requester_quantity.columns = ['요청자', '합계 수량']

        # Streamlit 내장 bar_chart 이용
        st.bar_chart(requester_quantity.head(10).set_index('요청자')['합계 수량'])

    # Streamlit 내장 divider 사용
    st.divider()

    # 5분 단위로 요청 수 집계
    df['datetime'] = pd.to_datetime(df['datetime'])  # datetime 형식 변환
    df.set_index('datetime', inplace=True)
    
    # 마지막 데이터 기준 2시간 이전까지의 데이터만 사용
    end_time = df.index.max()
    start_time = end_time - timedelta(hours=2)
    filtered_df = df[start_time:end_time]

    requests_per_5min = filtered_df.resample('5T').size().reset_index(name='count')

    # 요청 수 5분 단위 그래프
    st.header("5분 단위 요청 수", divider="red")
    st.line_chart(requests_per_5min.set_index('datetime')['count'])
else:
    st.write("사용 가능한 데이터가 없습니다.")
