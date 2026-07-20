"""
[소스 파일 정보]
- 작성자: 안성민 (광주 4반)
- 작성일: 2026-07-20
- 파일 역할: Pydantic v2를 이용한 API 응답 데이터 구조 정의 및 유효성 검증(타입/범위) 담당
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated

class WeatherHourly(BaseModel):
    time: List[str]
    temperature_2m: List[float] = Field(..., description="섭씨 기온 (float 타입 검증)")
    
    # [스키마 검증 1] 타입 및 범위 검증
    # Annotated를 사용하여 리스트 내부에 들어있는 각각의 '정수(int)'가 0~100 사이인지 강제합니다.
    precipitation_probability: List[Annotated[int, Field(ge=0, le=100)]] = Field(..., description="강수 확률 (0~100%)")

class WeatherData(BaseModel):
    timezone: str
    hourly: WeatherHourly

    def to_flat_dict(self) -> dict:
        """기상 데이터를 DataFrame 생성에 적합한 1차원 딕셔너리로 평탄화"""
        return {
            "time": self.hourly.time,
            "temperature": self.hourly.temperature_2m,
            "precip_prob": self.hourly.precipitation_probability
        }

class IpData(BaseModel):
    # [스키마 검증 2] 필수 필드 존재 여부 검증 (해당 키가 없으면 에러 발생)
    query: str
    status: str
    country: str
    city: str

    def to_flat_dict(self) -> dict:
        return self.model_dump()

class CountryData(BaseModel):
    name: str
    capital: Optional[str] = Field(default=None, description="수도명 (선택적 문자열)")
    region: Optional[str] = None

    def to_flat_dict(self) -> dict:
        """API 응답 중 필요한 필수 필드만 추출하여 평탄화"""
        return {
            "name": self.name,
            "capital": self.capital if self.capital else "N/A",
            "region": self.region
        }