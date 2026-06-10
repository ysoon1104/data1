import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="봄·가을이 짧아지고 있는가?",
    layout="wide"
)

st.title("🌸🍂 봄·가을이 정말 짧아지고 있는가?")
st.markdown("서울 기온 관측자료를 이용한 장기 기후변화 분석")

# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------

FILE_NAME = "ta_20260601093156.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(FILE_NAME)

    df["날짜"] = pd.to_datetime(df["날짜"])
    df["연도"] = df["날짜"].dt.year

    return df

df = load_data()

st.success(f"데이터 로드 완료 : {len(df):,}일")

# --------------------------------------------------
# 계절 정의
# --------------------------------------------------
#
# 봄 : 평균기온 5~20℃
# 여름 : 20℃ 초과
# 가을 : 5~20℃
# 겨울 : 5℃ 미만
#
# 봄 = 2~6월 구간의 온화한 날
# 가을 = 8~11월 구간의 온화한 날
#
# --------------------------------------------------

def calc_season_length(year_df):

    spring = year_df[
        (year_df["날짜"].dt.month >= 2) &
        (year_df["날짜"].dt.month <= 6) &
        (year_df["평균기온(℃)"] >= 5) &
        (year_df["평균기온(℃)"] <= 20)
    ]

    autumn = year_df[
        (year_df["날짜"].dt.month >= 8) &
        (year_df["날짜"].dt.month <= 11) &
        (year_df["평균기온(℃)"] >= 5) &
        (year_df["평균기온(℃)"] <= 20)
    ]

    return len(spring), len(autumn)

records = []

for year, g in df.groupby("연도"):

    spring_days, autumn_days = calc_season_length(g)

    records.append({
        "연도": year,
        "봄일수": spring_days,
        "가을일수": autumn_days,
        "봄가을합계": spring_days + autumn_days
    })

season_df = pd.DataFrame(records)

# --------------------------------------------------
# 회귀분석
# --------------------------------------------------

def slope(x, y):

    x_mean = x.mean()
    y_mean = y.mean()

    numerator = ((x - x_mean) * (y - y_mean)).sum()
    denominator = ((x - x_mean) ** 2).sum()

    return numerator / denominator

trend = slope(
    season_df["연도"],
    season_df["봄가을합계"]
)

# --------------------------------------------------
# 기본 통계
# --------------------------------------------------

early = season_df.head(30)
late = season_df.tail(30)

early_mean = early["봄가을합계"].mean()
late_mean = late["봄가을합계"].mean()

difference = late_mean - early_mean

# --------------------------------------------------
# 결과 표시
# --------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "초기 30년 평균",
        f"{early_mean:.1f}일"
    )

with col2:
    st.metric(
        "최근 30년 평균",
        f"{late_mean:.1f}일"
    )

with col3:
    st.metric(
        "변화량",
        f"{difference:.1f}일"
    )

st.subheader("연도별 봄 길이")
st.line_chart(
    season_df.set_index("연도")["봄일수"]
)

st.subheader("연도별 가을 길이")
st.line_chart(
    season_df.set_index("연도")["가을일수"]
)

st.subheader("연도별 봄+가을 총 길이")
st.line_chart(
    season_df.set_index("연도")["봄가을합계"]
)

st.subheader("초기 30년 vs 최근 30년")

compare = pd.DataFrame({
    "구간": ["초기30년", "최근30년"],
    "평균일수": [early_mean, late_mean]
})

st.bar_chart(
    compare.set_index("구간")
)

# --------------------------------------------------
# 해석
# --------------------------------------------------

st.header("통계적 해석")

if trend < 0:
    st.error(
        f"""
        장기 추세 기울기 = {trend:.3f}

        음수 기울기가 나타났습니다.

        이는 시간이 지날수록 봄·가을 길이가 감소하는 방향의
        장기 추세가 존재함을 의미합니다.
        """
    )
else:
    st.success(
        f"""
        장기 추세 기울기 = {trend:.3f}

        감소 추세는 관찰되지 않습니다.
        """
    )

if difference < 0:
    st.warning(
        f"""
        최근 30년의 봄·가을 평균 길이는

        과거 30년보다 {-difference:.1f}일 짧습니다.

        이는 봄과 가을이 점차 짧아지고
        여름·겨울이 길어지는 기후변화 가설을 지지합니다.
        """
    )
else:
    st.info(
        """
        최근 기간에서 봄·가을 단축 현상이
        뚜렷하게 나타나지 않습니다.
        """
    )

st.header("탐구 결론")

st.markdown(
"""
본 분석은 1907년 이후 서울 기온 자료를 이용하여
봄과 가을의 길이를 계산하였다.

봄·가을을 평균기온 5~20℃ 범위의 온화한 계절로 정의하고,
연도별 지속일수를 분석하였다.

연도별 추세와 과거·최근 기간 비교를 통해
봄과 가을의 길이가 실제로 감소하는지 확인할 수 있다.

이는 지구온난화에 따른 계절 구조 변화 연구의
기초 자료로 활용될 수 있다.
"""
)

st.dataframe(season_df, use_container_width=True)
