
---

## 📁 파일 3: `main.py`

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PISA 국제 학업성취도 비교",
    page_icon="🌍",
    layout="wide",
)

# 과목 영어 → 한글 매핑
SUBJECT_KR = {
    "mathematics": "수학",
    "reading": "읽기",
    "science": "과학",
}
SUBJECT_EN = {v: k for k, v in SUBJECT_KR.items()}  # 한글 → 영어


# ─────────────────────────────────────────────
# 데이터 불러오기 (캐싱으로 속도 향상)
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("pisa-scores.csv")
    # 결측치(점수 없는 행) 제거
    df = df.dropna(subset=["mean_score"])
    # 과목명을 한글로 추가
    df["subject_kr"] = df["subject"].map(SUBJECT_KR)
    return df


df = load_data()

# ─────────────────────────────────────────────
# 제목
# ─────────────────────────────────────────────
st.title("🌍 PISA 국제 학업성취도 비교 대시보드")
st.caption("OECD PISA 데이터 (2000~2018) | 수학 · 읽기 · 과학")

# ─────────────────────────────────────────────
# 사이드바: 분석 메뉴 선택
# ─────────────────────────────────────────────
st.sidebar.header("📊 분석 메뉴")
menu = st.sidebar.radio(
    "원하는 분석을 선택하세요",
    [
        "1️⃣ 국가별 시계열 추이",
        "2️⃣ 다국가 비교",
        "3️⃣ 과목별 강약점 분석",
        "4️⃣ OECD 평균 대비",
        "5️⃣ 연도별 순위표",
        "6️⃣ 과목 간 상관관계",
    ],
)

# 국가 목록 (OECD members 제외한 실제 국가만, 정렬)
all_countries = sorted(df["country_name"].unique())
real_countries = [c for c in all_countries if c != "OECD members"]


