# ------------------------------------------------------------
# 🚗 CO2 차량 연비 분석 대시보드 (Streamlit 버전 - 파일 자동 로드)
# ------------------------------------------------------------
# 실행 방법:
# 1️⃣ 이 파일을 co2_dashboard.py 로 저장
# 2️⃣ 같은 폴더에 co2.csv 파일을 넣기
# 3️⃣ 터미널에서 실행: streamlit run co2_dashboard.py
# ------------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
from matplotlib import rc


# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지

# 깃허브 리눅스 기준
if platform.system() == 'Linux':
    fontname = './NanumGothic.ttf'
    font_files = fm.findSystemFonts(fontpaths=fontname)
    fm.fontManager.addfont(fontname)
    fm._load_fontmanager(try_read_cache=False)
    rc('font', family='NanumGothic')

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Streamlit 기본 설정
st.set_page_config(page_title="CO2 차량 연비 분석 대시보드", layout="wide")
st.title("🚗 CO2 차량 연비 분석 대시보드")
st.markdown("이 앱은 차량 데이터를 기반으로 **연비 및 CO₂ 배출량**을 시각적으로 분석합니다.")

# ------------------------------------------------------------
# 1. CSV 파일 자동 불러오기
# ------------------------------------------------------------
file_path = "co2.csv"

if not os.path.exists(file_path):
    st.error("❌ co2.csv 파일이 현재 폴더에 없습니다. 같은 폴더에 co2.csv 파일을 넣어주세요.")
    st.stop()

# 데이터 로드
df = pd.read_csv(file_path)
st.success("✅ 'co2.csv' 파일이 성공적으로 불러와졌습니다!")

# ------------------------------------------------------------
# 2. 기본 정보 표시
# ------------------------------------------------------------
with st.expander("📄 데이터 미리보기"):
    st.dataframe(df.head())

with st.expander("ℹ️ 데이터 기본 정보"):
    st.write(f"행 수: {df.shape[0]}, 열 수: {df.shape[1]}")
    st.write("열 이름:", list(df.columns))
    st.write(df.describe())

# ------------------------------------------------------------
# 3. 기본 변수 설정
# ------------------------------------------------------------
numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
target_col = "Fuel Consumption Comb (L/100 km)"

st.sidebar.header("🔧 분석 설정")
st.sidebar.write("분석 기준을 선택하세요.")

# 사용자 설정
x_option = st.sidebar.selectbox("분석 기준 (X축)", ["Vehicle Class", "Engine Size(L)", "Cylinders", "Fuel Type"])
chart_type = st.sidebar.radio("그래프 종류 선택", ["막대그래프", "박스플롯", "산점도"], horizontal=True)

# ------------------------------------------------------------
# 4. 그룹별 평균 연비 분석
# ------------------------------------------------------------
st.header(f"📊 {x_option}별 연비 분석")

if x_option in df.columns:
    group_data = df.groupby(x_option)[target_col].mean().reset_index().sort_values(target_col)

    plt.figure(figsize=(10, 5))
    if chart_type == "막대그래프":
        sns.barplot(data=group_data, x=x_option, y=target_col, palette="Set2")
    elif chart_type == "박스플롯":
        sns.boxplot(data=df, x=x_option, y=target_col, palette="Pastel1")
    elif chart_type == "산점도":
        sns.scatterplot(data=df, x=x_option, y=target_col, alpha=0.6)

    plt.xticks(rotation=45)
    plt.title(f"{x_option}별 평균 연비 ({target_col})")
    st.pyplot(plt)

    with st.expander("📋 평균 연비 요약표 보기"):
        st.dataframe(group_data)

# ------------------------------------------------------------
# 5. 상관관계 분석
# ------------------------------------------------------------
st.header("📈 수치형 변수 간 상관관계")
corr = df[numeric_cols].corr()

plt.figure(figsize=(10, 6))
sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
plt.title("상관관계 히트맵")
st.pyplot(plt)

# ------------------------------------------------------------
# 6. 맞춤형 데이터 필터
# ------------------------------------------------------------
st.header("🎯 맞춤형 데이터 필터링")
filter_col = st.selectbox("필터링할 기준 선택", cat_cols)
unique_values = df[filter_col].unique()
selected_values = st.multiselect(f"{filter_col}에서 선택", unique_values)

if selected_values:
    filtered_df = df[df[filter_col].isin(selected_values)]
    st.write(f"선택된 데이터 ({len(filtered_df)}개 항목):")
    st.dataframe(filtered_df.head())

    plt.figure(figsize=(10, 5))
    sns.barplot(data=filtered_df, x=x_option, y=target_col, estimator="mean", palette="Set3", errorbar=None)
    plt.xticks(rotation=45)
    plt.title(f"{filter_col}별 {x_option} 평균 연비 비교")
    st.pyplot(plt)

# ------------------------------------------------------------
# 7. 데이터 다운로드
# ------------------------------------------------------------
st.header("💾 분석 결과 다운로드")
csv_export = group_data.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 그룹별 평균 연비 CSV 다운로드",
    data=csv_export,
    file_name="grouped_fuel_efficiency.csv",
    mime="text/csv",
)

# ------------------------------------------------------------
# 8. 푸터
# ------------------------------------------------------------
st.markdown("---")
st.markdown("🧠 *개발자: 한규찬의 데이터 분석 프로젝트 (powered by Streamlit)*")
