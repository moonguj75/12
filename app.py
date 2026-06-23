import streamlit as st

st.set_page_config(page_title="부부 은퇴 자산 시뮬레이터", layout="centered")

st.title("📊 부부 은퇴 자산 시뮬레이터 v2.5")
st.caption("질문자님 맞춤형 건보료 수비 및 연차별 자산 흐름 계측기")
st.markdown("---")

# 세션 상태 초기화 (계산 버튼 클릭 유무 확인용)
if "calculated" not in st.session_state:
    st.session_state.calculated = False

st.sidebar.header("⚙️ 1단계: 초기 자산 설정 (만원 단위)")
husband_jesus = st.sidebar.number_input("👨 남편 주식 예수금", value=110000, step=1000) * 10000
husband_cma = st.sidebar.number_input("👨 남편 CMA 잔액", value=1350, step=50) * 10000
wife_deposit = st.sidebar.number_input("👩 아내 정기예금 총액", value=42000, step=500) * 10000
wife_cma = st.sidebar.number_input("👩 아내 CMA 잔액", value=1200, step=50) * 10000
deposit_unit = st.sidebar.number_input("🔓 매년 만기되는 통장 단위", value=8400, step=100) * 10000

st.header("📈 2단계: 연차별 시장 변수 설정")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🗓️ 1년차 설정")
    living_cost_1 = st.number_input("1년차 연간 총 생활비 (만원)", value=7740, step=10) * 10000
    cma_rate_1 = st.slider("1년차 CMA 금리 (%)", 1.0, 6.0, 3.0, 0.1) / 100
    deposit_rate_1 = st.slider("1년차 예금 금리 (%)", 1.0, 6.0, 4.0, 0.1) / 100

with col2:
    st.subheader("🗓️ 2년차 설정")
    living_cost_2 = st.number_input("2년차 연간 총 생활비 (만원)", value=7740, step=10) * 10000
    cma_rate_2 = st.slider("2년차 CMA 금리 (%)", 1.0, 6.0, 3.0, 0.1) / 100
    deposit_rate_2 = st.slider("2년차 예금 금리 (%)", 1.0, 6.0, 4.0, 0.1) / 100

st.markdown("---")

if st.button("🚀 은퇴 자산 시뮬레이션 가동", type="primary"):
    st.session_state.calculated = True

if st.session_state.calculated:
    # 1년차 계산
    jesus_rate = 0.006
    h_total_pre_1 = (husband_jesus * jesus_rate) + (husband_cma * cma_rate_1)
    w_total_pre_1 = (wife_deposit * deposit_rate_1) + ((wife_cma * cma_rate_1) / 2)
    
    tax_rate = 0.154
    h_total_post_1 = int(h_total_pre_1 * (1 - tax_rate))
    w_total_post_1 = int(w_total_pre_1 * (1 - tax_rate))
    family_post_1 = h_total_post_1 + w_total_post_1
    deficit_1 = int(living_cost_1 - family_post_1)
    leftover_1 = deposit_unit - deficit_1
    
    # 2년차 계산 (질문자님 안심 리밸런싱 강제 적용)
    h_jesus_2 = 1165000000
    h_cma_2 = 70000000
    w_deposit_2 = 365000000
    w_new_deposit_2 = 80000000
    w_cma_2 = 40000000
    
    h_total_pre_2 = (h_jesus_2 * jesus_rate) + (h_cma_2 * cma_rate_2)
    w_total_pre_2 = (w_deposit_2 * deposit_rate_2) + (w_new_deposit_2 * deposit_rate_2) + ((w_cma_2 * cma_rate_2) / 2)
    
    h_total_post_2 = int(h_total_pre_2 * (1 - tax_rate))
    w_total_post_2 = int(w_total_pre_2 * (1 - tax_rate))
    family_post_2 = h_total_post_2 + w_total_post_2
    deficit_2 = int(living_cost_2 - family_post_2)
    leftover_2 = deposit_unit - deficit_2

    # 결과 화면 출력
    tab1, tab2 = st.tabs(["📋 1년차 결과 보고서", "📋 2년차 결과 보고서"])
    
    with tab1:
        st.subheader("1년차 결산")
        st.metric("부부 총 세후 이자 수입", f"{int(family_fit:=family_post_1/10000):,} 만원")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"👨 남편 세전 금융소득: {int(h_total_pre_1/10000):,} 만원" + (" ❌ (위험)" if h_total_pre_1 >= 10000000 else " 🛡️ (안전)"))
        with c2:
            st.info(f"👩 아내 세전 금융소득: {int(w_total_pre_1/10000):,} 만원" + (" ❌ (위험)" if w_total_pre_1 >= 20000000 else " 🛡️ (안전)"))
            
        st.warning(f"🛒 생활비 진짜 부족분: {int(deficit_1/10000):,} 만원")
        st.success(f"💰 부족분 메우고 남은 알짜 잔돈: {int(leftover_1/10000):,} 만원")

    with tab2:
        st.subheader("2년차 결산 (안심 눈금 재배치 반영)")
        st.metric("부부 총 세후 이자 수입", f"{int(family_post_2/10000):,} 만원")
        
        c3, c4 = st.columns(2)
        with c3:
            st.info(f"👨 남편 세전 금융소득: {int(h_total_pre_2/10000):,} 만원" + (" ❌ (위험)" if h_total_pre_2 >= 10000000 else " 🛡️ (안전)"))
        with c4:
            st.info(f"👩 아내 세전 금융소득: {int(w_total_pre_2/10000):,} 만원" + (" ❌ (위험)" if w_total_pre_2 >= 20000000 else " 🛡️ (안전)"))
            
        st.warning(f"🛒 생활비 진짜 부족분: {int(deficit_2/10000):,} 만원")
        st.success(f"💰 부족분 메우고 남은 알짜 잔돈: {int(leftover_2/10000):,} 만원")
