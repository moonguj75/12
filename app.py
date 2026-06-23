import streamlit as st
import pandas as pd

st.set_page_config(page_title="부부 은퇴 자산 입체 계측기 v6.7", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; }
    div.stDataFrame div[data-testid="stTable"] { font-family: 'Pretendard', sans-serif; }
    .css-17eq0hr { border-radius: 10px; background-color: #f8f9fa; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👑 부부 은퇴 자산 초정밀 계측기 v6.7")
st.caption("v6.7 수정사항: ① st.success() 인자 오류 수정 ② carry 이월 로직 버그 수정")
st.markdown("---")

# 기본 설정 및 기간 입력 (사이드바 상단)
st.sidebar.header("🗓️ 기본 환경 설정")
years_to_run = st.sidebar.number_input("📊 전체 시뮬레이션 기간 (년)", value=10, min_value=1, max_value=30, step=1)
living_cost_annual = st.sidebar.number_input("🛒 연간 총 생활비 (만원)", value=7740, step=10) * 10000
deposit_unit = st.sidebar.number_input("🔓 매년 만기/소비되는 아내 예금 단위", value=8400, step=100) * 10000

# 1단계: 연차별 자산 설정 구역
st.sidebar.markdown("---")
st.sidebar.header("⚙️ 연차별 자산 설정")

selected_setup_year = st.sidebar.selectbox("계측 및 자산 설정을 진행할 연차를 고르세요", [f"{i}년차" for i in range(1, years_to_run + 1)])
setup_year_num = int(selected_setup_year.replace("년차", ""))

if "asset_config" not in st.session_state:
    st.session_state.asset_config = {}

# KeyError 방지 — 모든 연차 기본값 사전 확보
for y in range(1, years_to_run + 1):
    if y == 1:
        st.session_state.asset_config.setdefault(y, {"h_jesus": 110000, "h_cma": 1350, "w_deposit": 42000, "w_cma": 1200, "w_new_deposit": 0, "override": True})
    elif y == 2:
        st.session_state.asset_config.setdefault(y, {"h_jesus": 55000, "h_cma": 1350, "w_deposit": 36500, "w_cma": 4000, "w_new_deposit": 8000, "override": True})
    else:
        st.session_state.asset_config.setdefault(y, {"h_jesus": 0, "h_cma": 0, "w_deposit": 0, "w_cma": 0, "w_new_deposit": 0, "override": False})

st.sidebar.subheader(f"📍 [{selected_setup_year}] 초기 자산 배정")

# override 플래그: 해당 연차에 사용자가 직접 값을 지정할지 여부
override_flag = st.sidebar.checkbox(
    f"{selected_setup_year} 자산을 직접 지정 (체크 해제 시 자동 이월)",
    value=st.session_state.asset_config[setup_year_num].get("override", setup_year_num <= 2)
)

c_hj = st.sidebar.number_input(f"👨 {selected_setup_year} 남편 주식 예수금 (만원)", value=st.session_state.asset_config[setup_year_num]["h_jesus"], step=1000, disabled=not override_flag)
c_hc = st.sidebar.number_input(f"👨 {selected_setup_year} 남편 CMA 잔액 (만원)", value=st.session_state.asset_config[setup_year_num]["h_cma"], step=50, disabled=not override_flag)
c_wd = st.sidebar.number_input(f"👩 {selected_setup_year} 아내 기존정기예금 (만원)", value=st.session_state.asset_config[setup_year_num]["w_deposit"], step=500, disabled=not override_flag)
c_wn = st.sidebar.number_input(f"👩 {selected_setup_year} 아내 신규정기예금 (만원)", value=st.session_state.asset_config[setup_year_num]["w_new_deposit"], step=500, disabled=not override_flag)
c_wc = st.sidebar.number_input(f"👩 {selected_setup_year} 아내 CMA 잔액 (만원)", value=st.session_state.asset_config[setup_year_num]["w_cma"], step=50, disabled=not override_flag)

st.session_state.asset_config[setup_year_num] = {
    "h_jesus": c_hj, "h_cma": c_hc, "w_deposit": c_wd, "w_new_deposit": c_wn, "w_cma": c_wc,
    "override": override_flag
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

if st.button(f"🚀 {selected_setup_year} 자산 장부 집중 동기화 가동", type="primary"):
    carry_h_jesus = 0
    carry_h_cma = 0
    carry_w_deposit = 0
    carry_w_new_deposit = 0
    carry_w_cma = 0
    h_tr_etf = 0

    jesus_rate = 0.006
    tax_rate = 0.154
    monthly_living_cost = living_cost_annual / 12
    monthly_tr_transfer = 1100000000 / 24

    yearly_records = []
    monthly_records = []

    for year in range(1, years_to_run + 1):
        cfg = st.session_state.asset_config.get(
            year,
            {"h_jesus": 0, "h_cma": 0, "w_deposit": 0, "w_cma": 0, "w_new_deposit": 0, "override": False}
        )

        use_override = (year == 1) or cfg.get("override", False)

        h_jesus      = cfg["h_jesus"] * 10000       if use_override else carry_h_jesus
        h_cma        = cfg["h_cma"] * 10000         if use_override else carry_h_cma
        w_deposit    = cfg["w_deposit"] * 10000     if use_override else carry_w_deposit
        w_new_deposit= cfg["w_new_deposit"] * 10000 if use_override else carry_w_new_deposit
        w_cma        = cfg["w_cma"] * 10000         if use_override else carry_w_cma

        # 이자 산출
        h_jesus_interest   = h_jesus * jesus_rate
        h_cma_interest     = h_cma * cma_rate
        h_interest_pre     = h_jesus_interest + h_cma_interest

        w_old_dep_interest = w_deposit * deposit_rate
        w_new_dep_interest = w_new_deposit * deposit_rate
        w_cma_interest_val = (w_cma * cma_rate) / 2
        w_interest_pre     = w_old_dep_interest + w_new_dep_interest + w_cma_interest_val

        h_interest_post    = int(h_interest_pre * (1 - tax_rate))
        w_interest_post    = int(w_interest_pre * (1 - tax_rate))
        total_income_post  = h_interest_post + w_interest_post

        if year <= 5:
            w_cma += total_income_post
        else:
            h_cma += total_income_post

        # 12개월 연산
        for month in range(1, 13):
            if year <= 2:
                if h_jesus >= monthly_tr_transfer:
                    h_jesus -= monthly_tr_transfer
                    h_tr_etf += monthly_tr_transfer
                else:
                    h_tr_etf += h_jesus
                    h_jesus = 0

            if w_cma >= monthly_living_cost:
                w_cma -= monthly_living_cost
            else:
                if h_cma >= monthly_living_cost:
                    h_cma -= monthly_living_cost
                else:
                    h_cma = 0

            if year == setup_year_num:
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

        h_tr_etf = int(h_tr_etf * (1 + tr_etf_rate))

        deficit  = int(living_cost_annual - total_income_post)
        leftover = deposit_unit - deficit if w_deposit >= deposit_unit else 0

        if w_deposit >= deposit_unit:
            w_deposit -= deposit_unit

        w_cma += leftover

        # 이월 데이터 상속
        carry_h_jesus      = h_jesus
        carry_h_cma        = h_cma
        carry_w_deposit    = w_deposit
        carry_w_new_deposit= w_new_deposit
        carry_w_cma        = w_cma

        yearly_records.append({
            "연차": f"{year}년차",
            "남편세전": h_interest_pre,
            "남편예수금이차": h_jesus_interest,
            "남편CMA이자": h_cma_interest,
            "아내세전": w_interest_pre,
            "아내기존예금이차": w_old_dep_interest,
            "아내신규예금이차": w_new_dep_interest,
            "아내CMA이자": w_cma_interest_val,
            "세후이자": total_income_post,
            "부족분": deficit,
            "잔돈": leftover
        })

    # --- 결과 출력 ---
    st.header(f"🏁 3단계: [{selected_setup_year}] 집중 분석 리포트")

    tab_yearly, tab_monthly = st.tabs(["📅 건보료선 정밀 검증 보고서", "📊 월별 주머니 잔고 현황 (해당 연차 전용)"])

    target_res = yearly_records[setup_year_num - 1]

    with tab_yearly:
        col_h, col_w = st.columns(2)
        with col_h:
            st.markdown("#### 👨 남편 명의 이자 명세서")
            st.metric("남편 세전 금융소득 합계", f"{int(target_res['남편세전']/10000):配置} 만원".replace('配置', ''))
            st.metric("남편 세전 금융소득 합계", f"{int(target_res['남편세전']/10000):,} 만원")
            st.markdown(f"""
            * **주식 예수금 이용료 (연 0.6%):** {int(target_res['남편예수금이차']/10000):,} 만원
            * **대신증권 CMA 이자:** {int(target_res['남편CMA이자']/10000):,} 만원
            """)
            h_margin = 10000000 - target_res['남편세전']
            if h_margin > 0:
                st.success(f"🛡️ 건보료 안전지대 (마지노선까지 {int(h_margin/10000):,}만원 여유)")
            else:
                st.error(f"🚨 경고: 1,000만원 초과! 건보료 부과 대상")

        with col_w:
            st.markdown("#### 👩 아내 명의 이자 명세서")
            st.metric("아내 세전 금융소득 합계", f"{int(target_res['아내세전']/10000):,} 만원")
            st.markdown(f"""
            * **기존 정기예금 이자:** {int(target_res['아내기존예금이차']/10000):,} 만원
            * **신규 정기예금 이자:** {int(target_res['아내신규예금이차']/10000):,} 만원
            * **대신증권 CMA 이자:** {int(target_res['아내CMA이자']/10000):,} 만원
            """)
            w_margin = 20000000 - target_res['아내세전']
            if w_margin > 0:
                st.success(f"🛡️ 종합과세 안전지대 (마지노선까지 {int(w_margin/10000):,}만원 여유)")
            else:
                st.error(f"🚨 경고: 2,000만원 초과! 종합과세 대상")

        st.markdown("---")
        col_tot1, col_tot2, col_tot3 = st.columns(3)
        with col_tot1:
            st.metric("👪 부부 합산 세후 이자 수령액", f"{int(target_res['세후이자']/10000):,} 만원")
        with col_tot2:
            st.warning(f"🛒 연간 생활비 부족 구멍: {int(target_res['부족분']/10000):,} 만원")
        with col_tot3:
            st.success(f"💰 통장 깨고 남은 알짜 잔돈(자동 저축): {int(target_res['잔돈']/10000):,} 만원")
            st.caption("※ 연말에 남은 잔돈은 자동으로 아내 CMA 통장으로 전액 이양됩니다.")

    with tab_monthly:
        st.subheader(f"🗓️ [{selected_setup_year}] 1월 ~ 12월 주머니별 잔고 이동 보고서")
        df_monthly = pd.DataFrame(monthly_records)
        # ★깔끔하게 코드의 마무리를 짓는 세션 가동
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
            height=450
        )
