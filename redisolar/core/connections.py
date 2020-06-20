import os

import redis
from redistimeseries.client import Client

PASSWORD = os.environ.get('REDISOLAR_REDIS_PASSWORD')


def get_redis_connection(hostname, port, password=PASSWORD):
    if password:
        return redis.Redis(host=hostname,
                           port=port,
                           password=password,
                           decode_responses=True)

    return redis.Redis(host=hostname, port=port, decode_responses=True)


def get_redis_timeseries_connection(hostname, port, password=PASSWORD):
    if password:
        return Client(host=hostname, port=port, password=password, decode_responses=True)

    return Client(host=hostname, port=port, decode_responses=True)
