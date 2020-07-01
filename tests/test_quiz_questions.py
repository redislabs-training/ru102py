"""Unit tests quiz questions in the final exam."""
import datetime
from typing import Set

import pytest

from redisolar.dao.base import RateLimitExceededException


def test_set_get(redis, key_schema):
    key = key_schema.quiz_get_set_key()
    client = redis
    client.connection_pool.connection_kwargs['decode_responses'] = False
    client.set(key, 1.5)
    result = client.get(key)
    assert isinstance(result, bytes)


def test_get_members(redis, key_schema):
    key = key_schema.quiz_get_members_key()
    client = redis

    for i in range(10):
        redis.sadd(key, i)

    def get_members1(key: str) -> Set[str]:
        return client.smembers(key)

    def get_members2(key: str) -> Set[str]:
        return set(client.sscan_iter(key, count=1000))

    expected = {str(i) for i in range(10)}

    assert get_members1(key) == expected
    assert get_members2(key) == expected


def test_zadd(redis, key_schema):
    client = redis
    key = key_schema.quiz_metrics_key()

    def insert(minute_of_day: int, element: str):
        redis.zadd(key, mapping={element: minute_of_day})

    insert(0, "A")
    insert(1, "B")
    insert(2, "C")
    insert(3, "A")

    results = client.zrange(key, 0, -1)
    assert results == ["B", "C", "A"]


def test_pipeline_vs_tx(redis, key_schema):
    client = redis
    key_1 = key_schema.quiz_pipeline_key_1()
    key_2 = key_schema.quiz_pipeline_key_2()

    def pipeline(key_1: str, key_2: str):
        # Using pipeline() creates a transaction by default.
        with client.pipeline() as t:
            t.lpush(key_1, "A")
            t.incr(key_2)
            t.execute()

    def transaction(key_1: str, key_2: str):
        # Meanwhile, transaction=False creates a real pipeline.
        with client.pipeline(transaction=False) as p:
            p.lpush(key_1, "A")
            p.incr(key_2)
            p.execute()

    pipeline(key_1, key_2)
    transaction(key_1, key_2)

    assert client.lrange(key_1, 0, -1) == ["A", "A"]
    assert client.get(key_2) == '2'


def test_stream(redis, key_schema):
    client = redis
    key = key_schema.quiz_streams_key()

    client.xadd(key, id="1-0", fields={"thing": 1})
    client.xadd(key, id="2-0", fields={"thing": 1})
    client.xadd(key, id="3-0", fields={"thing": 1})

    _id, _ = client.xrange(key, '3-0', '3-0')[0]

    assert _id == "3-0"


def test_race_condition(redis, key_schema):
    client = redis
    key = key_schema.quiz_race_condition_key()
    client.hset(key, "max-temp", 1)

    def update_temperature(key, current_temperature: float):
        max_temperature = client.hget(key, "max-temp")

        if current_temperature > float(max_temperature):
            client.hset(key, "max-temp", current_temperature)

    update_temperature(key, 22)
    assert client.hget(key, "max-temp") == '22'


def test_rate_limiter(redis, key_schema):
    client = redis
    now = datetime.datetime.now()
    key = key_schema.quiz_rate_limiter_key(now.timestamp(), 1)

    def hit(user_id: str, max_hits: int):
        with client.pipeline(transaction=False) as p:
            p.lpush(key, now.isoformat())
            p.expire(key, 1)
            p.lrange(key, 0, -1)
            _, _, hits = p.execute()

            if len(hits) > max_hits:
                raise RateLimitExceededException

    hit(1, 2)
    hit(1, 2)

    with pytest.raises(RateLimitExceededException):
        hit(1, 2)
