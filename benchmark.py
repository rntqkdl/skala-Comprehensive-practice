"""
[소스 파일 정보]
- 작성자: 안성민 (광주 4반)
- 작성일: 2026-07-20
- 파일 역할: 검증 완료된 데이터를 CSV 및 Parquet로 로컬에 저장하고, 읽기/쓰기 성능을 정밀 측정.
"""
import time
import os
import pandas as pd
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    """실행 소요 시간을 측정하는 컨텍스트 매니저 (코드 중복 방지)"""
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"[{label:^15}] 소요 시간: {elapsed:.5f} sec")

def run_io_benchmark(df: pd.DataFrame, file_name: str = "benchmark_output") -> None:
    """
    [저장 및 성능 비교 요구사항 구현]
    데이터프레임을 CSV와 Parquet 두 가지 포맷으로 실제로 저장한 뒤 파일 크기와 시간을 비교합니다.
    """
    # 저장 경로 누락으로 인한 런타임 에러 방지 (폴더 자동 생성)
    output_dir = Path("output_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / f"{file_name}.csv"
    parquet_path = output_dir / f"{file_name}.parquet"

    print(f"\n📊 [{file_name.upper()} - 저장 및 I/O 성능 비교]")
    print("-" * 55)
    
    # ---------------------------------------------------------
    # 1. 쓰기(Write) 및 저장 시간 측정
    # ---------------------------------------------------------
    with timer("CSV Write"):
        # [CSV 저장 부분] pandas의 to_csv를 이용하여 디스크에 파일 생성
        df.to_csv(csv_path, index=False)
        
    with timer("Parquet Write"):
        # [Parquet 저장 부분] engine="auto"를 통해 pyarrow로 디스크에 파일 생성
        df.to_parquet(parquet_path, engine="auto", index=False)
        
    # ---------------------------------------------------------
    # 2. 읽기(Read) 시간 측정
    # ---------------------------------------------------------
    with timer("CSV Read"):
        pd.read_csv(csv_path)
        
    with timer("Parquet Read"):
        pd.read_parquet(parquet_path, engine="auto")

    # 3. 파일 크기 비교 측정 출력
    print("-" * 55)
    csv_size = os.path.getsize(csv_path) / 1024
    parquet_size = os.path.getsize(parquet_path) / 1024
    print(f"[파일 크기] CSV: {csv_size:.2f} KB | Parquet: {parquet_size:.2f} KB")
    print("-" * 55)