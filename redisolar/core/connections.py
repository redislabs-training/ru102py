import os

import redis

PASSWORD = os.environ.get('REDISOLAR_REDIS_PASSWORD')


def get_redis_connection(hostname, port, password=PASSWORD):
    if PASSWORD:
        return redis.Redis(host=hostname,
                           port=port,
                           password=PASSWORD,
                           decode_responses=True)

    return redis.Redis(host=hostname, port=port, decode_responses=True)
