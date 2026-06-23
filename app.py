import streamlit as st
import pandas as pd

st.set_page_config(page_title="부부 은퇴 자산 입체 계측기 v5.9", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; }
    div.stDataFrame div[data-testid="stTable"] { font-family: 'Pretendard', sans-serif; }
    .css-17eq0hr { border-radius: 10px; background-color: #f8f9fa; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👑 부부 은퇴 자산 초정밀 계측기 v5.9")
st.caption("잉여 자금 저축 항목 신설 및 차기년도 예산·기초자산 자동 반영 시스템")
st.markdown("---")

# 기본 설정 및 기간 입력 (사이드바 상단)
st.sidebar.header("🗓️ 기본 환경 설정")
years_to_run = st.sidebar.number_input("📊 시뮬레이션 기간 (년)", value=10, min_value=1, max_value=30, step=1)
living_cost_annual = st.sidebar.number_input("🛒 연간 총 생활비 (만원)", value=7740, step=10) * 10000
deposit_unit = st.sidebar.number_input("🔓 매년 만기/소비되는 아내 예금 단위", value=8400, step=100) * 10000

# 저축 및 재투자 전략 설정 (사이드바 중단)
st.sidebar.markdown("---")
st.sidebar.header("💰 연말 잉여금 저축·재투자 설정")
saving_destination = st.sidebar.selectbox(
    "매년 생활비를 쓰고 남은 잔돈을 어디에 저축(반영)할까요?",
    ["👩 아내 CMA 통장으로 저축 (추천)", "👨 남편 CMA 통장으로 저축", "📈 지수 TR ETF로 즉시 재투자"]
)

# 1단계: 연차별 초기 자산 설정
st.sidebar.markdown("---")
st.sidebar.header("⚙️ 연차별 초기 자산 설정")
selected_setup_year = st.sidebar.selectbox("자산을 세팅할 연차를 선택하세요", [f"{i}년차" for i in range(1, years_to_run + 1)])
setup_year_num = int(selected_setup_year.replace("년차", ""))

if "asset_config" not in st.session_state:
    st.session_state.asset_config = {}

for y in range(1, years_to_run + 1):
    if y not in st.session_state.asset_config:
        if y == 1:
            st.session_state.asset_config[y] = {"h_jesus": 110000, "h_cma": 1350, "w_deposit": 42000, "w_cma": 1200, "w_new_deposit": 0}
        elif y == 2:
            st.session_state.asset_config[y] = {"h_jesus": 55000, "h_cma": 1350, "w_deposit": 36500, "w_cma": 4000, "w_new_deposit": 8000}
        else:
            # 3년차 이후는 기본적으로 앞선 자산 흐름을 이어받지만, 사용자가 수동 유입액을 적을 수 있도록 0으로 대기
            st.session_state.asset_config[y] = {"h_jesus": 0, "h_cma": 0, "w_deposit": 0, "w_cma": 0, "w_new_deposit": 0}

st.sidebar.subheader(f"📍 [{selected_setup_year}] 초기 자산 눈금 조정")
c_hj = st.sidebar.number_input(f"👨 {selected_setup_year} 남편 주식 예수금 (만원)", value=st.session_state.asset_config[setup_year_num]["h_jesus"], step=1000)
c_hc = st.sidebar.number_input(f"👨 {selected_setup_year} 남편 CMA 잔액 (만원)", value=st.session_state.asset_config[setup_year_num]["h_cma"], step=50)
c_wd = st.sidebar.number_input(f"👩 {selected_setup_year} 아내 기존정기예금 (만원)", value=st.session_state.asset_config[setup_year_num]["w_deposit"], step=500)
c_wn = st.sidebar.number_input(f"👩 {selected_setup_year} 아내 신규정기예금 (만원)", value=st.session_state.asset_config[setup_year_num]["w_new_deposit"], step=500)
c_wc = st.sidebar.number_input(f"👩 {selected_setup_year} 아내 CMA 잔액 (만원)", value=st.session_state.asset_config[setup_year_num]["w_cma"], step=50)

st.session_state.asset_config[setup_year_num] = {
    "h_jesus": c_hj, "h_cma": c_hc, "w_deposit": c_wd, "w_new_deposit": c_wn, "w_cma": c_wc
}

# 변수 및 전략 설정 (메인 화면)
st.header("📈 전략 및 시장 변수 세팅")
c_etf, c_vars = st.columns(2)

with c_etf:
    st.subheader("🛡️ 남편 11억 TR ETF 2년 분할 전술")
    tr_etf_rate = st.slider("지수 TR ETF 예상 연 수익률 (%)", 1.0, 10.0, 5.0, 0.5) / 100

with c_vars:
    st.subheader("💰 시장 적용 금리")
    deposit_rate = st.slider("저축은행 정기예금 금리 (%)", 1.0, 6.0, 4.0, 0.1) / 100
    cma_rate = st.slider("대신증권 CMA 금리 (%)", 1.0, 6.0, 3.0, 0.1) / 100

st.markdown("---")

if st.button("🚀 연차별 자산 장부 동기화 및 시뮬레이션 가동", type="primary"):
    # 시뮬레이션 내부 연동용 캐월(carry-over) 잔고 변수 선언
    carry_over_h_cma = 0
    carry_over_w_cma = 0
    carry_over_tr_etf = 0
    
    h_tr_etf = 0
    jesus_rate = 0.006
    tax_rate = 0.154
    monthly_living_cost = living_cost_annual / 12
    monthly_tr_transfer = 1100000000 / 24  
    
    yearly_records = []
    monthly_records = []
    
    for year in range(1, years_to_run + 1):
        cfg = st.session_state.asset_config[year]
        
        # [핵심 로직] 사용자가 수동으로 가치를 입력했으면 그것을 쓰고, 0이면 전년도 이월(저축 반영) 자산을 승계
        h_jesus = cfg["h_jesus"] * 10000
        
        h_cma = (cfg["h_cma"] * 10000) if cfg["h_cma"] > 0 else carry_over_h_cma
        w_deposit = cfg["w_deposit"] * 10000
        w_new_deposit = cfg["w_new_deposit"] * 10000
        w_cma = (cfg["w_cma"] * 10000) if cfg["w_cma"] > 0 else carry_over_w_cma
        
        if year > 1 and carry_over_tr_etf > 0:
            h_tr_etf = carry_over_tr_etf

        # --- [항목별 이자 명세서 추출] ---
        h_jesus_interest = h_jesus * jesus_rate
        h_cma_interest = h_cma * cma_rate
        h_interest_pre = h_jesus_interest + h_cma_interest
        
        w_old_dep_interest = w_deposit * deposit_rate
        w_new_dep_interest = w_new_deposit * deposit_rate
        w_cma_interest = (w_cma * cma_rate) / 2
        w_interest_pre = w_old_dep_interest + w_new_dep_interest + w_cma_interest

        h_interest_post = int(h_interest_pre * (1 - tax_rate))
        w_interest_post = int(w_interest_pre * (1 - tax_rate))
        total_income_post = h_interest_post + w_interest_post
        
        # 연초 이자를 우선 아내 생활비 지갑에 충전
        if year <= 5:
            w_cma += total_income_post
        else:
            h_cma += total_income_post

        # --- [12개월 정밀 월별 시뮬레이션] ---
        for month in range(1, 13):
            if year <= 2:
                if h_jesus >= monthly_tr_transfer:
                    h_jesus -= monthly_tr_transfer
                    h_tr_etf += monthly_tr_transfer
                else:
                    h_tr_etf += h_jesus
                    h_jesus = 0
            
            # 부부 생활비 지갑 우선순위 차감
            if w_cma >= monthly_living_cost:
                w_cma -= monthly_living_cost
            else:
                if h_cma >= monthly_living_cost:
                    h_cma -= monthly_living_cost
                else:
                    h_cma = 0
            
            monthly_records.append({
                "연차": f"{year}년차",
                "월": f"{month}월",
                "👨남편 주식예수금": int(h_jesus / 10000),
                "👨남편 CMA잔액": int(h_cma / 10000),
                "👨남편 지수TR ETF": int(h_tr_etf / 10000),
                "👩아내 정기예금": int(max(0, (w_deposit + w_new_deposit)) / 10000),
                "👩아내 CMA": int(max(0, w_cma) / 10000),
                "👪부부 합산 자산": int((h_jesus + h_cma + h_tr_etf + max(0, w_deposit + w_new_deposit) + max(0, w_cma)) / 10000)
            })
            
        # 연말 TR ETF 성장 정산
        h_tr_etf = int(h_tr_etf * (1 + tr_etf_rate))
        
        # [★정밀 계산기 연동★] 생활비 쓰고 남은 잔돈 계산
        deficit = int(living_cost_annual - total_income_post)
        leftover = deposit_unit - deficit if w_deposit >= deposit_unit else 0
        
        if w_deposit >= deposit_unit:
            w_deposit -= deposit_unit
        
        # 연말 최종 남은 잉여 자금을 약속한 주머니에 저축 및 재투자 반영
        saved_amount = leftover
        if year > 5:  # 예금 소멸 이후 연차에 혹시 이자가 더 많아 잔돈이 생기는 경우 처리
            saved_amount = int(max(0, h_cma + w_cma - (living_cost_annual)))
            
        if "아내 CMA" in saving_destination:
            w_cma += saved_amount
        elif "남편 CMA" in saving_destination:
            h_cma += saved_amount
        elif "지수 TR ETF" in saving_destination:
            h_tr_etf += saved_amount

        # 연말 정산 잔고를 '차기년도 이월 기초자산(Carry-over)'으로 저장
        carry_over_h_cma = h_cma
        carry_over_w_cma = w_cma
        carry_over_tr_etf = h_tr_etf

        yearly_records.append({
            "연차": f"{year}년차",
            "남편세전": h_interest_pre,
            "남편예수금이차": h_jesus_interest,
            "남편CMA이자": h_cma_interest,
            "아내세전": w_interest_pre,
            "아내기존예금이차": w_old_dep_interest,
            "아내신규예금이차": w_new_dep_interest,
            "아내CMA이자": w_cma_interest,
            "세후이자": total_income_post,
            "부족분": deficit,
            "당해저축반영액": saved_amount,
            "저축처": saving_destination.split(" ")[1] + " " + saving_destination.split(" ")[2],
            "남편총액": h_jesus + h_cma + h_tr_etf,
            "아내총액": max(0, w_deposit + w_new_deposit + w_cma)
        })

    # --- [결과 화면 출력] ---
    tab_yearly, tab_monthly = st.tabs(["📅 연차별 요약 및 부부별 건보료선 정밀 검증", "📊 부부 각각 월별 주머니 잔고 현황"])
    
    with tab_yearly:
        st.subheader("📋 부부 명의별 자산 세부항목 이자 및 차기년도 저축 명세")
        for res in yearly_records:
            with st.expander(f"💎 {res['연차']} 부부 금융수비 및 차기 예산 반영액 확인하기"):
                col_h, col_w = st.columns(2)
                
                with col_h:
                    st.markdown("#### 👨 남편 명의 이자 명세서")
                    st.metric("남편 세전 금융소득 합계", f"{int(res['남편세전']/10000):,} 만원")
                    st.markdown(f"""
                    * **주식 예수금 이용료 (연 0.6%):** {int(res['남편예수금이차']/10000):,} 만원
                    * **대신증권 CMA 이자:** {int(res['남편CMA이자']/10000):,} 만원
                    """)
                    h_margin = 10000000 - res['남편세전']
                    if h_margin > 0:
                        st.success(f"🛡️ 건보료 안전지대 (마지노선까지 **{int(h_margin/10000):,}만원** 여유)")
                    else:
                        st.error(f"🚨 경고: 1,000만원 초과! 건보료 부과 대상")

                with col_w:
                    st.markdown("#### 👩 아내 명의 이자 명세서")
                    st.metric("아내 세전 금융소득 합계", f"{int(res['아내세전']/10000):,} 만원")
                    st.markdown(f"""
                    * **기존 정기예금 이자:** {int(res['아내기존예금이차']/10000):,} 만원
                    * **신규 정기예금 이자:** {int(res['아내신규예금이차']/10000):,} 만원
                    * **대신증권 CMA 이자:** {int(res['아내CMA이자']/10000):,} 만원
                    """)
                    w_margin = 20000000 - res['아내세전']
                    if w_margin > 0:
                        st.success(f"🛡️ 종합과세 안전지대 (마지노선까지 **{int(w_margin/10000):,}만원** 여유)")
                    else:
                        st.error(f"🚨 경고: 2,000만원 초과! 금융소득 종합과세 대상")
                
                st.markdown("---")
                col_tot1, col_tot2, col_tot3 = st.columns(3)
                with col_tot1:
                    st.metric("👪 부부 합산 세후 이자 수령액", f"{int(res['세후이자']/10000):,} 만원")
                with col_tot2:
                    st.warning(f"🛒 연간 생활비 부족 구멍: {int(res['부족분']/10000):,} 만원")
                with col_tot3:
                    # [재투자 및 저축 눈금 시각화]
                    st.metric(f"💰 차기년도 예산 자동 반영액 ({res['저축처']})", f"{int(res['당해저축반영액']/10000):,} 만원")
                    st.caption("※ 이 잔돈은 다음 해의 기초 자산으로 귀속되어 복리로 정상 가동됩니다.")

    with tab_monthly:
        st.subheader("🗓️ 월 단위 부부 계좌 잔고 입체 표")
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
        st.line_chart(df_monthly.set_index(["연차", "월"])["👪부부 합산 자산"])
