from typing import Set


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

    client.add(key, id="1-0", fields={"thing": 1})
    client.add(key, id="2-0", fields={"thing": 1})
    client.add(key, id="3-0", fields={"thing": 1})

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
