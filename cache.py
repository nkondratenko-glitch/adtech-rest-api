from __future__ import annotations

import json
import os
from typing import Any

import fakeredis
import redis

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
USE_FAKE_REDIS = os.getenv('USE_FAKE_REDIS', 'false').lower() == 'true'

_cache_client = None


def get_cache_client():
    global _cache_client
    if _cache_client is not None:
        return _cache_client

    if USE_FAKE_REDIS:
        _cache_client = fakeredis.FakeRedis(decode_responses=True)
        return _cache_client

    _cache_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _cache_client


def read_through_cache(key: str, ttl_seconds: int, loader) -> tuple[dict[str, Any], str]:
    client = get_cache_client()
    cached = client.get(key)
    if cached:
        payload = json.loads(cached)
        payload['source'] = 'cache'
        return payload, 'cache'

    payload = loader()
    client.setex(key, ttl_seconds, json.dumps(payload, default=str))
    payload['source'] = 'db'
    return payload, 'db'
