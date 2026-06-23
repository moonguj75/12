import streamlit as st
import pandas as pd

st.set_page_config(page_title="부부 은퇴 자산 입체 계측기 v5.6", layout="wide")

# 스타일 리모델링 (표 가독성 극대화 및 숫자를 보기 편하게 만듦)
st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; }
    div.stDataFrame div[data-testid="stTable"] { font-family: 'Pretendard', sans-serif; }
    .css-17eq0hr { border-radius: 10px; background-color: #f8f9fa; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👑 부부 은퇴 자산 초정밀 계측기 v5.6")
st.caption("남편 자산(예수금/CMA) 완전 분리 및 시뮬레이션 연도 설정 기능 복구 버전")
st.markdown("---")

# 1단계: 자산 설정 (사이드바 - 남편 예수금과 CMA 완벽 분류)
st.sidebar.header("⚙️ 자산 설정 (만원)")
husband_jesus_init = st.sidebar.number_input("👨 남편 주식 예수금", value=110000, step=1000) * 10000
husband_cma_init = st.sidebar.number_input("👨 남편 CMA 잔액", value=1350, step=50) * 10000
wife_deposit_init = st.sidebar.number_input("👩 아내 정기예금 총액", value=42000, step=500) * 10000
wife_cma_init = st.sidebar.number_input("👩 아내 CMA 잔액", value=1200, step=50) * 10000
deposit_unit = st.sidebar.number_input("🔓 매년 만기되는 통장 단위", value=8400, step=100) * 10000

st.header("📈 전략 및 시장 변수 세팅")
c_etf, c_vars = st.columns(2)

with c_etf:
    st.subheader("🛡️ 남편 11억 TR ETF 2년 분할 전술")
    st.write("※ 남편 예수금(11억)을 2년(24개월) 동안 **매월 약 4,583만 원씩** 쪼개어 지수 TR ETF로 자동 적립합니다.")
    tr_etf_rate = st.slider("지수 TR ETF 예상 연 수익률 (%)", 1.0, 10.0, 5.0, 0.5) / 100

with c_vars:
    st.subheader("🛒 기간 및 생활비 환경")
    # 질문자님 요청으로 연도 설정 항목 다시 부활!
    years_to_run = st.number_input("📊 몇 년 동안 시뮬레이션할까요? (연금 개시 잔여년도)", value=10, min_value=1, max_value=30, step=1)
    living_cost_annual = st.number_input("연간 총 생활비 (만원)", value=7740, step=10) * 10000
    deposit_rate = st.slider("저축은행 정기예금 금리 (%)", 1.0, 6.0, 4.0, 0.1) / 100
    cma_rate = st.slider("대신증권 CMA 금리 (%)", 1.0, 6.0, 3.0, 0.1) / 100

st.markdown("---")

if st.button("🚀 부부 최적화 초정밀 시뮬레이션 가동", type="primary"):
    # 자산 초기 상태 세팅 (입력된 예수금과 CMA를 각각 독립적으로 복사)
    h_jesus = husband_jesus_init
    h_cma = husband_cma_init
    h_tr_etf = 0
    
    w_deposit = wife_deposit_init
    w_cma = wife_cma_init
    w_new_deposit = 0
    
    jesus_rate = 0.006
    tax_rate = 0.154
    monthly_living_cost = living_cost_annual / 12
    
    # 24개월간 매달 들어갈 TR ETF 금액 세팅 (11억 원 기준)
    monthly_tr_transfer = 1100000000 / 24  
    
    yearly_records = []
    monthly_records = []
    
    # 질문자님이 설정한 가동 연수(years_to_run)만큼 루프 돌리기
    for year in range(1, years_to_run + 1):
        # 2년차 진입 시 질문자님의 최적 안심 눈금 고정 수비 자동 발동
        if year == 2:
            w_deposit = 365000000
            w_new_deposit = 80000000
            w_cma = 40000000

        # 연초 금융소득 가집계 (월별 흐름 전 세전금액 확정)
        h_interest_pre = (h_jesus * jesus_rate) + (h_cma * cma_rate)
        if year <= 5:
            w_interest_pre = (w_deposit * deposit_rate) + (w_new_deposit * deposit_rate) + ((w_cma * cma_rate) / 2)
        else:
            w_interest_pre = 0

        h_interest_post = int(h_interest_pre * (1 - tax_rate))
        w_interest_post = int(w_interest_pre * (1 - tax_rate))
        total_income_post = h_interest_post + w_interest_post
        
        # 연초 이자를 생활비 지갑에 미리 적립
        if year <= 5:
            w_cma += total_income_post
        else:
            h_cma += total_income_post

        # --- [12개월 정밀 월별 시뮬레이션] ---
        for month in range(1, 13):
            # 1~2년차인 경우(총 24개월 동안) 매달 남편 예수금에서 TR ETF로 자금 이사
            if year <= 2:
                if h_jesus >= monthly_tr_transfer:
                    h_jesus -= monthly_tr_transfer
                    h_tr_etf += monthly_tr_transfer
                else:
                    h_tr_etf += h_jesus
                    h_jesus = 0
            
            # 매달 생활비 차감 (5년차까지는 아내CMA, 6년차부터는 남편CMA)
            if year <= 5:
                w_cma -= monthly_living_cost
            else:
                h_cma -= monthly_living_cost
            
            # 월별 장부 기록 (만원 단위 정수화)
            monthly_records.append({
                "연차": f"{year}년차",
                "월": f"{month}월",
                "👨남편 주식예수금": int(h_jesus / 10000),
                "👨남편 CMA잔액": int(h_cma / 10000),
                "👨남편 지수TR ETF": int(h_tr_etf / 10000),
                "👩아내 정기예금": int(max(0, (w_deposit + w_new_deposit)) / 10000) if year <= 5 else 0,
                "👩아내 CMA": int(max(0, w_cma) / 10000) if year <= 5 else 0,
                "👪부부 합산 자산": int((h_jesus + h_cma + h_tr_etf + max(0, w_deposit + w_new_deposit) + max(0, w_cma)) / 10000)
            })
            
        # 연말 TR ETF 수익률 복리 정산
        h_tr_etf = int(h_tr_etf * (1 + tr_etf_rate))
        
        # 연말 아내 정기예금 청산 스케줄링
        if year <= 5:
            deficit = int(living_cost_annual - total_income_post)
            leftover = deposit_unit - deficit
            w_deposit -= deposit_unit
            w_cma += leftover
        else:
            deficit = int(living_cost_annual - total_income_post)
            leftover = 0

        # 연간 종합 성적표 저장
        yearly_records.append({
            "연차": f"{year}년차",
            "남편세전": h_interest_pre,
            "아내세전": w_interest_pre,
            "세후이자": total_income_post,
            "부족분": deficit,
            "잔돈": leftover,
            "남편총액": h_jesus + h_cma + h_tr_etf,
            "아내총액": max(0, w_deposit + w_new_deposit + w_cma) if year <= 5 else 0
        })

    # --- [3단계: 화면 출력] ---
    tab_yearly, tab_monthly = st.tabs(["📅 연차별 요약 및 부부별 건보료선 정밀 검증", "📊 부부 각각 월별 주머니 잔고 현황 (초정밀 표)"])
    
    with tab_yearly:
        st.subheader("📋 부부 명의별 금융소득 및 건강보험료 자격 검증 리포트")
        for res in yearly_records:
            with st.expander(f"💎 {res['연차']} 부부 개별 금융소득 수비 성적 확인하기"):
                col_h, col_w = st.columns(2)
                
                with col_h:
                    st.markdown("#### 👨 남편 명의 주머니 검증")
                    st.metric("세전 금융소득", f"{int(res['남편세전']/10000):,} 만원")
                    
                    h_margin = 10000000 - res['남편세전']
                    if h_margin > 0:
                        st.success(f"🛡️ 건보료 피부양자 안전지대 (마지노선까지 **{int(h_margin/10000):,}만원** 여유)")
                    else:
                        st.error(f"🚨 경고: 1,000만원 초과! 남편 별도 건보료 부과 대상 지역 진입 (초과액: {int(abs(h_margin)/10000):,}만원)")
                    st.caption(f"· 연말 남편 자산 총합: {int(res['남편총액']/10000):,} 만원")

                with col_w:
                    st.markdown("#### 👩 아내 명의 주머니 검증")
                    st.metric("세전 금융소득", f"{int(res['아내세전']/10000):,} 만원")
                    
                    w_margin = 20000000 - res['아내세전']
                    if w_margin > 0:
                        st.success(f"🛡️ 금융소득 종합과세 안전지대 (마지노선까지 **{int(w_margin/10000):,}만원** 여유)")
                    else:
                        st.error(f"🚨 경고: 2,000만원 초과! 금융소득 종합과세 위험!")
                    st.caption(f"· 연말 아내 자산 총합: {int(res['아내총액']/10000):,} 만원")
                
                st.markdown("---")
                col_tot1, col_tot2, col_tot3 = st.columns(3)
                with col_tot1:
                    st.metric("👪 부부 합산 세후 이자 수령액", f"{int(res['세후이자']/10000):,} 만원")
                with col_tot2:
                    st.warning(f"🛒 연간 생활비 부족 구멍: {int(res['부족분']/10000):,} 만원")
                with col_tot3:
                    if res['잔돈'] > 0:
                        st.success(f"💰 통장 깨고 남은 알짜 잔돈: {int(res['잔돈']/10000):,} 만원")
                    else:
                        st.info("💡 6년차 이후: 남편 유동성 주머니(CMA)에서 생활비 다이렉트 차감 중")

    with tab_monthly:
        st.subheader("🗓️ 월 단위 부부 계좌 잔고 입체 표 (24개월 TR ETF 분할 매수 반영)")
        df_monthly = pd.DataFrame(monthly_records)
        
        st.dataframe(
            df_monthly.style.format({
                "👨남편 주식예수금": "{:,} 만원",
                "👨남편 CMA잔액": "{:,} 만원",
                "👨남편 지수TR ETF": "{:,} 만원",
                "👩아내 정기예금": "{:,} 만원",
                "👩아내 CMA": "{:,} 만원",
                "👪부부 합산 자산": "{:,} 만원"
            }),
            use_container_width=True,
            height=600
        )
        
        st.subheader("📉 자산 요새 총액 감소 추이선")
        st.line_chart(df_monthly.set_index(["연차", "월"])["👪부부 합산 자산"])
    
