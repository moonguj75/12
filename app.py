import streamlit as st
import pandas as pd

st.set_page_config(page_title="부부 은퇴 자산 입체 계측기 v4.5", layout="wide")

st.title("📊 부부 은퇴 자산 입체 계측기 v4.5")
st.caption("6년차 대응 전술 완벽 수동 제어: 내 손으로 직접 정하는 TR ETF 전환 계획")
st.markdown("---")

# 1단계: 자산 설정 (사이드바 - 질문자님 요청으로 '초기' 문구 제거)
st.sidebar.header("⚙️ 자산 설정 (만원)")
husband_jesus_init = st.sidebar.number_input("👨 남편 주식 예수금", value=110000, step=1000) * 10000
husband_cma_init = st.sidebar.number_input("👨 남편 CMA 잔액", value=1350, step=50) * 10000
wife_deposit_init = st.sidebar.number_input("👩 아내 정기예금 총액", value=42000, step=500) * 10000
wife_cma_init = st.sidebar.number_input("👩 아내 CMA 잔액", value=1200, step=50) * 10000
deposit_unit = st.sidebar.number_input("🔓 매년 만기되는 통장 단위", value=8400, step=100) * 10000

st.header("📈 2단계: 장기 전략 및 시장 변수 설정")
c1, c2, c3, c4 = st.columns(4)

with c1:
    years_to_run = st.number_input("📊 몇 년 동안 시뮬레이션할까요?", value=10, min_value=1, max_value=30, step=1)
with c2:
    living_cost_annual = st.number_input("🛒 연간 총 생활비 (만원)", value=7740, step=10) * 10000
with c3:
    cma_rate = st.slider("대신증권 CMA 금리 (%)", 1.0, 6.0, 3.0, 0.1) / 100
with c4:
    deposit_rate = st.slider("저축은행 예금 금리 (%)", 1.0, 6.0, 4.0, 0.1) / 100

# --- [6년차 질문자님 직접 변경 전술 구역] ---
st.subheader("🛡️ 6년차 남편 자산 이동 전술 (질문자님 직접 제어)")
st.write("※ 6년차 아내 예금 고갈 시, 남편 예수금에서 얼마를 떼어 TR ETF로 보낼지 직접 설정하는 칸입니다.")
cx, cy, cz = st.columns(3)
with cx:
    # 6년차에 예수금 11.65억 중 얼마를 TR ETF로 넘길지 만원 단위로 직접 입력 (기본값은 예수금 전액인 116,500만원)
    tr_transfer_total_input = st.number_input("6년차에 TR ETF로 이동할 총 금액 (만원)", value=116500, step=1000) * 10000
with cy:
    # 1년 만에 다 채울지, 2년에 걸쳐 쪼갤지 선택
    tr_etf_transfer_years = st.selectbox("TR ETF로 쪼개 넣을 분할 기간 (년)", [1, 2], index=1)
with cz:
    tr_etf_return_rate = st.slider("TR ETF 예상 연 수익률 (%)", 1.0, 10.0, 5.0, 0.5) / 100

st.markdown("---")

