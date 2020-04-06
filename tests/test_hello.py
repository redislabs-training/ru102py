import os

import pytest
import redis

PASSWORD = os.environ.get('REDISOLAR_REDIS_PASSWORD')


@pytest.fixture
def redis_connection(app):
    hostname = app.config['REDIS_HOST']
    port = app.config['REDIS_PORT']

    if PASSWORD:
        yield redis.Redis(host=hostname,
                          port=port,
                          password=PASSWORD,
                          decode_responses=True)

    yield redis.Redis(host=hostname, port=port, decode_responses=True)


def test_hello(redis_connection):
    result = redis_connection.set("hello", "world")
    value = redis_connection.get("hello")
    assert result is True
    assert value == "world"
