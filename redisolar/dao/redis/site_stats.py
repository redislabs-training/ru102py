import datetime

from redisolar.models import MeterReading
from redisolar.models import SiteStats
from redisolar.scripts import CompareAndUpdateScript
from redisolar.dao.base import SiteStatsDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.schema import SiteStatsSchema


WEEK_SECONDS = 60 * 60 * 24 * 7


class SiteStatsNotFound(Exception):
    """A SiteStats model was not found for the given query."""


class SiteStatsDaoRedis(SiteStatsDaoBase, RedisDaoBase):
    """Persists and queries SiteStats in Redis."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compare_and_update_script = CompareAndUpdateScript(self.redis)

    def find_by_id(self, site_id: int, day: datetime.datetime = None) -> SiteStats:
        if day is None:
            day = datetime.datetime.now()

        key = self.key_schema.site_stats_key(site_id, day)
        fields = self.redis.hgetall(key)

        if not fields:
            raise SiteStatsNotFound()

        return SiteStatsSchema().load(fields)

    def update(self, meter_reading: MeterReading) -> None:
        key = self.key_schema.site_stats_key(meter_reading.site_id, meter_reading.timestamp)
        # self.update_basic(key, meter_reading)
        self.update_optimized(key, meter_reading)

    def update_basic(self, key: str, reading: MeterReading) -> None:
        reporting_time = datetime.datetime.utcnow().isoformat()
        self.redis.hset(key, SiteStats.LAST_REPORTING_TIME, reporting_time)
        self.redis.hincrby(key, SiteStats.COUNT, 1)
        self.redis.expire(key, WEEK_SECONDS)

        max_wh = self.redis.hget(key, SiteStats.MAX_WH)
        if not max_wh or reading.wh_generated > float(max_wh):
            self.redis.hset(key, SiteStats.MAX_WH, reading.wh_generated)

        min_wh = self.redis.hget(key, SiteStats.MIN_WH)
        if not min_wh or reading.wh_generated < float(min_wh):
            self.redis.hset(key, SiteStats.MIN_WH, reading.wh_generated)

        max_capacity = self.redis.hget(key, SiteStats.MAX_CAPACITY)
        if not max_capacity or reading.current_capacity > float(max_capacity):
            self.redis.hset(key, SiteStats.MAX_CAPACITY, reading.wh_generated)

    def update_optimized(self, key: str, reading: MeterReading) -> None:
        reporting_time = datetime.datetime.utcnow().isoformat()

        p = self.redis.pipeline()
        p.hset(key, SiteStats.LAST_REPORTING_TIME, reporting_time)
        p.hincrby(key, SiteStats.COUNT, 1)
        p.expire(key, WEEK_SECONDS)

        self.compare_and_update_script.update_if_greater(
            p, key, SiteStats.MAX_WH, reading.wh_generated)
        self.compare_and_update_script.update_if_less(
            p, key, SiteStats.MIN_WH, reading.wh_generated)
        self.compare_and_update_script.update_if_greater(
            p, key, SiteStats.MAX_CAPACITY, reading.current_capacity)

        p.execute()
