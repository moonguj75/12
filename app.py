import streamlit as st
import pandas as pd

st.set_page_config(page_title="부부 은퇴 자산 입체 계측기 v5.0", layout="wide")

st.title("📊 부부 은퇴 자산 입체 계측기 v5.0")
st.caption("퇴직 1~2년차 남편 11억 지수 TR ETF 선제 이동 및 유동자금 고금리 수비 시스템")
st.markdown("---")

# 1단계: 자산 설정 (사이드바)
st.sidebar.header("⚙️ 자산 설정 (만원)")
husband_total_init = st.sidebar.number_input("👨 남편 퇴직 초기 총 자산 (예수금+CMA)", value=123500, step=1000) * 10000
wife_deposit_init = st.sidebar.number_input("👩 아내 정기예금 총액", value=42000, step=500) * 10000
wife_cma_init = st.sidebar.number_input("👩 아내 CMA 잔액", value=1200, step=50) * 10000
deposit_unit = st.sidebar.number_input("🔓 매년 만기되는 통장 단위", value=8400, step=100) * 10000

st.header("📈 2단계: 1~2년차 남편 11억 지수 TR ETF 이동 및 유동자금 배치")
c_etf, c_move = st.columns(2)

with c_etf:
    tr_transfer_annual = st.selectbox("남편 자산 중 11억 원을 TR ETF로 어떻게 이동할까요?", 
                                      ["1년차에 11억 전액 이동", "1~2년차에 걸쳐 매년 5.5억씩 이동"], index=1)
    tr_etf_rate = st.slider("지수 TR ETF 예상 연 수익률 (%)", 1.0, 10.0, 5.0, 0.5) / 100

with c_move:
    # 11억 원을 제외하고 남은 남편 유동자금을 어디에 예치할지 질문자님이 직접 선택
    husband_liquidity_target = st.radio("11억 제외 남편 유동자금을 어디에 넣어 이자를 극대화할까요?", 
                                         ["금리 높은 정기저축(예금) 주머니로 이동 (4.0%대)", "대신증권 CMA 주머니에 유지 (3.0%대)"])

st.subheader("🗓️ 3단계: 장기 전략 및 시장 변수 설정")
c1, c2, c3 = st.columns(3)
with c1:
    years_to_run = st.number_input("📊 몇 년 동안 시뮬레이션할까요?", value=10, min_value=1, max_value=30, step=1)
with c2:
    living_cost_annual = st.number_input("🛒 연간 총 생활비 (만원)", value=7740, step=10) * 10000
with c3:
    deposit_rate = st.slider("저축은행 정기저축/예금 금리 (%)", 1.0, 6.0, 4.0, 0.1) / 100
    cma_rate = st.slider("대신증권 CMA 금리 (%)", 1.0, 6.0, 3.0, 0.1) / 100

st.markdown("---")

