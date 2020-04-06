import pytest

from redisolar.dao.redis.fixed_rate_limiter import FixedRateLimiter
from redisolar.dao.redis.fixed_rate_limiter import MinuteInterval
from redisolar.dao.redis.fixed_rate_limiter import RateLimitExceededException


def test_within_limit(redis, key_schema):
    exception_count = 0
    limiter = FixedRateLimiter(MinuteInterval.ONE, 10, redis, key_schema=key_schema)

    for _ in range(10):
        try:
            limiter.hit("foo")
        except RateLimitExceededException:
            exception_count += 1

    assert exception_count == 0


def test_exceeds_limit(redis, key_schema):
    exception_count = 0
    limiter = FixedRateLimiter(MinuteInterval.ONE, 10, redis, key_schema=key_schema)

    for _ in range(12):
        try:
            limiter.hit("foo")
        except RateLimitExceededException:
            exception_count += 1

    assert exception_count == 2
