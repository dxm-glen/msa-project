import streamlit as st
import requests

# 실제 Lambda 함수 URL로 교체하세요
# 주소 끝에 '/'제거
LAMBDA_URL = "https://your-lambda-function-url.amazonaws.com"


def get_items():
    if not LAMBDA_URL or LAMBDA_URL == "https://your-lambda-function-url.amazonaws.com":
        st.error("Lambda 함수 URL이 설정되지 않았습니다. LAMBDA_URL을 확인해주세요.")
        return []

    try:
        response = requests.get(f"{LAMBDA_URL}/item", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"상품 정보를 가져오는데 실패했습니다: {str(e)}")
        return []


def update_item_quantity(item_id, quantity):
    if not LAMBDA_URL or LAMBDA_URL == "https://your-lambda-function-url.amazonaws.com":
        return {
            "message": "Lambda 함수 URL이 설정되지 않았습니다. LAMBDA_URL을 확인해주세요."
        }

    data = {"quantity": quantity}
    try:
        response = requests.put(f"{LAMBDA_URL}/item/{item_id}", json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"message": f"수량 업데이트 중 오류가 발생했습니다: {str(e)}"}


st.set_page_config(page_title="관리자 페이지", page_icon="👨‍💼", layout="wide")

st.title("👨‍💼 관리자 페이지")
items = get_items()

if not items:
    st.info("관리할 상품이 없습니다.")
else:
    st.subheader("상품 수량 관리")
    for item in items:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{item['name']}** (현재 재고: {item['quantity']}개)")
        with col2:
            new_quantity = st.number_input(
                f"{item['name']} 새 수량",
                min_value=0,
                value=item["quantity"],
                key=f"admin_{item['item_id']}",
            )
        with col3:
            if st.button(f"{item['name']} 업데이트", key=f"update_{item['item_id']}"):
                result = update_item_quantity(item["item_id"], new_quantity)
                st.write(result["message"])
        st.markdown("---")
