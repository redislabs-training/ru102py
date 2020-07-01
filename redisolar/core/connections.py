import os

import redis
from redistimeseries.client import Client  # type: ignore

USERNAME = os.environ.get('REDISOLAR_REDIS_USERNAME')
PASSWORD = os.environ.get('REDISOLAR_REDIS_PASSWORD')


def get_redis_connection(hostname, port, username=USERNAME, password=PASSWORD):
    client_kwargs = {
        "host": hostname,
        "port": port,
        "decode_responses": True
    }
    if password:
        client_kwargs["password"] = password
    if username:
        client_kwargs["username"] = username

    return redis.Redis(**client_kwargs)


def get_redis_timeseries_connection(hostname, port, username=USERNAME, password=PASSWORD):
    client_kwargs = {
        "host": hostname,
        "port": port,
        "decode_responses": True
    }
    if password:
        client_kwargs["password"] = password
    if username:
        client_kwargs["username"] = username

    return Client(**client_kwargs)