if st.button("🚀 부부 입체 자산 주판 튕기기", type="primary"):
    # 변수 초기화
    h_jesus = husband_jesus_init
    h_cma = husband_cma_init
    h_tr_etf = 0  
    
    w_deposit = wife_deposit_init
    w_cma = wife_cma_init
    w_new_deposit = 0
    
    jesus_rate = 0.006
    tax_rate = 0.154
    monthly_living_cost = living_cost_annual / 12
    
    yearly_records = []
    monthly_records = []
    
    # 6년차 가동 시 매년 빠져나갈 TR 분할 투자금 계산기 세팅
    annual_tr_transfer = tr_transfer_total_input / tr_etf_transfer_years
    
    # 연차별 루프 시작
    for year in range(1, years_to_run + 1):
        # 2년차 진입 시 질문자님의 최적 안심 눈금 강제 세팅 발동 (5년차까지 유지)
        if 2 <= year <= 5:
            h_jesus = 1165000000
            h_cma = 70000000
            if year == 2:
                w_deposit = 365000000
                w_new_deposit = 80000000
                w_cma = 40000000

        # 6년차 이후: 질문자님이 세팅한 수동 공식에 맞춰 예수금 -> TR ETF 전환 실행
        if year >= 6:
            # 설정한 투자 기간 내에서만 예수금을 차감하여 ETF로 이동
            if year < 6 + tr_etf_transfer_years:
                if h_jesus >= annual_tr_transfer:
                    h_jesus -= annual_tr_transfer
                    h_tr_etf += annual_tr_transfer
                else:
                    h_tr_etf += h_jesus
                    h_jesus = 0

        # --- [연간 이자/수익 정산 (연초 반영)] ---
        h_interest_pre = (h_jesus * jesus_rate) + (h_cma * cma_rate)
        # TR ETF 수익 정산 (배당소득세에서 완벽 제외되므로 세전 소득 집계 안 됨)
        h_tr_etf = int(h_tr_etf * (1 + tr_etf_return_rate)) 
        
        if year <= 5:
            w_interest_pre = (w_deposit * deposit_rate) + (w_new_deposit * deposit_rate) + ((w_cma * cma_rate) / 2)
        else:
            w_interest_pre = 0  # 6년차 이후 아내 예금 자산은 0

        h_interest_post = int(h_interest_pre * (1 - tax_rate))
        w_interest_post = int(w_interest_pre * (1 - tax_rate))
        total_income_post = h_interest_post + w_interest_post
        
        # 이자 수입을 생활비 통장(5년차까진 아내CMA, 6년차부턴 남편CMA)에 선입금
        if year <= 5:
            w_cma += total_income_post
        else:
            h_cma += total_income_post

        # --- [월별 시뮬레이션 루프] ---
        for month in range(1, 13):
            if year <= 5:
                w_cma -= monthly_living_cost
            else:
                # 6년차부터는 아내 자산 대신 남편 CMA에서 실시간 생활비 조달!
                h_cma -= monthly_living_cost
            
            # 월별 잔고 기록
            monthly_records.append({
                "연차": f"{year}년차",
                "월": f"{month}월",
                "👨남편 예수금(만원)": int(h_jesus / 10000),
                "👨남편 CMA(만원)": int(h_cma / 10000),
                "👨남편 TR ETF(만원)": int(h_tr_etf / 10000),
                "👩아내 정기예금(만원)": int(max(0, (w_deposit + w_new_deposit)) / 10000) if year <= 5 else 0,
                "👩아내 CMA(만원)": int(max(0, w_cma) / 10000) if year <= 5 else 0,
                "👪부부 합산자산(만원)": int((h_jesus + h_cma + h_tr_etf + max(0, w_deposit + w_new_deposit) + max(0, w_cma)) / 10000)
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

        # 연간 데이터 보관
        yearly_records.append({
            "연차": f"{year}년차",
            "남편 세전소득": h_interest_pre,
            "아내 세전소득": w_interest_pre,
            "부부 총 세후이자": total_income_post,
            "생활비 부족분": deficit,
            "남편 총자산": h_jesus + h_cma + h_tr_etf,
            "아내 총자산": max(0, w_deposit + w_new_deposit + w_cma) if year <= 5 else 0
        })

    # --- [3단계: 최종 결과 출력] ---
    st.header("🏁 3단계: 맞춤형 자산 분배 결과 보고서")
    
    tab_yearly, tab_monthly = st.tabs(["📅 연차별 요약 및 건보료선", "📊 부부 각각 월별 주머니 잔고 현황"])
    
    with tab_yearly:
        for res in yearly_records:
            with st.expander(f"🔍 {res['연차']} 자산 운용 결과"):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("부부 합산 세후 이자", f"{int(res['부부 총 세후이자']/10000):,} 만원")
                    st.info(f"👨 남편 세전 소득: {int(res['남편 세전소득']/10000):,}만원" + (" ❌ 위험" if res['남편 세전소득'] >= 10000000 else " 🛡️ 안전"))
                with col_b:
                    st.warning(f"📉 생활비 부족분: {int(res['생활비 부족분']/10000):,} 만원")
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
