# Delivery Report

## Implemented stack
- **Framework:** FastAPI
- **Database layer:** SQLAlchemy
- **Production DB target:** MySQL (via Docker Compose)
- **Cache:** Redis with read-through strategy
- **Benchmark mode used in this environment:** SQLite + FakeRedis for reproducible local execution

## Implemented endpoints
- `GET /campaign/{campaign_id}/performance`
- `GET /advertiser/{advertiser_id}/spending`
- `GET /user/{user_id}/engagements`

## Read-through cache behavior
1. Check Redis by key.
2. If key exists, return cached payload.
3. Otherwise query DB, store JSON in Redis, and return DB result.

### TTL
- Campaign performance: **30 seconds**
- Advertiser spending: **5 minutes**

## Benchmark results
| endpoint                  | mode                |   avg_ms |   min_ms |   max_ms |   median_ms |
|:--------------------------|:--------------------|---------:|---------:|---------:|------------:|
| /campaign/101/performance | without_redis_cache |    30.21 |    28.82 |    34.42 |       30.07 |
| /campaign/101/performance | with_redis_cache    |     2.47 |     2    |     2.96 |        2.46 |
| /advertiser/1/spending    | without_redis_cache |    30.09 |    29.21 |    31.63 |       30.14 |
| /advertiser/1/spending    | with_redis_cache    |     2.39 |     1.99 |     3.89 |        2.32 |

## Notes
- The API includes `X-Data-Source` and `X-Response-Time-ms` headers to make cache hits visible during testing.
- Docker Compose is configured for **API + MySQL + Redis**.
- Seed data is created automatically on startup.
- In this sandbox, MySQL/Redis containers were not launched, so the benchmark was executed in local demo mode. The production code path still targets MySQL + Redis through environment variables.

## Run commands
```bash
# Production-style stack
docker compose up --build

# Local benchmark/demo mode
PYTHONPATH=. python scripts/benchmark.py
```
