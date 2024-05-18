import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# API에서 데이터 가져오기
def fetch_data():
    url = "-"
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

    # 서울 타임존 설정
    seoul_tz = pytz.timezone('Asia/Seoul')

    # datetime 형식 변환 및 타임존 설정
    df['datetime'] = pd.to_datetime(df['datetime'], utc=True).dt.tz_convert(seoul_tz)
    df = df.sort_values(by='datetime', ascending=False)
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # 최근 20개의 로그
    recent_logs = df.head(20)

    # 제목
    st.header('🏭 :blue[NxtCloud - Factory] 생산 요청 로그 🏭', divider='rainbow')

    st.header("최근 20개의 :blue[로그]", divider='rainbow')
    st.dataframe(recent_logs[['requester', 'item_name', 'quantity', 'datetime']].rename(columns={
        'requester': '요청자', 
        'item_name': '요청 아이템 이름', 
        'quantity': '수량', 
        'datetime': '신청 시간'
    }))

    st.header("요청자 :blue[이름]으로 :blue[검색]", divider='rainbow')
    requester_name = st.text_input("요청자 이름")
    
    if requester_name:
        filtered_logs = df[df['requester'].str.contains(requester_name, case=False, na=False)]
        st.dataframe(filtered_logs[['requester', 'item_name', 'quantity', 'datetime']].rename(columns={
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
        st.header("요청자 별 :blue[요청 횟수]", divider='rainbow')
        requester_count = df['requester'].value_counts().reset_index()
        requester_count.columns = ['요청자', '요청 횟수']

        # Streamlit 내장 bar_chart 이용
        st.bar_chart(requester_count.head(10).set_index('요청자')['요청 횟수'])

    with col4:
        st.header("요청자 별 :blue[합계 수량]", divider='rainbow')
        requester_quantity = df.groupby('requester')['quantity'].sum().reset_index()
        requester_quantity.columns = ['요청자', '합계 수량']
        requester_quantity = requester_quantity.sort_values(by='합계 수량', ascending=False)

        # Streamlit 내장 bar_chart 이용
        st.bar_chart(requester_quantity.head(10).set_index('요청자')['합계 수량'])

    # Streamlit 내장 divider 사용
    st.divider()

    st.header("아이템 별 :blue[생산 수량]")
    recent_logs = df.head(20).sort_values(by='datetime')

    # 데이터 피벗: 각 item_name을 컬럼으로 설정
    pivot_data = recent_logs[recent_logs['item_name'].isin(['Item1', 'Item2', 'Item3'])].pivot(index='datetime', columns='item_name', values='quantity').fillna(0)

    # 라인 차트 표시
    st.line_chart(pivot_data)

else:
    st.write("사용 가능한 데이터가 없습니다.")
