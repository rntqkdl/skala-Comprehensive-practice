"""
[소스 파일 정보]
- 작성자: 안성민 (광주 4반)
- 작성일: 2026-07-20
- 파일 역할: 비동기(asyncio) 다중 API 수집, 스키마 검증, 최종 저장 오케스트레이션을 담당하는 메인 실행 파일.
"""
import asyncio
import httpx
import pandas as pd
from pydantic import ValidationError
from typing import Dict, List, Any

from schemas import WeatherData, IpData, CountryData
from benchmark import run_io_benchmark

# [요구사항] 수집 대상 API 3종 정의
API_TARGETS = {
    "weather": "https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul",
    "country": "https://countries.dev/alpha/KOR",
    "ip": "http://ip-api.com/json/8.8.8.8"
}

async def fetch_api(client: httpx.AsyncClient, name: str, url: str, max_retries: int = 3) -> Dict[str, Any]:
    """단일 API를 비동기(httpx)로 호출하며, 네트워크 오류 시 최대 3회 재시도합니다."""
    for attempt in range(1, max_retries + 1):
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status() 
            return {"name": name, "data": response.json(), "error": None}
            
        except (httpx.TimeoutException, httpx.RequestError, httpx.HTTPStatusError) as e:
            if attempt == max_retries:
                return {"name": name, "data": None, "error": f"네트워크 에러 ({type(e).__name__}): {str(e)}"}
            print(f"[{name}] 수집 지연 ({attempt}/{max_retries}회 실패). 2초 후 재시도합니다...")
            await asyncio.sleep(2)
            
        except ValueError:
            return {"name": name, "data": None, "error": "응답이 유효한 JSON 포맷이 아님"}

    return {"name": name, "data": None, "error": "알 수 없는 루프 종료"}

async def fetch_all_data(targets: Dict[str, str]) -> List[Dict[str, Any]]:
    """[비동기 수집 요구사항] asyncio.gather()를 이용해 3개 API를 동시에 병렬 요청합니다."""
    async with httpx.AsyncClient() as client:
        tasks = [fetch_api(client, name, url) for name, url in targets.items()]
        return await asyncio.gather(*tasks)

def process_and_flatten_data(results: List[Dict[str, Any]]) -> Dict[str, pd.DataFrame]:
    """[스키마 검증 요구사항] 수집된 JSON에서 필요한 필드만 추출하여 Pydantic 모델로 검증합니다."""
    valid_dfs = {}
    for res in results:
        name, data, error = res["name"], res["data"], res["error"]
        
        if error:
            print(f"[{name}] ❌ API 수집 실패: {error}")
            continue

        try:
            # 수집된 종류에 맞는 Pydantic 모델을 통한 타입/범위 유효성 검사
            if name == "weather":
                validated = WeatherData(**data)
                valid_dfs[name] = pd.DataFrame(validated.to_flat_dict())
            elif name == "ip":
                validated = IpData(**data)
                valid_dfs[name] = pd.DataFrame([validated.to_flat_dict()])
            elif name == "country":
                # 리스트 형태의 응답을 방어적으로 추출
                raw = data[0] if isinstance(data, list) else data
                validated = CountryData(**raw)
                valid_dfs[name] = pd.DataFrame([validated.to_flat_dict()])
                
            print(f"[{name}] ✅ 데이터 타입 및 범위 검증 완료")
            
        # [요구사항] 타입 오류 시 ValidationError 예외 처리로 파이프라인 중단 방지
        except ValidationError as e:
            print(f"[{name}] ❌ 스키마 유효성 검증 실패 (ValidationError 격리):\n{e}")
            
    return valid_dfs

async def main():
    print(">>> 1. 비동기 데이터 동시 수집 시작 (asyncio.gather)")
    results = await fetch_all_data(API_TARGETS)

    print("\n>>> 2. 데이터 Pydantic 스키마 검증 및 필드 추출")
    valid_dfs = process_and_flatten_data(results)

    print("\n>>> 3. 검증 통과 데이터 CSV/Parquet 포맷 저장 및 성능 비교")
    if not valid_dfs:
        print("❌ 저장할 유효한 데이터가 없습니다.")
    else:
        # 검증을 통과한 모든 API 데이터를 CSV와 Parquet로 저장하고 I/O를 측정
        for name, df in valid_dfs.items():
            run_io_benchmark(df, file_name=f"{name}_dataset")

if __name__ == "__main__":
    asyncio.run(main())