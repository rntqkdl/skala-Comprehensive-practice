# 비동기 데이터 수집 및 품질 검증 파이프라인

## 📌 프로젝트 개요
본 프로젝트는 3개의 외부 공개 API를 비동기 방식(`asyncio`, `httpx`)으로 동시 호출하여 데이터를 수집하고, `Pydantic v2`를 이용해 데이터의 타입과 범위를 엄격하게 검증하는 파이프라인입니다. 검증된 데이터는 CSV와 Parquet 형식으로 각각 저장되며, 파일 I/O 성능(읽기/쓰기 시간 및 파일 크기)을 벤치마크하여 비교합니다.

- **작성자**: 안성민 (광주 4반)
- **작성일**: 2026-07-20

## 🛠 사용 기술 및 라이브러리
- **Python 3.11+**
- **비동기 통신**: `asyncio`, `httpx`
- **데이터 검증**: `pydantic v2`
- **데이터 처리 및 저장**: `pandas`, `pyarrow` (CSV, Parquet)
- **테스트 및 품질**: `pytest`, `ruff`

## 🚀 수집 대상 API (총 3종)
1. **Open-Meteo**: 서울 3일 시간대별 기온 및 강수확률
2. **Countries.dev**: 대한민국(KOR) 국가 정보
3. **ip-api**: 8.8.8.8 IP 기반 지역 정보

## 📁 파일 구조 및 역할
- `main.py`: 비동기 API 수집, 검증, 변환, 저장 벤치마크를 통합 실행하는 메인 오케스트레이션
- `schemas.py`: Pydantic 모델을 통한 응답 데이터 구조 정의 및 타입/범위 유효성 검증
- `benchmark.py`: 검증된 DataFrame을 CSV/Parquet로 저장하고 I/O 성능을 측정
- `test.py`: Pydantic 모델의 정상/오류(ValidationError) 케이스 단위 테스트
- `requirements.txt`: 프로젝트 의존성 패키지 관리

## 💻 실행 방법
```bash
# 1. 가상환경 생성 및 활성화
python3 -m venv .venv
source .venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 린팅 및 단위 테스트 검증
ruff check .
pytest test.py

# 4. 파이프라인 실행 (데이터 수집 -> 검증 -> CSV/Parquet 저장 및 비교)
python main.py