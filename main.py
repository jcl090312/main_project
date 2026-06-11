
---

## 📄 main.py

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, date

# ===================== 기본 설정 =====================
st.set_page_config(page_title="수학 학습 & 건강 관리", page_icon="📚", layout="wide")

DATA_DIR = "data"
PROBLEMS_FILE = os.path.join(DATA_DIR, "problems.csv")
STUDY_FILE = os.path.join(DATA_DIR, "study.csv")

# 데이터 폴더 생성
os.makedirs(DATA_DIR, exist_ok=True)


# ===================== 데이터 로드/저장 함수 =====================
def load_problems():
    if os.path.exists(PROBLEMS_FILE):
        return pd.read_csv(PROBLEMS_FILE)
    else:
        return pd.DataFrame(columns=[
            "날짜", "단원", "난이도", "문제내용", "정답여부", "오답메모"
        ])


def save_problems(df):
    df.to_csv(PROBLEMS_FILE, index=False)


def load_study():
    if os.path.exists(STUDY_FILE):
        return pd.read_csv(STUDY_FILE)
    else:
        return pd.DataFrame(columns=[
            "날짜", "수면시간", "집중시간"
        ])


def save_study(df):
    df.to_csv(STUDY_FILE, index=False)


# ===================== 사이드바 메뉴 =====================
st.sidebar.title("📚 메뉴")
menu = st.sidebar.radio(
    "이동할 페이지를 선택하세요",
    ["🏠 홈", "✏️ 문제풀이 / 오답노트", "📊 정답률 분석",
     "🎯 취약점 분석", "💪 건강 관리"]
)


# ===================== 1. 홈 =====================
if menu == "🏠 홈":
    st.title("📚 수학 학습 & 건강 관리 도우미")
    st.markdown("---")
    st.write("당곡고등학교 학생을 위한 학습 관리 웹앱입니다. 👋")

    problems = load_problems()
    study = load_study()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📝 총 푼 문제 수", f"{len(problems)} 문제")
    with col2:
        if len(problems) > 0:
            rate = (problems["정답여부"] == "정답").mean() * 100
            st.metric("✅ 전체 정답률", f"{rate:.1f} %")
        else:
            st.metric("✅ 전체 정답률", "0 %")
    with col3:
        if len(study) > 0:
            total = study["집중시간"].sum()
            st.metric("⏰ 총 집중 시간", f"{total:.1f} 시간")
        else:
            st.metric("⏰ 총 집중 시간", "0 시간")

    st.markdown("---")
    st.subheader("📌 사용 안내")
    st.markdown("""
    - **✏️ 문제풀이 / 오답노트**: 푼 문제를 기록하고 오답을 정리해요.
    - **📊 정답률 분석**: 단원별 정답률과 학습 추이를 확인해요.
    - **🎯 취약점 분석**: 약한 단원을 찾아 집중 학습 계획을 세워요.
    - **💪 건강 관리**: 눈 휴식, 스트레칭, 수면/집중 시간을 관리해요.
    """)


