"""
[소스 파일 정보]
- 작성자: 안성민 (광주 4반)
- 작성일: 2026-07-20
- 파일 역할: pytest를 활용하여 Pydantic 모델의 정상/오류(150% 강수확률 등) 케이스를 방어하는지 검증하는 단위 테스트 파일
"""
import pytest
from pydantic import ValidationError
from schemas import WeatherHourly

def test_weather_hourly_valid():
    """[테스트 1] 정상적인 범위(0~100)의 강수 확률 데이터가 에러 없이 모델을 생성하는지 확인"""
    valid_data = {
        "time": ["2026-07-20T00:00"],
        "temperature_2m": [25.5],
        "precipitation_probability": [50] 
    }
    model = WeatherHourly(**valid_data)
    assert model.precipitation_probability[0] == 50

def test_weather_hourly_invalid_precipitation():
    """[테스트 2] 범위를 초과하는 강수 확률(150%) 입력 시 ValidationError를 뱉어내고 차단하는지 확인"""
    invalid_data = {
        "time": ["2026-07-20T00:00"],
        "temperature_2m": [25.5],
        "precipitation_probability": [150]  # 0~100 범위를 명시적으로 위반
    }
    with pytest.raises(ValidationError):
        WeatherHourly(**invalid_data)