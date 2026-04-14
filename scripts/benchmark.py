from __future__ import annotations

import os
import statistics
import time
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

# Force local demo mode for benchmark reproducibility in this environment.
os.environ['DATABASE_URL'] = 'sqlite:///./benchmark.db'
os.environ['USE_FAKE_REDIS'] = 'true'
os.environ['DB_SIMULATED_DELAY_MS'] = '25'

from app.main import app  # noqa: E402
from app.cache import get_cache_client  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS_MD = ROOT / 'BENCHMARK_RESULTS.md'
RESULTS_CSV = ROOT / 'benchmark_results.csv'


def timed_get(client: TestClient, path: str) -> tuple[float, dict, dict]:
    started = time.perf_counter()
    resp = client.get(path)
    elapsed_ms = (time.perf_counter() - started) * 1000
    resp.raise_for_status()
    return elapsed_ms, resp.json(), dict(resp.headers)


def run_series(client: TestClient, path: str, iterations: int, flush_each_time: bool) -> list[float]:
    timings = []
    cache = get_cache_client()
    for _ in range(iterations):
        if flush_each_time:
            cache.flushall()
        elapsed_ms, _, _ = timed_get(client, path)
        timings.append(elapsed_ms)
    return timings


def summarize(label: str, path: str, timings: list[float]) -> dict:
    return {
        'endpoint': path,
        'mode': label,
        'avg_ms': round(statistics.mean(timings), 2),
        'min_ms': round(min(timings), 2),
        'max_ms': round(max(timings), 2),
        'median_ms': round(statistics.median(timings), 2),
    }


def main() -> None:
    rows = []
    endpoints = [
        '/campaign/101/performance',
        '/advertiser/1/spending',
    ]
    iterations = 30
    with TestClient(app) as client:
        cache = get_cache_client()
        for path in endpoints:
            cache.flushall()
            no_cache_timings = run_series(client, path, iterations, flush_each_time=True)

            cache.flushall()
            warm_elapsed, warm_body, warm_headers = timed_get(client, path)
            cached_timings = []
            for _ in range(iterations):
                elapsed_ms, _, _ = timed_get(client, path)
                cached_timings.append(elapsed_ms)

            rows.append(summarize('without_redis_cache', path, no_cache_timings))
            rows.append(summarize('with_redis_cache', path, cached_timings))

            print(f'Warm request for {path}: {warm_elapsed:.2f} ms | source={warm_headers.get("x-data-source")}')
            print(f'Payload sample: {warm_body}')

    df = pd.DataFrame(rows)
    df.to_csv(RESULTS_CSV, index=False)

    markdown_table = df.to_markdown(index=False)
    RESULTS_MD.write_text(
        '# Benchmark Results\n\n'
        'The benchmark below was executed locally in demo mode using SQLite + FakeRedis with seeded data. '\
        'The production stack in docker-compose uses MySQL + Redis.\n\n'
        f'{markdown_table}\n',
        encoding='utf-8',
    )
    print('\n' + markdown_table)
    print(f'\nSaved: {RESULTS_MD}')
    print(f'Saved: {RESULTS_CSV}')


if __name__ == '__main__':
    main()