# ===================== 2. 문제풀이 / 오답노트 =====================
elif menu == "✏️ 문제풀이 / 오답노트":
    st.title("✏️ 문제풀이 / 오답노트")
    st.markdown("---")

    problems = load_problems()

    # 문제 입력
    st.subheader("➕ 문제 기록 추가")
    with st.form("problem_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            input_date = st.date_input("날짜", value=date.today())
            unit = st.selectbox("단원", [
                "수와 연산", "문자와 식", "함수", "방정식과 부등식",
                "도형(기하)", "삼각함수", "미분", "적분",
                "확률과 통계", "수열", "기타"
            ])
        with col2:
            difficulty = st.selectbox("난이도", ["쉬움", "보통", "어려움"])
            result = st.radio("정답 여부", ["정답", "오답"], horizontal=True)

        content = st.text_area("문제 내용 (간단히)", placeholder="예: 이차방정식의 근의 공식 문제")
        memo = st.text_area("오답 메모 (틀린 이유, 풀이 방법 등)",
                            placeholder="오답일 경우 왜 틀렸는지, 어떻게 풀어야 하는지 적어보세요!")

        submitted = st.form_submit_button("저장하기")
        if submitted:
            new_row = pd.DataFrame([{
                "날짜": str(input_date),
                "단원": unit,
                "난이도": difficulty,
                "문제내용": content,
                "정답여부": result,
                "오답메모": memo
            }])
            problems = pd.concat([problems, new_row], ignore_index=True)
            save_problems(problems)
            st.success("✅ 문제가 저장되었습니다!")

    st.markdown("---")

    # 오답노트 보기
    st.subheader("📒 오답노트 (틀린 문제만 보기)")
    wrong = problems[problems["정답여부"] == "오답"]
    if len(wrong) > 0:
        for idx, row in wrong.iterrows():
            with st.expander(f"[{row['단원']}] {row['문제내용']}  ({row['날짜']})"):
                st.write(f"**난이도:** {row['난이도']}")
                st.write(f"**오답 메모:** {row['오답메모']}")
    else:
        st.info("아직 오답이 없어요! 👍")

    st.markdown("---")

    # 전체 기록 보기 및 삭제
    st.subheader("📋 전체 기록")
    if len(problems) > 0:
        st.dataframe(problems, use_container_width=True)

        # 삭제 기능
        del_idx = st.number_input(
            "삭제할 행 번호 (맨 왼쪽 인덱스)", min_value=0,
            max_value=len(problems) - 1, step=1
        )
        if st.button("선택한 기록 삭제"):
            problems = problems.drop(del_idx).reset_index(drop=True)
            save_problems(problems)
            st.success("삭제되었습니다. 새로고침 해주세요.")
            st.rerun()

        # CSV 다운로드 (백업용)
        csv = problems.to_csv(index=False).encode("utf-8-sig")
        st.download_button("💾 기록 CSV 다운로드", csv,
                           "problems_backup.csv", "text/csv")
    else:
        st.info("아직 기록이 없어요. 문제를 추가해보세요!")


# ===================== 3. 정답률 분석 =====================
elif menu == "📊 정답률 분석":
    st.title("📊 오답 및 정답률 분석")
    st.markdown("---")

    problems = load_problems()

    if len(problems) == 0:
        st.info("아직 데이터가 없어요. 문제를 먼저 기록해주세요!")
    else:
        # 전체 정답/오답 비율
        st.subheader("전체 정답 / 오답 비율")
        result_count = problems["정답여부"].value_counts().reset_index()
        result_count.columns = ["결과", "개수"]
        fig1 = px.pie(result_count, names="결과", values="개수",
                      color="결과",
                      color_discrete_map={"정답": "#4CAF50", "오답": "#F44336"})
        st.plotly_chart(fig1, use_container_width=True)

        # 단원별 정답률
        st.subheader("단원별 정답률")
        unit_stats = problems.groupby("단원")["정답여부"].apply(
            lambda x: (x == "정답").mean() * 100
        ).reset_index()
        unit_stats.columns = ["단원", "정답률"]
        fig2 = px.bar(unit_stats, x="단원", y="정답률",
                      color="정답률", color_continuous_scale="RdYlGn",
                      text=unit_stats["정답률"].round(1))
        fig2.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig2, use_container_width=True)

        # 난이도별 정답률
        st.subheader("난이도별 정답률")
        diff_stats = problems.groupby("난이도")["정답여부"].apply(
            lambda x: (x == "정답").mean() * 100
        ).reset_index()
        diff_stats.columns = ["난이도", "정답률"]
        fig3 = px.bar(diff_stats, x="난이도", y="정답률",
                      color="난이도",
                      text=diff_stats["정답률"].round(1))
        fig3.update_layout(yaxis_range=[0, 100])
        st.plotly_chart(fig3, use_container_width=True)

        # 날짜별 학습량 추이
        st.subheader("날짜별 푼 문제 수 추이")
        date_count = problems.groupby("날짜").size().reset_index(name="문제수")
        fig4 = px.line(date_count, x="날짜", y="문제수", markers=True)
        st.plotly_chart(fig4, use_container_width=True)


# ===================== 4. 취약점 분석 =====================
elif menu == "🎯 취약점 분석":
    st.title("🎯 취약점 분석")
    st.markdown("---")

    problems = load_problems()

    if len(problems) == 0:
        st.info("아직 데이터가 없어요. 문제를 먼저 기록해주세요!")
    else:
        # 단원별 통계 계산
        stats = problems.groupby("단원").agg(
            총문제수=("정답여부", "count"),
            정답수=("정답여부", lambda x: (x == "정답").sum())
        ).reset_index()
        stats["정답률"] = (stats["정답수"] / stats["총문제수"] * 100).round(1)
        stats = stats.sort_values("정답률")

        st.subheader("📉 정답률이 낮은 단원 (취약 단원)")
        st.dataframe(stats, use_container_width=True)

        # 취약 단원 추천 (정답률 60% 미만)
        weak = stats[stats["정답률"] < 60]
        st.markdown("---")
        st.subheader("💡 집중 학습 추천")
        if len(weak) > 0:
            for _, row in weak.iterrows():
                st.warning(
                    f"**{row['단원']}** 단원의 정답률이 "
                    f"**{row['정답률']}%** 입니다. 복습이 필요해요! 📖"
                )
        else:
            st.success("모든 단원의 정답률이 60% 이상이에요! 아주 잘하고 있어요 🎉")

        # 가장 약한 단원 강조
        if len(stats) > 0:
            worst = stats.iloc[0]
            st.markdown("---")
            st.info(
                f"🔥 **가장 취약한 단원은 '{worst['단원']}'** 입니다. "
                f"(정답률 {worst['정답률']}%)\n\n"
                f"이 단원의 오답노트를 다시 확인하고, 비슷한 문제를 더 풀어보세요!"
            )


