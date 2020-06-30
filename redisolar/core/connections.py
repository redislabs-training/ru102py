import os

import redis
from redistimeseries.client import Client  # type: ignore

USERNAME = os.environ.get('REDISOLAR_REDIS_USERNAME')
PASSWORD = os.environ.get('REDISOLAR_REDIS_PASSWORD')


def get_redis_connection(hostname, port, username=USERNAME, password=PASSWORD):
    args = {
        "host": hostname,
        "port": port,
        "decode_responses": True
    }
    if password:
        args["password"] = password
    if username:
        args["username"] = username

    return redis.Redis(**args)


def get_redis_timeseries_connection(hostname, port, username=USERNAME, password=PASSWORD):
    args = {
        "host": hostname,
        "port": port,
        "decode_responses": True
    }
    if password:
        args["password"] = password
    if username:
        args["username"] = username

    return Client(**args)
