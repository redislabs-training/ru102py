import datetime

import redis.client

from redisolar.dao.base import SiteStatsDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.models import MeterReading
from redisolar.models import SiteStats
from redisolar.schema import SiteStatsSchema
from redisolar.scripts import CompareAndUpdateScript

WEEK_SECONDS = 60 * 60 * 24 * 7


class SiteStatsNotFound(Exception):
    """A SiteStats model was not found for the given query."""


class SiteStatsDaoRedis(SiteStatsDaoBase, RedisDaoBase):
    """Persists and queries SiteStats in Redis."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.compare_and_update_script = CompareAndUpdateScript(self.redis)

    def find_by_id(self, site_id: int, day: datetime.datetime = None,
                   **kwargs) -> SiteStats:
        if day is None:
            day = datetime.datetime.now()

        key = self.key_schema.site_stats_key(site_id, day)
        fields = self.redis.hgetall(key)

        if not fields:
            raise SiteStatsNotFound()

        return SiteStatsSchema().load(fields)

    def _update_basic(self, key: str, reading: MeterReading) -> None:
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

    def _update_optimized(self, key: str, meter_reading: MeterReading,
                      pipeline: redis.client.Pipeline = None) -> None:
        execute = False
        if pipeline is None:
            pipeline = self.redis.pipeline()
            execute = True

        # Set the reporting time, increment count, and set the expiry.
        reporting_time = datetime.datetime.utcnow().isoformat()
        pipeline.hset(key, SiteStats.LAST_REPORTING_TIME, reporting_time)
        pipeline.hincrby(key, SiteStats.COUNT, 1)
        pipeline.expire(key, WEEK_SECONDS)

        # Use the Lua script to update MAX_WH only if the new wh_generated is greater.
        self.compare_and_update_script.update_if_greater(
            pipeline, key, SiteStats.MAX_WH, meter_reading.wh_generated
        )

        # Use the Lua script to update MIN_WH only if the new wh_generated is lower.
        self.compare_and_update_script.update_if_less(
            pipeline, key, SiteStats.MIN_WH, meter_reading.wh_generated
        )

        # Use the Lua script to update MAX_CAPACITY only if the new current_capacity is greater.
        self.compare_and_update_script.update_if_greater(
            pipeline, key, SiteStats.MAX_CAPACITY, meter_reading.current_capacity
        )

        if execute:
            pipeline.execute()

    def update(self, meter_reading: MeterReading, **kwargs) -> None:
        key = self.key_schema.site_stats_key(meter_reading.site_id,
                                             meter_reading.timestamp)
        # Remove for Challenge #3
        self._update_basic(key, meter_reading)

        # Uncomment the following two lines for Challenge #3
        # pipeline = kwargs.get('pipeline')
        # self._update_optimized(key, meter_reading, pipeline)
