import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Streamlit 페이지 설정
st.set_page_config(
    page_title="NxtCloud 공장 관리자 대시보드", page_icon="🏭", layout="wide"
)

# 데이터베이스 연결 정보
DB_HOST = "데이터베이스 호스트"
DB_USER = "데이터베이스 유저"
DB_PASSWORD = "데이터베이스 암호"
DB_NAME = "데이터베이스 이름"


# 데이터베이스 연결 함수
def connect_to_database():
    return mysql.connector.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME
    )


# 데이터 가져오기 함수
def fetch_data(conn, query):
    return pd.read_sql(query, conn)


# Streamlit 앱 시작
st.title("🏭 :blue[NxtCloud 공장 관리자 대시보드]")

# 데이터베이스 연결
try:
    conn = connect_to_database()
    st.success("✅ 데이터베이스에 성공적으로 연결되었습니다.")
except mysql.connector.Error as e:
    st.error(f"❌ 데이터베이스 연결 오류: {e}")
    st.stop()

# 날짜 범위 선택
st.header("📅 :blue[날짜] 범위 선택")
st.divider()

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("시작 날짜", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("종료 날짜", datetime.now())

# 쿼리 실행
query = f"""
SELECT * FROM logs
WHERE DATE(datetime) BETWEEN '{start_date}' AND '{end_date}'
ORDER BY datetime
"""
df = fetch_data(conn, query)

# 데이터 없을 경우 처리
if df.empty:
    st.warning("⚠️ 선택한 날짜 범위에 데이터가 없습니다.")
    st.stop()

# 기본 통계 표시
st.header("📊 기본 :blue[통계]", divider="rainbow")
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.metric(label="📝 총 로그 수", value=len(df))
with col2:
    st.metric(label="📦 총 생산량", value=df["quantity"].sum())

# 요청자별 생산량
st.header("👥 요청자별 :blue[생산량]", divider="rainbow")

fig_requester = px.bar(
    df.groupby("requester")["quantity"].sum().reset_index(),
    x="requester",
    y="quantity",
    title="요청자별 총 생산량",
)
st.plotly_chart(fig_requester)

# 공장별 생산량 차트
st.header("🏭 공장별 :blue[생산량]", divider="rainbow")
st.divider()

fig_factory = px.bar(
    df.groupby("factory_name")["quantity"].sum().reset_index(),
    x="factory_name",
    y="quantity",
    title="공장별 총 생산량",
)
st.plotly_chart(fig_factory)

# 상품별 생산량 차트
st.header("🛍️상품별 :blue[ 생산량]", divider="rainbow")

fig_item = px.pie(
    df.groupby("item_name")["quantity"].sum().reset_index(),
    names="item_name",
    values="quantity",
    title="상품별 생산량 비율",
)
st.plotly_chart(fig_item)

# 시간에 따른 생산량 추이
st.header("📈 시간에 따른 :blue[생산량 추이]", divider="rainbow")

df["date"] = pd.to_datetime(df["datetime"]).dt.date
daily_production = df.groupby("date")["quantity"].sum().reset_index()
fig_trend = px.line(daily_production, x="date", y="quantity", title="일별 생산량 추이")
st.plotly_chart(fig_trend)


# 원본 데이터 표시
st.header("📋 :blue[원본 데이터]", divider="rainbow")

st.dataframe(df)

# 데이터베이스 연결 종료
conn.close()
