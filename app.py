import streamlit as st
import pandas as pd

st.set_page_config(page_title="부부 은퇴 자산 입체 계측기", layout="wide")

st.title("📊 부부 은퇴 자산 입체 계측기 v3.5")
st.caption("예수금·CMA·예금 주머니의 연차별/월별 잔고 흐름 정밀 추적 시스템")
st.markdown("---")

# 1단계: 초기 자산 설정 (사이드바)
st.sidebar.header("⚙️ 1단계: 초기 자산 설정 (만원)")
husband_jesus_init = st.sidebar.number_input("👨 남편 주식 예수금", value=110000, step=1000) * 10000
husband_cma_init = st.sidebar.number_input("👨 남편 CMA 잔액", value=1350, step=50) * 10000
wife_deposit_init = st.sidebar.number_input("👩 아내 정기예금 총액", value=42000, step=500) * 10000
wife_cma_init = st.sidebar.number_input("👩 아내 CMA 잔액", value=1200, step=50) * 10000
deposit_unit = st.sidebar.number_input("🔓 매년 만기되는 통장 단위", value=8400, step=100) * 10000

st.header("📈 2단계: 시뮬레이션 환경 설정")
c1, c2, c3, c4 = st.columns(4)

with c1:
    years_to_run = st.number_input("📊 몇 년 동안 시뮬레이션할까요?", value=5, min_value=1, max_value=30, step=1)
with c2:
    living_cost_annual = st.number_input("🛒 연간 총 생활비 (만원)", value=7740, step=10) * 10000
with c3:
    cma_rate = st.slider("대신증권 CMA 금리 (%)", 1.0, 6.0, 3.0, 0.1) / 100
with c4:
    deposit_rate = st.slider("저축은행 예금 금리 (%)", 1.0, 6.0, 4.0, 0.1) / 100

st.markdown("---")