# ─────────────────────────────────────────────
# 1. 국가별 시계열 추이
# ─────────────────────────────────────────────
if menu.startswith("1"):
    st.header("1️⃣ 국가별 시계열 추이")
    st.write("선택한 국가의 연도별 점수 변화를 과목별로 확인합니다.")

    country = st.selectbox("국가를 선택하세요", real_countries,
                           index=real_countries.index("Korea, Rep.")
                           if "Korea, Rep." in real_countries else 0)

    cdf = df[df["country_name"] == country].sort_values("year")

    if cdf.empty:
        st.warning("해당 국가의 데이터가 없습니다.")
    else:
        fig = px.line(
            cdf,
            x="year",
            y="mean_score",
            color="subject_kr",
            markers=True,
            labels={"year": "연도", "mean_score": "평균 점수", "subject_kr": "과목"},
            title=f"{country}의 연도별 PISA 점수 추이",
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # 데이터 표
        with st.expander("📋 원본 데이터 보기"):
            pivot = cdf.pivot_table(index="year", columns="subject_kr",
                                    values="mean_score")
            st.dataframe(pivot, use_container_width=True)


# ─────────────────────────────────────────────
# 2. 다국가 비교
# ─────────────────────────────────────────────
elif menu.startswith("2"):
    st.header("2️⃣ 다국가 비교")
    st.write("여러 국가를 선택하여 특정 과목의 점수를 비교합니다.")

    col1, col2 = st.columns(2)
    with col1:
        subject_kr = st.selectbox("과목 선택", list(SUBJECT_KR.values()))
    with col2:
        default = [c for c in ["Korea, Rep.", "Japan", "Finland", "United States"]
                   if c in real_countries]
        countries = st.multiselect("비교할 국가 선택 (여러 개 가능)",
                                    real_countries, default=default)

    subject_en = SUBJECT_EN[subject_kr]

    if not countries:
        st.info("👆 비교할 국가를 한 개 이상 선택해주세요.")
    else:
        sub = df[(df["subject"] == subject_en) &
                 (df["country_name"].isin(countries))].sort_values("year")
        fig = px.line(
            sub, x="year", y="mean_score", color="country_name",
            markers=True,
            labels={"year": "연도", "mean_score": "평균 점수",
                    "country_name": "국가"},
            title=f"국가별 {subject_kr} 점수 비교",
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 3. 과목별 강약점 분석
# ─────────────────────────────────────────────
elif menu.startswith("3"):
    st.header("3️⃣ 과목별 강약점 분석")
    st.write("선택한 국가의 특정 연도 3과목 점수를 비교하여 강점과 약점을 파악합니다.")

    col1, col2 = st.columns(2)
    with col1:
        country = st.selectbox("국가 선택", real_countries,
                               index=real_countries.index("Korea, Rep.")
                               if "Korea, Rep." in real_countries else 0)
    with col2:
        years = sorted(df[df["country_name"] == country]["year"].unique())
        if not years:
            st.warning("데이터가 없습니다.")
            st.stop()
        year = st.selectbox("연도 선택", years, index=len(years) - 1)

    cdf = df[(df["country_name"] == country) & (df["year"] == year)]

    if cdf.empty:
        st.warning("해당 연도의 데이터가 없습니다.")
    else:
        fig = px.bar(
            cdf, x="subject_kr", y="mean_score", color="subject_kr",
            text="mean_score",
            labels={"subject_kr": "과목", "mean_score": "평균 점수"},
            title=f"{country} ({year}년) 과목별 점수",
        )
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

        # 강점 / 약점 안내
        best = cdf.loc[cdf["mean_score"].idxmax()]
        worst = cdf.loc[cdf["mean_score"].idxmin()]
        c1, c2 = st.columns(2)
        c1.metric("💪 가장 강한 과목", best["subject_kr"],
                  f"{best['mean_score']:.1f}점")
        c2.metric("📉 가장 약한 과목", worst["subject_kr"],
                  f"{worst['mean_score']:.1f}점")


# ─────────────────────────────────────────────
# 4. OECD 평균 대비
# ─────────────────────────────────────────────
elif menu.startswith("4"):
    st.header("4️⃣ OECD 평균 대비 분석")
    st.write("선택한 국가의 점수를 OECD 평균(2018년 기준)과 비교합니다.")

    # OECD 평균 데이터 확인
    oecd = df[df["country_name"] == "OECD members"]
    if oecd.empty:
        st.warning("OECD 평균 데이터가 없습니다.")
    else:
        country = st.selectbox("비교할 국가 선택", real_countries,
                               index=real_countries.index("Korea, Rep.")
                               if "Korea, Rep." in real_countries else 0)

        # OECD 평균이 있는 연도(2018) 사용
        oecd_year = oecd["year"].unique()[0]
        st.caption(f"※ OECD 평균은 {oecd_year}년 기준입니다.")

        cdf = df[(df["country_name"] == country) & (df["year"] == oecd_year)]

        if cdf.empty:
            st.warning(f"{country}의 {oecd_year}년 데이터가 없습니다.")
        else:
            # 비교용 데이터 합치기
            compare = pd.concat([
                cdf[["subject_kr", "mean_score"]].assign(구분=country),
                oecd[["subject_kr", "mean_score"]].assign(구분="OECD 평균"),
            ])
            fig = px.bar(
                compare, x="subject_kr", y="mean_score", color="구분",
                barmode="group", text="mean_score",
                labels={"subject_kr": "과목", "mean_score": "평균 점수"},
                title=f"{country} vs OECD 평균 ({oecd_year}년)",
            )
            fig.update_traces(texttemplate="%{text:.0f}", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────
# 5. 연도별 순위표
# ─────────────────────────────────────────────
elif menu.startswith("5"):
    st.header("5️⃣ 연도별 순위표")
    st.write("특정 연도, 특정 과목의 국가별 순위를 확인합니다.")

    col1, col2, col3 = st.columns(3)
    with col1:
        subject_kr = st.selectbox("과목 선택", list(SUBJECT_KR.values()))
    with col2:
        years = sorted(df["year"].unique())
        year = st.selectbox("연도 선택", years, index=len(years) - 1)
    with col3:
        top_n = st.slider("상위 몇 개국?", 5, 30, 10)

    subject_en = SUBJECT_EN[subject_kr]
    rank = df[(df["subject"] == subject_en) & (df["year"] == year) &
              (df["country_name"] != "OECD members")].copy()
    rank = rank.sort_values("mean_score", ascending=False).head(top_n)
    rank["순위"] = range(1, len(rank) + 1)

    fig = px.bar(
        rank.sort_values("mean_score"),
        x="mean_score", y="country_name", orientation="h",
        text="mean_score",
        labels={"mean_score": "평균 점수", "country_name": "국가"},
        title=f"{year}년 {subject_kr} 상위 {top_n}개국",
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(height=max(400, top_n * 35))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("📋 순위표 보기"):
        show = rank[["순위", "country_name", "mean_score"]].rename(
            columns={"country_name": "국가", "mean_score": "점수"})
        st.dataframe(show, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────
# 6. 과목 간 상관관계
# ─────────────────────────────────────────────
elif menu.startswith("6"):
    st.header("6️⃣ 과목 간 상관관계")
    st.write("두 과목 점수 사이의 관계를 산점도로 탐구합니다. "
             "(점 하나 = 한 국가의 특정 연도)")

    col1, col2, col3 = st.columns(3)
    with col1:
        sub_x = st.selectbox("X축 과목", list(SUBJECT_KR.values()), index=0)
    with col2:
        sub_y = st.selectbox("Y축 과목", list(SUBJECT_KR.values()), index=1)
    with col3:
        years = sorted(df["year"].unique())
        year = st.selectbox("연도 선택", years, index=len(years) - 1)

    # 피벗으로 과목별 점수를 컬럼으로 변환
    ydf = df[(df["year"] == year) &
             (df["country_name"] != "OECD members")]
    pivot = ydf.pivot_table(index="country_name", columns="subject",
                            values="mean_score").reset_index()

    x_en, y_en = SUBJECT_EN[sub_x], SUBJECT_EN[sub_y]

    if x_en not in pivot.columns or y_en not in pivot.columns:
        st.warning("선택한 과목의 데이터가 부족합니다.")
    else:
        plot_df = pivot.dropna(subset=[x_en, y_en])
        fig = px.scatter(
            plot_df, x=x_en, y=y_en, hover_name="country_name",
            trendline="ols",  # 추세선
            labels={x_en: f"{sub_x} 점수", y_en: f"{sub_y} 점수"},
            title=f"{year}년 {sub_x} vs {sub_y} 점수 관계",
        )
        st.plotly_chart(fig, use_container_width=True)

        # 상관계수 계산
        corr = plot_df[x_en].corr(plot_df[y_en])
        st.metric("상관계수 (Correlation)", f"{corr:.3f}")
        if corr > 0.7:
            st.info("📈 두 과목은 **강한 양의 상관관계**를 보입니다. "
                    "한 과목을 잘하면 다른 과목도 잘하는 경향이 있어요.")
        elif corr > 0.4:
            st.info("📊 두 과목은 **중간 정도의 상관관계**를 보입니다.")
        else:
            st.info("📉 두 과목은 **약한 상관관계**를 보입니다.")


# ─────────────────────────────────────────────
# 하단 정보
# ─────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.caption("데이터 출처: OECD PISA\n\n당곡고등학교 데이터 분석 프로젝트")
