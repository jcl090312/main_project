# 🌍 PISA 국제 학업성취도 비교 대시보드

OECD PISA(국제 학업성취도 평가) 데이터를 활용하여 전 세계 국가들의
수학·읽기·과학 성취도를 비교·분석하는 Streamlit 웹 애플리케이션입니다.

## 📌 주요 기능

1. **국가별 시계열 추이**: 특정 국가의 연도별 점수 변화 확인
2. **다국가 비교**: 여러 국가를 동시에 비교
3. **과목별 강약점 분석**: 한 국가의 수학/읽기/과학 비교
4. **OECD 평균 대비 분석**: 기준선과 비교
5. **연도별 순위표**: 특정 연도의 국가 랭킹
6. **과목 간 상관관계**: 산점도를 통한 데이터 탐구

## 🗂 데이터 정보

- 출처: PISA (Programme for International Student Assessment)
- 기간: 2000년 ~ 2018년 (3년 주기)
- 과목: 수학(mathematics), 읽기(reading), 과학(science)
- 컬럼: country_name, country_code, year, subject, mean_score

## ⚠️ 데이터 특이사항

- 일부 국가/연도의 특정 과목 점수가 누락되어 있음 (결측치 처리됨)
- `OECD members`는 국가가 아닌 평균 집계 단위 → 기준선으로 활용
- 국가마다 참여 연도가 다름

## 🚀 실행 방법

```bash
# 1. 라이브러리 설치
pip install -r requirements.txt

# 2. 앱 실행 (pisa-scores.csv 파일을 같은 폴더에 둘 것)
streamlit run main.py
