import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="부부 은퇴 자산 입체 계측기 v6.9.1", layout="wide")

st.markdown("""
    <style>
    .reportview-container .main .block-container{ max-width: 95%; }
    div.stDataFrame div[data-testid="stTable"] { font-family: 'Pretendard', sans-serif; }
    .css-17eq0hr { border-radius: 10px; background-color: #f8f9fa; padding: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👑 부부 은퇴 자산 초정밀 계측기 v6.9.1")
st.caption("v6.9.1 수정사항: 입력창 변경 즉시 세션 버퍼에 동기화되도록 패치하여 [💾 현재 세팅 기억] 기능 무결점화")
st.markdown("---")

# ----------------------------------------------------------------
# [★안전 장치★] 영구 기억 장치 및 실시간 입력 감지 버퍼 초기화
# ----------------------------------------------------------------
if "global_snapshot" not in st.session_state:
    st.session_state.global_snapshot = {
        "start_date": datetime(2026, 6, 23).date(),
        "years_to_run": 10,
        "living_cost_annual": 7740,
        "deposit_unit": 8400,
        "tr_etf_rate": 5.0,
        "deposit_rate": 4.0,
        "cma_rate": 3.0,
        "jesus_rate": 0.6,
        "asset_config": {
            1: {"h_jesus": 110000, "h_deposit": 0, "h_cma": 1350, "w_deposit": 42000, "w_cma": 1200, "override": True},
            2: {"h_jesus": 55000, "h_deposit": 0, "h_cma": 1350, "w_deposit": 36500, "w_cma": 4000, "override": True}
        }
    }

if "buffer" not in st.session_state:
    st.session_state.buffer = st.session_state.global_snapshot.copy()

if "asset_config" not in st.session_state:
    st.session_state.asset_config = st.session_state.buffer["asset_config"].copy()

# [★핵심 패치★] 화면에서 조정한 숫자가 즉시 버퍼에 누적 보존되도록 연동하는 콜백 함수들
def update_buffer_meta():
    st.session_state.buffer["start_date"] = st.session_state.start_date_input
    st.session_state.buffer["years_to_run"] = st.session_state.years_to_run_input
    st.session_state.buffer["living_cost_annual"] = st.session_state.living_cost_annual_input
    st.session_state.buffer["deposit_unit"] = st.session_state.deposit_unit_input
    st.session_state.buffer["tr_etf_rate"] = st.session_state.tr_etf_rate_input
    st.session_state.buffer["deposit_rate"] = st.session_state.deposit_rate_input
    st.session_state.buffer["cma_rate"] = st.session_state.cma_rate_input
    st.session_state.buffer["jesus_rate"] = st.session_state.jesus_rate_input

# ----------------------------------------------------------------
# 💾 사이드바 최상단 저장 / 불러오기 제어 센터
# ----------------------------------------------------------------
st.sidebar.header("💾 장부 세팅 제어 센터")
col_save, col_load = st.sidebar.columns(2)

with col_save:
    if st.button("💾 현재 세팅 기억", use_container_width=True, type="secondary"):
        # 실시간 버퍼에 쌓여있던 가장 따끈따끈한 세팅 가치를 마스터 저장소에 영구 박제
        st.session_state.global_snapshot = {
            "start_date": st.session_state.buffer["start_date"],
            "years_to_run": st.session_state.buffer["years_to_run"],
            "living_cost_annual": st.session_state.buffer["living_cost_annual"],
            "deposit_unit": st.session_state.buffer["deposit_unit"],
            "tr_etf_rate": st.session_state.buffer["tr_etf_rate"],
            "deposit_rate": st.session_state.buffer["deposit_rate"],
            "cma_rate": st.session_state.buffer["cma_rate"],
            "jesus_rate": st.session_state.buffer["jesus_rate"],
            "asset_config": st.session_state.asset_config.copy()
        }
        st.sidebar.success("정확하게 기억 완료!")

with col_load:
    if st.button("📂 세팅 불러오기", use_container_width=True):
        # 마스터 저장소 값을 버퍼와 자산 설정창으로 강제 복원 유도
        st.session_state.buffer = st.session_state.global_snapshot.copy()
        st.session_state.asset_config = st.session_state.global_snapshot["asset_config"].copy()
        st.rerun()

st.sidebar.markdown("---")

# ----------------------------------------------------------------
# 기본 환경 설정 (on_change를 걸어 실시간으로 입력 탈취)
# ----------------------------------------------------------------
st.sidebar.header("🗓️ 기본 환경 및 시작일 설정")
start_date = st.sidebar.date_input("🚀 시뮬레이션 기준 시작일", value=st.session_state.buffer["start_date"], key="start_date_input", on_change=update_buffer_meta)
years_to_run = st.sidebar.number_input("📊 전체 시뮬레이션 기간 (년)", value=int(st.session_state.buffer["years_to_run"]), min_value=1, max_value=30, step=1, key="years_to_run_input", on_change=update_buffer_meta)
living_cost_annual_display = st.sidebar.number_input("🛒 연간 총 생활비 (만원)", value=int(st.session_state.buffer["living_cost_annual"]), step=10, key="living_cost_annual_input", on_change=update_buffer_meta)
living_cost_annual = living_cost_annual_display * 10000
deposit_unit_display = st.sidebar.number_input("🔓 매년 만기/소비되는 아내 예금 단위", value=int(st.session_state.buffer["deposit_unit"]), step=10, key="deposit_unit_input", on_change=update_buffer_meta)
deposit_unit = deposit_unit_display * 10000

# ----------------------------------------------------------------
# 1단계: 연차별 자산 설정 구역
# ----------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.header("⚙️ 연차별 자산 설정")
year_options = [f"{i}년차({start_date.year + i - 1}년)" for i in range(1, years_to_run + 1)]
selected_setup_year = st.sidebar.selectbox("계측 및 자산 설정을 진행할 연차를 고르세요", year_options)
setup_year_num = int(selected_setup_year.split("년차")[0])

# 빈 연차 자동 이월 안전망 형성
for y in range(1, years_to_run + 1):
    st.session_state.asset_config.setdefault(y, {"h_jesus": 0, "h_deposit": 0, "h_cma": 0, "w_deposit": 0, "w_cma": 0, "override": False})

target_display_year = start_date.year + setup_year_num - 1
st.sidebar.subheader(f"📍 [{setup_year_num}년차 ({target_display_year}년)] 자산 배정")

override_flag = st.sidebar.checkbox(
    f"{setup_year_num}년차 자산을 직접 지정 (체크 해제 시 자동 이월)",
    value=st.session_state.asset_config[setup_year_num].get("override", setup_year_num <= 2)
)

c_hj = st.sidebar.number_input(f"👨 {setup_year_num}년차 남편 주식 예수금 (만원)", value=int(st.session_state.asset_config[setup_year_num]["h_jesus"]), step=1000, disabled=not override_flag)
c_hd = st.sidebar.number_input(f"👨 {setup_year_num}년차 남편 정기예금 (만원)", value=int(st.session_state.asset_config[setup_year_num].get("h_deposit", 0)), step=500, disabled=not override_flag)
c_hc = st.sidebar.number_input(f"👨 {setup_year_num}년차 남편 CMA 잔액 (만원)", value=int(st.session_state.asset_config[setup_year_num]["h_cma"]), step=50, disabled=not override_flag)
c_wd = st.sidebar.number_input(f"👩 {setup_year_num}년차 아내 기존정기예금 (만원)", value=int(st.session_state.asset_config[setup_year_num]["w_deposit"]), step=500, disabled=not override_flag)
c_wc = st.sidebar.number_input(f"👩 {setup_year_num}년차 아내 CMA 잔액 (만원)", value=int(st.session_state.asset_config[setup_year_num]["w_cma"]), step=50, disabled=not override_flag)

st.session_state.asset_config[setup_year_num] = {
    "h_jesus": c_hj, "h_deposit": c_hd, "h_cma": c_hc, "w_deposit": c_wd, "w_cma": c_wc, "override": override_flag
}

# 변수 및 전략 설정 (메인 화면 - 실시간 동기화 연동)
st.header("📈 전략 및 시장 변수 세팅")
c_etf, c_vars = st.columns(2)

with c_etf:
    st.subheader("🛡️ 남편 11억 TR ETF 2년 분할 전술")
    tr_etf_rate = st.slider("지수 TR ETF 예상 연 수익률 (%)", 1.0, 10.0, value=float(st.session_state.buffer["tr_etf_rate"]), step=0.5, key="tr_etf_rate_input", on_change=update_buffer_meta) / 100

with c_vars:
    st.subheader("💰 시장 적용 금리")
    deposit_rate = st.slider("저축은행 정기예금 금리 (%)", 1.0, 6.0, value=float(st.session_state.buffer["deposit_rate"]), step=0.1, key="deposit_rate_input", on_change=update_buffer_meta) / 100
    cma_rate = st.slider("대신증권 CMA 금리 (%)", 1.0, 6.0, value=float(st.session_state.buffer["cma_rate"]), step=0.1, key="cma_rate_input", on_change=update_buffer_meta) / 100
    jesus_rate = st.slider("증권사 주식 예수금 이율 (%)", 0.1, 3.0, value=float(st.session_state.buffer["jesus_rate"]), step=0.1, key="jesus_rate_input", on_change=update_buffer_meta) / 100

st.markdown("---")

if st.button(f"🚀 {setup_year_num}년차 ({start_date.year + setup_year_num - 1}년) 장부 집중 가동", type="primary"):
    carry_h_jesus, carry_h_deposit, carry_h_cma = 0, 0, 0
    carry_w_deposit, carry_w_cma = 0, 0
    h_tr_etf = 0
    tax_rate = 0.154
    monthly_living_cost = living_cost_annual / 12
    monthly_tr_transfer = 1100000000 / 24

    yearly_records, monthly_records = [], []
    current_running_date = datetime(start_date.year, start_date.month, start_date.day)

    for year in range(1, years_to_run + 1):
        cfg = st.session_state.asset_config.get(year, {"h_jesus": 0, "h_deposit": 0, "h_cma": 0, "w_deposit": 0, "w_cma": 0, "override": False})
        use_override = (year == 1) or cfg.get("override", False)

        h_jesus      = cfg["h_jesus"] * 10000       if use_override else carry_h_jesus
        h_deposit    = cfg.get("h_deposit", 0) * 10000 if use_override else carry_h_deposit
        h_cma        = cfg["h_cma"] * 10000         if use_override else carry_h_cma
        w_deposit    = cfg["w_deposit"] * 10000     if use_override else carry_w_deposit
        w_cma        = cfg["w_cma"] * 10000         if use_override else carry_w_cma

        h_jesus_monthly_balances = []
        h_deposit_init, h_cma_init, w_deposit_init, w_cma_init = h_deposit, h_cma, w_deposit, w_cma
        cal_year = start_date.year + year - 1

        for month in range(1, 13):
            h_jesus_monthly_balances.append(h_jesus)
            if year <= 2:
                if h_jesus >= monthly_tr_transfer:
                    h_jesus -= monthly_tr_transfer; h_tr_etf += monthly_tr_transfer
                else:
                    h_tr_etf += h_jesus; h_jesus = 0

            if w_cma >= monthly_living_cost: w_cma -= monthly_living_cost
            else: h_cma -= monthly_living_cost

            # 정산 이후 캘린더 연산 전진
            m = current_running_date.month + 1
            y_offset = current_running_date.year
            if m > 12: m = 1; y_offset += 1
            current_running_date = datetime(y_offset, m, min(current_running_date.day, 28))

            if year == setup_year_num:
                stamp_text = current_running_date.strftime("%Y년 %m월 %d일")
                monthly_records.append({
                    "📅 정산 기준일": stamp_text,
                    "👨남편 주식예수금": int(h_jesus / 10000), "👨남편 정기예금": int(h_deposit / 10000),
                    "👨남편 CMA잔액(가용현금)": int(h_cma / 10000), "👨남편 지수TR ETF(잠금)": int(h_tr_etf / 10000),
                    "👩아내 정기예금": int(max(0, w_deposit) / 10000), "👩아내 CMA": int(max(0, w_cma) / 10000),
                    "👪부부 찐 가용자산(CMA+예금)": int((h_jesus + h_deposit + h_cma + max(0, w_deposit) + max(0, w_cma)) / 10000)
                })

        avg_h_jesus = sum(h_jesus_monthly_balances) / 12
        h_jesus_interest   = avg_h_jesus * jesus_rate
        h_dep_interest_val = h_deposit_init * deposit_rate
        h_cma_interest     = h_cma_init * cma_rate
        h_interest_pre     = h_jesus_interest + h_dep_interest_val + h_cma_interest

        w_old_dep_interest = w_deposit_init * deposit_rate
        w_cma_interest_val = (w_cma_init * cma_rate) / 2
        w_interest_pre     = w_old_dep_interest + w_cma_interest_val

        h_interest_post = int(h_interest_pre * (1 - tax_rate))
        w_interest_post = int(w_interest_pre * (1 - tax_rate))
        total_income_post = h_interest_post + w_interest_post

        if year <= 5: w_cma += total_income_post
        else: h_cma += total_income_post

        h_tr_etf = int(h_tr_etf * (1 + tr_etf_rate))
        deficit  = int(living_cost_annual - total_income_post)
        leftover = deposit_unit - deficit if w_deposit >= deposit_unit else 0

        if w_deposit >= deposit_unit: w_deposit -= deposit_unit
        w_cma += leftover

        carry_h_jesus, carry_h_deposit, carry_h_cma = h_jesus, h_deposit, h_cma
        carry_w_deposit, carry_w_cma = w_deposit, w_cma

        yearly_records.append({
            "연차": f"{year}년차({cal_year}년)", "남편세전": h_interest_pre,
            "남편예수금이차": h_jesus_interest, "남편정기예금이자": h_dep_interest_val, "남편CMA이자": h_cma_interest,
            "아내세전": w_interest_pre, "아내기존예금이차": w_old_dep_interest, "아내CMA이자": w_cma_interest_val,
            "부부세전합계": h_interest_pre + w_interest_pre, "세후이자": total_income_post, "부족분": deficit, "잔돈": leftover,
            "남편예수금_avg": avg_h_jesus, "남편예금_val": h_deposit_init, "남편CMA_val": h_cma_init,
            "아내예금_val": w_deposit_init, "아내CMA_val": w_cma_init
        })

    # --- 결과 출력 ---
    st.header(f"🏁 3단계: [{setup_year_num}년차 ({start_date.year + setup_year_num - 1}년 정산)] 집중 분석 리포트")
    tab_yearly, tab_monthly = st.tabs(["📅 건보료선 정밀 검증 보고서", "📊 월별 주머니 잔고 현황 (해당 연차 전용)"])
    target_res = yearly_records[setup_year_num - 1]

    with tab_yearly:
        st.subheader(f"🧾 이자 계산 상세 명세 ({start_date.year + setup_year_num - 1}년 기준)")
        h_interest_table = pd.DataFrame([
            {"명의": "👨 남편", "자산 주머니": "주식 예수금 (월할평균)", "원금": f"{int(target_res['남편예수금_avg']/10000):,} 만원", "적용이율": f"{jesus_rate*100:.1f}%", "발생이자 (세전)": f"{int(target_res['남편예수금이차']/10000):,} 만원"},
            {"명의": "👨 남편", "자산 주머니": "정기예금", "원금": f"{int(target_res['남편예금_val']/10000):,} 만원", "적용이율": f"{deposit_rate*100:.1f}%", "발생이자 (세전)": f"{int(target_res['남편정기예금이자']/10000):,} 만원"},
            {"명의": "👨 남편", "자산 주머니": "대신증권 CMA", "원금": f"{int(target_res['남편CMA_val']/10000):,} 만원", "적용이율": f"{cma_rate*100:.1f}%", "발생이자 (세전)": f"{int(target_res['남편CMA이자']/10000):,} 만원"},
            {"명의": "👩 아내", "자산 주머니": "정기예금", "원금": f"{int(target_res['아내예금_val']/10000):,} 만원", "적용이율": f"{deposit_rate*100:.1f}%", "발생이자 (세전)": f"{int(target_res['아내기존예금이차']/10000):,} 만원"},
            {"명의": "👩 아내", "자산 주머니": "대신증권 CMA (평균잔고)", "원금": f"{int(target_res['아내CMA_val']/10000):,} 만원", "적용이율": f"{cma_rate*100:.1f}% (평균반영)", "발생이자 (세전)": f"{int(target_res['아내CMA이자']/10000):,} 만원"}
        ])
        st.table(h_interest_table)

        col_h, col_w = st.columns(2)
        with col_h:
            st.markdown("#### 👨 남편 총평")
            st.metric("남편 세전 금융소득 합계", f"{int(target_res['남편세전']/10000):,} 만원")
            h_margin = 10000000 - target_res['남편세전']
            if h_margin > 0: st.success(f"🛡️ 건보료 안전지대 (마지노선까지 {int(h_margin/10000):,}만원 여유)")
            else: st.error("🚨 경고: 1,000만원 초과! 건보료 부과 대상")
        with col_w:
            st.markdown("#### 👩 아내 총평")
            st.metric("아내 세전 금융소득 합계", f"{int(target_res['아내세전']/10000):,} 만원")
            w_margin = 20000000 - target_res['아내세전']
            if w_margin > 0: st.success(f"🛡️ 종합과세 안전지대 (마지노선까지 {int(w_margin/10000):,}만원 여유)")
            else: st.error("🚨 경고: 2,000만원 초과! 종합과세 대상")

        st.markdown("---")
        st.subheader("🧾 부부 합산 세후 이자 산출 명세서")
        receipt_df = pd.DataFrame([
            {"항목 명세": "👨 남편 명의 세전 금융소득 합계", "금액": f"{int(target_res['남편세전']/10000):,} 만원"},
            {"항목 명세": "👩 아내 명의 세전 금융소득 합계", "금액": f"{int(target_res['아내세전']/10000):,} 만원"},
            {"항목 명세": "📊 부부 세전 소득 합계 (A)", "금액": f"{int(target_res['부부세전합계']/10000):,} 만원"},
            {"항목 명세": "💸 이자소득세 원천징수 (A × 15.4%)", "금액": f"- {int((target_res['부부세전합계']*0.154)/10000):,} 만원"},
            {"항목 명세": "👪 부부 최종 세후 이자 수령액", "금액": f"{int(target_res['세후이자']/10000):,} 만원"}
        ])
        st.table(receipt_df)

        st.markdown("---")
        col_tot1, col_tot2, col_tot3 = st.columns(3)
        with col_tot1: st.metric("👪 부부 합산 세후 이자", f"{int(target_res['세후이자']/10000):,} 만원")
        with col_tot2: st.warning(f"🛒 연간 생활비 구멍: {int(target_res['부족분']/10000):,} 만원")
        with col_tot3:
            st.success(f"💰 통장 깨고 남은 알짜 잔돈(자동 저축): {int(target_res['잔돈']/10000):,} 만원")
            st.caption("※ 연말 잔돈은 자동으로 아내 CMA 통장으로 전액 이양됩니다.")

    with tab_monthly:
        st.subheader(f"🗓️ 선택 연차 정산 달력 기준 잔고 흐름 보고서")
        df_monthly = pd.DataFrame(monthly_records)
        st.dataframe(
            df_monthly.set_index("📅 정산 기준일").style.format({
                "👨남편 주식예수금": "{:,} 만원", "👨남편 정기예금": "{:,} 만원",
                "👨남편 CMA잔액(가용현금)": "{:,} 만원", "👨남편 지수TR ETF(잠금)": "{:,} 만원",
                "👩아내 정기예금": "{:,} 만원", "👩아내 CMA": "{:,} 만원",
                "👪부부 찐 가용자산(CMA+예금)": "{:,} 만원"
            }), use_container_width=True, height=450
        )
