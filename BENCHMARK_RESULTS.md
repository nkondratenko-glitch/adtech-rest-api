# Benchmark Results

The benchmark below was executed locally in demo mode using SQLite + FakeRedis with seeded data. The production stack in docker-compose uses MySQL + Redis.

| endpoint                  | mode                |   avg_ms |   min_ms |   max_ms |   median_ms |
|:--------------------------|:--------------------|---------:|---------:|---------:|------------:|
| /campaign/101/performance | without_redis_cache |    30.21 |    28.82 |    34.42 |       30.07 |
| /campaign/101/performance | with_redis_cache    |     2.47 |     2    |     2.96 |        2.46 |
| /advertiser/1/spending    | without_redis_cache |    30.09 |    29.21 |    31.63 |       30.14 |
| /advertiser/1/spending    | with_redis_cache    |     2.39 |     1.99 |     3.89 |        2.32 |
