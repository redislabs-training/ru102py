import os

import pytest
import redis

USERNAME = os.environ.get('REDISOLAR_REDIS_USERNAME')
PASSWORD = os.environ.get('REDISOLAR_REDIS_PASSWORD')


@pytest.fixture
def redis_connection(app):
    client_kwargs = {
        "host": app.config['REDIS_HOST'],
        "port": app.config['REDIS_PORT'],
        "decode_responses": True
    }

    if USERNAME:
        client_kwargs["username"] = USERNAME
    if PASSWORD:
        client_kwargs["password"] = PASSWORD

    yield redis.Redis(**client_kwargs)


def test_say_hello(redis_connection):
    result = redis_connection.set("hello", "world")
    value = redis_connection.get("hello")
    assert result is True
    assert value == "world"