if st.button("🚀 부부 최적화 자산 주판 튕기기", type="primary"):
    # 자산 초기 셋팅
    h_total = husband_total_init
    h_tr_etf = 0
    h_jesus = 0
    h_cma = 0
    h_deposit = 0
    
    w_deposit = wife_deposit_init
    w_cma = wife_cma_init
    w_new_deposit = 0
    
    jesus_rate = 0.006
    tax_rate = 0.154
    monthly_living_cost = living_cost_annual / 12
    
    yearly_records = []
    monthly_records = []
    
    # 1년차 시작 전, 11억을 뺀 남편 유동자금 기본 스케일 산출 (1억 3,500만 원)
    husband_liquidity_base = h_total - 1100000000 
    
    # 연차별 루프
    for year in range(1, years_to_run + 1):
        
        # --- [1~2년차 남편 11억 지수 TR ETF 선제 이동 전술 반영] ---
        if tr_transfer_annual == "1년차에 11억 전액 이동":
            if year == 1:
                h_tr_etf = 1100000000
                h_jesus = 0  # 11억 원이 예수금에서 완전히 빠져나감
            # 유동자금은 질문자님 선택에 따라 고금리 이동
            if husband_liquidity_target == "금리 높은 정기저축(예금) 주머니로 이동 (4.0%대)":
                h_deposit = husband_liquidity_base
                h_cma = 0
            else:
                h_cma = husband_liquidity_base
                h_deposit = 0
        else:
            # 1~2년차 반반 이동 전술
            if year == 1:
                h_tr_etf = 550000000
                h_jesus = 550000000  # 남은 반은 아직 예수금 창고에 대기
                if husband_liquidity_target == "금리 높은 정기저축(예금) 주머니로 이동 (4.0%대)":
                    h_deposit = husband_liquidity_base
                    h_cma = 0
                else:
                    h_cma = husband_liquidity_base
                    h_deposit = 0
            elif year == 2:
                h_tr_etf += 550000000
                h_jesus = 0  # 2년차에 대기 자금까지 TR ETF로 완벽 이동 끝
                
        # 2년차부터 5년차까지 아내 자산 눈금 조정 규칙 적용
        if 2 <= year <= 5:
            if year == 2:
                w_deposit = 365000000
                w_new_deposit = 80000000
                w_cma = 40000000

        # --- [연간 이자/수익 정산] ---
        # 남편 세전 금융소득 (TR ETF 수익은 세전소득 집계에서 원천 제외되어 건보료 철벽 수비!)
        h_interest_pre = (h_jesus * jesus_rate) + (h_cma * cma_rate) + (h_deposit * deposit_rate)
        h_tr_etf = int(h_tr_etf * (1 + tr_etf_rate))  # TR ETF는 내부적으로 복리 성장
        
        # 아내 세전 금융소득
        if year <= 5:
            w_interest_pre = (w_deposit * deposit_rate) + (w_new_deposit * deposit_rate) + ((w_cma * cma_rate) / 2)
        else:
            w_interest_pre = 0

        h_interest_post = int(h_interest_pre * (1 - tax_rate))
        w_interest_post = int(w_interest_pre * (1 - tax_rate))
        total_income_post = h_interest_post + w_interest_post
        
        # 이자 소득을 생활비 통장에 선입금
        if year <= 5:
            w_cma += total_income_post
        else:
            if husband_liquidity_target == "금리 높은 정기저축(예금) 주머니로 이동 (4.0%대)":
                h_deposit += total_income_post
            else:
                h_cma += total_income_post

        # --- [월별 시뮬레이션 루프] ---
        for month in range(1, 13):
            if year <= 5:
                w_cma -= monthly_living_cost
            else:
                # 6년차부터 아내 예금 고갈 시 남편의 고금리 유동자금 주머니에서 생활비 조달!
                if husband_liquidity_target == "금리 높은 정기저축(예금) 주머니로 이동 (4.0%대)":
                    h_deposit -= monthly_living_cost
                else:
                    h_cma -= monthly_living_cost
            
            # 월별 잔고 보관
            monthly_records.append({
                "연차": f"{year}년차",
                "월": f"{month}월",
                "👨남편 대기예수금(만원)": int(h_jesus / 10000),
                "👨남편 고금리유동성(만원)": int((h_cma + h_deposit) / 10000),
                "👨남편 지수 TR ETF(만원)": int(h_tr_etf / 10000),
                "👩아내 정기예금(만원)": int(max(0, (w_deposit + w_new_deposit)) / 10000) if year <= 5 else 0,
                "👩아내 CMA(만원)": int(max(0, w_cma) / 10000) if year <= 5 else 0,
                "👪부부 합산자산(만원)": int((h_jesus + h_cma + h_deposit + h_tr_etf + max(0, w_deposit + w_new_deposit) + max(0, w_cma)) / 10000)
            })
            
        # --- [연말 부족분 원금 청산 및 누적 정산] ---
        if year <= 5:
            deficit = int(living_cost_annual - total_income_post)
            leftover = deposit_unit - deficit
            w_deposit -= deposit_unit
            w_cma += leftover
        else:
            deficit = int(living_cost_annual - total_income_post)
            leftover = 0 

        yearly_records.append({
            "연차": f"{year}년차",
            "남편 세전소득": h_interest_pre,
            "아내 세전소득": w_interest_pre,
            "부부 총 세후이자": total_income_post,
            "생활비 부족분": deficit,
            "남편 총자산": h_jesus + h_cma + h_deposit + h_tr_etf,
            "아내 총자산": max(0, w_deposit + w_new_deposit + w_cma) if year <= 5 else 0
        })

    # --- [최종 화면 보고서 출력] ---
    st.header("🏁 4단계: 질문자님 최적화 자산 흐름 성적표")
    
    tab_yearly, tab_monthly = st.tabs(["📅 연차별 요약 및 건보료선 검증", "📊 부부 각각 월별 주머니 잔고 현황"])
    
    with tab_yearly:
        for res in yearly_records:
            with st.expander(f"🔍 {res['연차']} 자산 운용 결과"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("부부 합산 세후 이자", f"{int(res['부부 총 세후이자']/10000):,} 만원")
                    st.info(f"👨 남편 세전 소득: {int(res['남편 세전소득']/10000):,}만원" + (" ❌ 위험" if res['남편 세전소득'] >= 10000000 else " 🛡️ 안전"))
                with col_b:
                    st.warning(f"📉 연간 생활비 부족분: {int(res['생활비 부족분']/10000):,} 만원")
                    st.info(f"👩 아내 세전 소득: {int(res['아내 세전소득']/10000):,}만원" + (" ❌ 위험" if res['아내 세전소득'] >= 20000000 else " 🛡️ 안전"))
                with col_c:
                    st.metric("👨 남편 자산 총합", f"{int(res['남편 총자산']/10000):,} 만원")
                    st.metric("👩 아내 자산 총합", f"{int(res['아내 총자산']/10000):,} 만원")

    with tab_monthly:
        st.subheader("🗓️ 부부 각각의 월별 자산 주머니 변동 현황")
        df_monthly = pd.DataFrame(monthly_records)
        st.dataframe(df_monthly, use_container_width=True, height=500)
        
        st.subheader("📉 부부 합산 총자산 변화 추이")
        st.line_chart(df_monthly.set_index(["연차", "월"])["👪부부 합산자산(만원)"])
