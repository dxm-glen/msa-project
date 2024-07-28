import streamlit as st
import requests

# 실제 Lambda 함수 URL로 교체하세요
# 끝에 '/' 제거
LAMBDA_URL = "https://your-lambda-function-url.amazonaws.com"

st.set_page_config(page_title="이커머스 재고 관리 시스템", page_icon="🛍️", layout="wide")


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


def purchase_item(item_name, quantity, requester):
    if not LAMBDA_URL or LAMBDA_URL == "https://your-lambda-function-url.amazonaws.com":
        return {
            "message": "Lambda 함수 URL이 설정되지 않았습니다. LAMBDA_URL을 확인해주세요."
        }

    data = {"item_name": item_name, "quantity": quantity, "requester": requester}
    try:
        response = requests.post(f"{LAMBDA_URL}/item", json=data, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


st.title("🛍️ 이커머스 재고 관리 시스템")
st.sidebar.success("위에서 페이지를 선택하세요.")
st.markdown(
    """
    이 시스템에서는 상품을 구매하고 재고를 관리할 수 있습니다.
    
    아래에서 상품을 구매하거나, **👈 사이드바**에서 관리자 페이지로 이동할 수 있습니다.
    """
)
st.divider()
st.header("상품 구매", divider="rainbow")

items = get_items()
if not items:
    st.info("현재 구매 가능한 상품이 없습니다.")
else:
    # 상품 목록을 3열로 표시
    cols = st.columns(3)
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            st.subheader(item["name"], divider="blue")
            st.write(f"재고: {item['quantity']}개")
            st.write(f"공장 ID: {item['factory_id']}")
            st.divider()

            quantity = st.slider(
                f"{item['name']} 구매 수량",
                min_value=1,
                max_value=5,
                value=1,
                step=1,
                key=f"buy_{idx}",
            )
            requester = st.text_input(
                f"{item['name']} 구매자 이름 *", key=f"requester_{idx}"
            )

            is_disabled = not requester  # 구매자 이름이 비어있으면 버튼 비활성화

            if is_disabled:
                st.info("구매자 이름을 입력해야 구매할 수 있습니다.")

            if st.button(
                f"{item['name']} 구매하기",
                key=f"buy_button_{idx}",
                disabled=is_disabled,
                type="primary",
            ):
                if not requester:
                    st.error("구매자 이름을 입력해주세요.")
                else:
                    result = purchase_item(item["name"], quantity, requester)
                    if "error" in result:
                        st.error(f"구매 처리 중 오류가 발생했습니다: {result['error']}")
                    elif "message" in result:
                        if "구매 실패" in result["message"]:
                            st.warning(result["message"])
                        else:
                            st.success(result["message"])
                    else:
                        st.error(f"예상치 못한 응답: {result}")

            st.markdown("---")
