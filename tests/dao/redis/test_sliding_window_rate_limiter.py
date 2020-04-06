import time

import pytest

from redisolar.dao.redis.sliding_window_rate_limiter import RateLimitExceededException
from redisolar.dao.redis.sliding_window_rate_limiter import SlidingWindowRateLimiter

TEN_SECONDS = 10 * 1000


def test_within_limit_inside_window(redis, key_schema):
    exception_count = 0
    limiter = SlidingWindowRateLimiter(TEN_SECONDS, 10, redis, key_schema=key_schema)

    for _ in range(10):
        try:
            limiter.hit("foo")
        except RateLimitExceededException:
            exception_count += 1

    assert exception_count == 0


def test_exceeds_limit_inside_window(redis, key_schema):
    exception_count = 0
    limiter = SlidingWindowRateLimiter(TEN_SECONDS, 10, redis, key_schema=key_schema)

    for _ in range(12):
        try:
            limiter.hit("foo")
        except RateLimitExceededException:
            exception_count += 1

    assert exception_count == 2


def test_exceeds_limit_outside_window(redis, key_schema):
    raised = False
    limiter = SlidingWindowRateLimiter(100, 10, redis, key_schema=key_schema)

    for _ in range(10):
        limiter.hit("foo")

    # Sleep to let the window move and thus allow an 11th request.
    time.sleep(1)

    try:
        limiter.hit("foo")
    except RateLimitExceededException:
        raised = True

    assert raised is False