if st.button("🚀 부부 입체 자산 주판 튕기기", type="primary"):
    # 변수 복사 및 초기화
    h_jesus = husband_jesus_init
    h_cma = husband_cma_init
    w_deposit = wife_deposit_init
    w_cma = wife_cma_init
    w_new_deposit = 0
    
    jesus_rate = 0.006
    tax_rate = 0.154
    monthly_living_cost = living_cost_annual / 12
    
    yearly_records = []
    monthly_records = []
    
    # 연차별 루프 시작
    for year in range(1, years_to_run + 1):
        # 2년차 진입 시 질문자님의 최적 안심 눈금 강제 세팅 발동
        if year >= 2:
            h_jesus = 1165000000
            h_cma = 70000000
            if year == 2:
                w_deposit = 365000000
                w_new_deposit = 80000000
                w_cma = 40000000

        # --- [연간 이자 정산 (연초에 선반영 및 검증)] ---
        h_interest_pre = (h_jesus * jesus_rate) + (h_cma * cma_rate)
        w_interest_pre = (w_deposit * deposit_rate) + (w_new_deposit * deposit_rate) + ((w_cma * cma_rate) / 2)
        
        h_interest_post = int(h_interest_pre * (1 - tax_rate))
        w_interest_post = int(w_interest_pre * (1 - tax_rate))
        total_income_post = h_interest_post + w_interest_post
        
        # 연초에 이자 수입을 아내 CMA 지갑에 먼저 입금 (생활비 방어용)
        w_cma += total_income_post
        
        # --- [월별 시뮬레이션 루프] ---
        # 아내 CMA에서 매달 월 생활비가 차감되는 흐름 추적
        for month in range(1, 13):
            w_cma -= monthly_living_cost
            
            # 월별 데이터 저장
            monthly_records.append({
                "연차": f"{year}년차",
                "월": f"{month}월",
                "👨남편 예수금(만원)": int(h_jesus / 10000),
                "👨남편 CMA(만원)": int(h_cma / 10000),
                "👩아내 정기예금(만원)": int((w_deposit + w_new_deposit) / 10000),
                "👩아내 CMA(만원)": int(w_cma / 10000),
                "👪부부 합산 자산(만원)": int((h_jesus + h_cma + w_deposit + w_new_deposit + w_cma) / 10000)
            })
            
        # --- [연말 부족분 원금 청산 및 누적 정산] ---
        # 연초에 넣은 이자+매달 뺀 생활비 결과로 쪼그라든 아내 CMA를 만기 예금으로 메우기
        deficit = int(living_cost_annual - total_income_post)
        leftover = deposit_unit - deficit
        
        # 실제 장부 기록 보관
        yearly_records.append({
            "연차": f"{year}년차",
            "남편 세전소득": h_interest_pre,
            "아내 세전소득": w_interest_pre,
            "부부 총 세후이자": total_income_post,
            "생활비 부족분": deficit,
            "만기 후 남은 알짜잔돈": leftover,
            "남편 총자산": h_jesus + h_cma,
            "아내 총자산": w_deposit + w_new_deposit + w_cma
        })
        
        # 내년차를 위한 원금 정산 및 리밸런싱 연속성 유지
        w_deposit -= deposit_unit
        w_cma += leftover  # 부족분 채우고 남은 진짜 잔돈을 아내 CMA에 최종 합산

    # --- [3단계: 최종 결과 입체 화면 출력] ---
    st.header("🏁 3단계: 부부 자산 현황 및 분배 리포트")
    
    # 탭으로 화면 분할 (연차별 요약 vs 월별 주머니 잔고)
    tab_yearly, tab_monthly = st.tabs(["📅 연차별 요약 및 건보료선", "📊 부부 각각 월별 주머니 잔고 현황"])
    
    with tab_yearly:
        st.subheader("📋 연차별 자산 흐름 및 마지노선 검증")
        for res in yearly_records:
            with st.expander(f"🔍 {res['연차']} 세부 자산 분배 결과 (클릭하여 열기)"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("부부 합산 세후 이자", f"{int(res['부부 총 세후이자']/10000):,} 만원")
                    st.info(f"👨 남편 세전 소득: {int(res['남편 세전소득']/10000):,}만원" + (" ❌ 위험" if res['남편 세전소득'] >= 10000000 else " 🛡️ 안전"))
                with col_b:
                    st.warning(f"📉 연간 생활비 부족분: {int(res['생활비 부족분']/10000):,} 만원")
                    st.info(f"👩 아내 세전 소득: {int(res['아내 세전소득']/10000):,}만원" + (" ❌ 위험" if res['아내 세전소득'] >= 20000000 else " 🛡️ 안전"))
                with col_c:
                    st.success(f"💰 예금 정산 후 남은 잔돈: {int(res['만기 후 남은 알짜잔돈']/10000):,} 만원")
                    st.metric("👨 남편 총 자산", f"{int(res['남편 총자산']/10000):,} 만원")
                    st.metric("👩 아내 총 자산", f"{int(res['아내 총자산']/10000):,} 만원")

    with tab_monthly:
        st.subheader("🗓️ 부부 각각의 월별 자산 주머니 변동 현황")
        st.write("※ 매달 생활비(연 생활비 ÷ 12)가 차감되면서 실시간으로 변하는 부부의 주머니별 잔액 표입니다.")
        
        # 데이터프레임 변환 후 테이블 출력
        df_monthly = pd.DataFrame(monthly_records)
        st.dataframe(df_monthly, use_container_width=True, height=500)
        
        # 간단한 자산 감소 추세선 그래프 추가
        st.subheader("📉 부부 합산 총자산 감소 추이")
        st.line_chart(df_monthly.set_index(["연차", "월"])["♻️부부 합산 자산(만원)" if "♻️부부 합산 자산(만원)" in df_monthly.columns else "👪부부 합산 자산(만원)"])
