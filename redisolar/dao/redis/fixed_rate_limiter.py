import datetime
from enum import Enum

from redis.client import Redis

from redisolar.dao.base import RateLimiterDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.dao.redis.key_schema import KeySchema


class MinuteInterval(Enum):
    """Supported minute intervals."""
    ONE = 1
    FIVE = 5
    TEN = 10
    TWENTY = 20
    THIRTY = 30
    SIXTY = 60


class RateLimitExceededException(Exception):
    """Raised when the rate limit is exceeded."""


class FixedRateLimiter(RateLimiterDaoBase, RedisDaoBase):
    """
    A fixed-window rate-limiter.

    Must be configured with a name, a minute interval, and
    the max hits allowed in that interval.

    For example, a minute_interval of 1 and a max_hits of 10
    means that...

    Interval    Hits   Result
    12:00          9       OK
    12:01         10       OK
    12:02         11       RateLimitExceededException

    For a minute_interval of 5 and max_hits of 50...

    Interval    Hits    Result
    12:00         99        OK
    12:05          2        OK
    12:10        101        RateLimitExceededException
    """
    def __init__(self,
                 interval: MinuteInterval,
                 max_hits: float,
                 redis_client: Redis,
                 key_schema: KeySchema = None,
                 **kwargs):
        self.interval = interval
        self.expiration = interval.value * 60
        self.max_hits = max_hits
        super().__init__(redis_client, key_schema, **kwargs)

    def _get_minute_of_day_block(self, dt: datetime.datetime) -> int:
        minute_of_day = dt.hour * 60 + dt.minute
        return minute_of_day / self.interval.value

    def _get_key(self, name: str) -> str:
        day_minute_block = self._get_minute_of_day_block(datetime.datetime.now())
        return self.key_schema.fixed_rate_limiter_key(name, day_minute_block, self.max_hits)

    def hit(self, name: str) -> None:
        key = self._get_key(name)
        pipeline = self.redis.pipeline()

        pipeline.incr(key)
        pipeline.expire(key, self.expiration)
        hits, _ = pipeline.execute()

        if hits > self.max_hits:
            raise RateLimitExceededException()
