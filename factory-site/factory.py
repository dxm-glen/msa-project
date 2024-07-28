# pip install streamlit plotly mysql-connector-python

import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# 데이터베이스 연결 정보
DB_CONFIG = {
    "host": "DB_HOST",
    "user": "DB_USER",
    "password": "DB_PW",
    "database": "DB_NAME",
}


# 데이터베이스 연결 함수
def connect_to_database():
    return mysql.connector.connect(**DB_CONFIG)


# 데이터 가져오기 함수
def fetch_data(query, params=None):
    conn = connect_to_database()
    try:
        with conn.cursor(dictionary=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
        return pd.DataFrame(result)
    finally:
        conn.close()


# 로그 삭제 함수
def delete_logs(condition=None, params=None):
    conn = connect_to_database()
    try:
        with conn.cursor() as cursor:
            if condition:
                query = f"DELETE FROM logs WHERE {condition}"
                cursor.execute(query, params)
            else:
                cursor.execute("DELETE FROM logs")
        conn.commit()
    finally:
        conn.close()


# 메인 대시보드 함수
def show_dashboard():
    st.title("🏭 :blue[NxtCloud 공장 관리자 대시보드]")

    # 데이터 가져오기
    query = """
    SELECT * FROM logs 
    ORDER BY datetime
    """
    df = fetch_data(query)

    if df.empty:
        st.warning("데이터가 없습니다.")
        return

    # 성공한 항목만 필터링
    df_success = df[df["status"] == "성공"]
    df_failed = df[df["status"] == "실패"]

    # 이전 기간 데이터 가져오기 (delta 계산을 위해)
    current_period = df["datetime"].max() - df["datetime"].min()
    previous_period_start = df["datetime"].min() - current_period
    query_previous = f"""
    SELECT * FROM logs 
    WHERE datetime BETWEEN '{previous_period_start}' AND '{df['datetime'].min()}'
    """
    df_previous = fetch_data(query_previous)
    df_previous_success = df_previous[df_previous["status"] == "성공"]

    # 기본 통계
    st.header("📊 :blue[기본 통계]", divider="rainbow")

    col1, col2, col3, col4 = st.columns(4)

    # 총 로그 수
    total_logs = len(df)
    total_logs_prev = len(df_previous)
    delta_logs = int(total_logs - total_logs_prev)
    col1.metric("총 로그 수", total_logs, delta=delta_logs, delta_color="normal")

    # 총 요청자 수
    total_requesters = df["requester"].nunique()
    total_requesters_prev = df_previous["requester"].nunique()
    delta_requesters = int(total_requesters - total_requesters_prev)
    col2.metric(
        "총 요청자 수", total_requesters, delta=delta_requesters, delta_color="normal"
    )

    # 총 생산량 (성공한 항목만)
    total_production = int(df_success["quantity"].sum())
    total_production_prev = int(df_previous_success["quantity"].sum())
    delta_production = int(total_production - total_production_prev)
    col3.metric(
        "총 생산량 (성공)",
        total_production,
        delta=delta_production,
        delta_color="normal",
    )

    # 생산 취소 건수
    total_failed = len(df_failed)
    total_failed_prev = len(df_previous[df_previous["status"] == "실패"])
    delta_failed = int(total_failed - total_failed_prev)
    col4.metric(
        "생산 취소 건수", total_failed, delta=delta_failed, delta_color="inverse"
    )

    # 상품별 생산량 (성공한 항목만)
    st.subheader("🛍️ :blue[상품별 생산량 정보]", divider="rainbow")
    current_production = df_success.groupby("item_name")["quantity"].sum()
    previous_production = df_previous_success.groupby("item_name")["quantity"].sum()

    for i in range(0, len(current_production), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(current_production):
                item = current_production.index[i + j]
                current_qty = int(current_production[item])
                previous_qty = (
                    int(previous_production[item]) if item in previous_production else 0
                )
                delta_qty = int(current_qty - previous_qty)
                cols[j].metric(
                    f"{item} 생산량", current_qty, delta=delta_qty, delta_color="normal"
                )

    # 시간에 따른 제품별 생산량 추이 (성공한 항목만)
    st.header("📈 :blue[시간에 따른 제품별 생산량 추이]", divider="rainbow")
    df_success["datetime"] = pd.to_datetime(df_success["datetime"])

    # 리샘플링 방식 수정
    df_resampled = (
        df_success.set_index("datetime")
        .groupby("item_name")
        .resample("1min")
        .agg({"quantity": "sum"})
        .reset_index()
    )

    if df_resampled.empty:
        st.warning("성공한 생산 데이터가 없습니다.")
    else:
        fig = px.line(
            df_resampled,
            x="datetime",
            y="quantity",
            color="item_name",
            title="분 단위 제품별 생산량 추이 (성공)",
        )
        fig.update_xaxes(title="시간")
        fig.update_yaxes(title="생산량")
        st.plotly_chart(fig)

    # 요청자별 생산량 (성공한 항목만)
    st.header("👥 :blue[요청자별 생산량]", divider="rainbow")
    requester_production = (
        df_success.groupby("requester")["quantity"].sum().sort_values(ascending=False)
    )

    if requester_production.empty:
        st.warning("성공한 생산 데이터가 없습니다.")

    else:
        # 그래프 유형 선택
        graph_type = st.radio("그래프 유형 선택", ["원형 차트", "막대 그래프"])

        if graph_type == "원형 차트":
            fig = px.pie(
                values=requester_production.values,
                names=requester_production.index,
                title="요청자별 수량 비율 (성공)",
            )
            st.plotly_chart(fig)
        else:  # 막대 그래프
            fig = px.bar(
                x=requester_production.index,
                y=requester_production.values,
                title="요청자별 수량 (성공)",
                labels={"x": "요청자", "y": "요청 수량"},
                color=requester_production.index,
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig)

    # 원본 데이터 표시
    st.header("📋 :blue[원본 데이터]", divider="rainbow")
    st.dataframe(df)


# 관리자 페이지 함수
def show_admin_page():
    st.title("👨‍💼 :blue[관리자 페이지]")

    # 전체 로그 삭제
    if st.button("모든 로그 삭제"):
        delete_logs()
        st.success("모든 로그가 삭제되었습니다.")

    st.header("🔍 :blue[로그 필터링 및 삭제]", divider="rainbow")

    # 로그 데이터 가져오기
    logs = fetch_data("SELECT * FROM logs ORDER BY datetime DESC")

    if logs.empty:
        st.warning("로그 데이터가 없습니다.")
        return

    # 컬럼 이름 확인 및 필터링 옵션 설정
    columns = logs.columns.tolist()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        item_name_col = (
            "item_name"
            if "item_name" in columns
            else "name" if "name" in columns else None
        )
        if item_name_col:
            item_filter = st.multiselect("상품명", options=logs[item_name_col].unique())
        else:
            st.warning("상품명 컬럼을 찾을 수 없습니다.")
            item_filter = []

    with col2:
        if "status" in columns:
            status_filter = st.multiselect("상태", options=logs["status"].unique())
        else:
            st.warning("상태 컬럼을 찾을 수 없습니다.")
            status_filter = []

    with col3:
        if "requester" in columns:
            requester_filter = st.multiselect(
                "요청자", options=logs["requester"].unique()
            )
        else:
            st.warning("요청자 컬럼을 찾을 수 없습니다.")
            requester_filter = []

    with col4:
        if "factory_id" in columns:
            factory_filter = st.multiselect(
                "공장 ID", options=logs["factory_id"].unique()
            )
        else:
            st.warning("공장 ID 컬럼을 찾을 수 없습니다.")
            factory_filter = []

    # 필터 적용
    filtered_logs = logs.copy()
    if item_filter and item_name_col:
        filtered_logs = filtered_logs[filtered_logs[item_name_col].isin(item_filter)]
    if status_filter:
        filtered_logs = filtered_logs[filtered_logs["status"].isin(status_filter)]
    if requester_filter:
        filtered_logs = filtered_logs[filtered_logs["requester"].isin(requester_filter)]
    if factory_filter:
        filtered_logs = filtered_logs[filtered_logs["factory_id"].isin(factory_filter)]

    # 필터링된 로그 표시
    st.subheader("필터링된 로그", divider="rainbow")
    st.dataframe(filtered_logs)

    # 선택된 로그 삭제
    if st.button("선택된 로그 삭제"):
        if not filtered_logs.empty:
            condition = "log_id IN (%s)" % ",".join(["%s"] * len(filtered_logs))
            delete_logs(condition, tuple(filtered_logs["log_id"]))
            st.success(f"{len(filtered_logs)}개의 로그가 삭제되었습니다.")
        else:
            st.warning("삭제할 로그가 없습니다.")


# 메인 앱
def main():
    st.set_page_config(
        page_title="NxtCloud 공장 관리 시스템", page_icon="🏭", layout="wide"
    )

    # 사이드바에 페이지 선택 옵션 추가
    page = st.sidebar.radio("페이지 선택", ["대시보드", "관리자 페이지"])

    if page == "대시보드":
        show_dashboard()
    elif page == "관리자 페이지":
        admin_password = st.sidebar.text_input("관리자 번호", type="password")
        if admin_password == "4808":
            show_admin_page()
        else:
            st.error("관리자 번호가 올바르지 않습니다.")


if __name__ == "__main__":
    main()