# ===================== 5. 건강 관리 =====================
elif menu == "💪 건강 관리":
    st.title("💪 건강 관리")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["👀 휴식 알림", "📝 수면/집중 기록", "📈 건강 통계"])

    # ----- 탭1: 눈 휴식 & 스트레칭 알림 -----
    with tab1:
        st.subheader("👀 눈 휴식 (20-20-20 규칙)")
        st.markdown("""
        **20-20-20 규칙**: 20분마다 → 20피트(약 6m) 떨어진 곳을 → 20초간 바라보세요!
        눈의 피로를 줄여줍니다. 👁️
        """)

        if st.button("👁️ 눈 휴식 타이머 안내 보기"):
            st.success("✅ 지금 화면에서 잠시 눈을 떼고, 창밖 먼 곳을 20초간 바라보세요!")
            st.balloons()

        st.markdown("---")
        st.subheader("🤸 스트레칭 알림")
        st.markdown("""
        오래 앉아있으면 목과 어깨가 뭉쳐요. 1시간에 한 번씩 일어나서 스트레칭 해요!
        """)
        stretch_list = [
            "🙆 목을 천천히 좌우로 돌리기 (각 5초)",
            "🙆 어깨를 위아래로 으쓱하기 (10회)",
            "🙆 양손 깍지 끼고 위로 쭉 뻗기 (10초)",
            "🙆 허리를 좌우로 비틀기 (각 10초)",
            "🙆 손목/발목 돌리기 (각 10회)"
        ]
        if st.button("🤸 오늘의 스트레칭 추천받기"):
            import random
            st.info("**오늘의 스트레칭:**\n\n" + random.choice(stretch_list))

    # ----- 탭2: 수면/집중 시간 기록 -----
    with tab2:
        st.subheader("📝 오늘의 수면 & 집중 시간 기록")
        study = load_study()

        with st.form("study_form", clear_on_submit=True):
            input_date = st.date_input("날짜", value=date.today())
            sleep_time = st.slider("수면 시간 (시간)", 0.0, 12.0, 7.0, 0.5)
            focus_time = st.slider("집중(공부) 시간 (시간)", 0.0, 16.0, 3.0, 0.5)
            submitted = st.form_submit_button("저장하기")
            if submitted:
                new_row = pd.DataFrame([{
                    "날짜": str(input_date),
                    "수면시간": sleep_time,
                    "집중시간": focus_time
                }])
                study = pd.concat([study, new_row], ignore_index=True)
                save_study(study)
                st.success("✅ 기록이 저장되었습니다!")

                # 간단한 피드백
                if sleep_time < 6:
                    st.warning("⚠️ 수면 시간이 부족해요. 충분히 자야 집중력이 올라가요!")
                elif sleep_time >= 7:
                    st.info("👍 적절한 수면 시간이에요!")

        st.markdown("---")
        st.subheader("📋 기록 목록")
        if len(study) > 0:
            st.dataframe(study, use_container_width=True)
            csv = study.to_csv(index=False).encode("utf-8-sig")
            st.download_button("💾 건강 기록 CSV 다운로드", csv,
                               "study_backup.csv", "text/csv")
        else:
            st.info("아직 기록이 없어요.")

    # ----- 탭3: 건강 통계 -----
    with tab3:
        st.subheader("📈 수면 & 집중 시간 통계")
        study = load_study()

        if len(study) == 0:
            st.info("아직 데이터가 없어요. 기록을 먼저 해주세요!")
        else:
            col1, col2 = st.columns(2)
            with col1:
                avg_sleep = study["수면시간"].mean()
                st.metric("평균 수면 시간", f"{avg_sleep:.1f} 시간")
            with col2:
                avg_focus = study["집중시간"].mean()
                st.metric("평균 집중 시간", f"{avg_focus:.1f} 시간")

            # 수면 시간 추이
            fig_sleep = px.line(study, x="날짜", y="수면시간",
                                markers=True, title="수면 시간 추이")
            st.plotly_chart(fig_sleep, use_container_width=True)

            # 집중 시간 추이
            fig_focus = px.bar(study, x="날짜", y="집중시간",
                               title="집중 시간 추이")
            st.plotly_chart(fig_focus, use_container_width=True)
