from typing import List

from redisolar.dao.base import FeedDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.models import MeterReading
from redisolar.schema import MeterReadingSchema


class FeedDaoRedis(FeedDaoBase, RedisDaoBase):
    """Persists and queries MeterReadings in Redis."""
    def insert(self, meter_reading: MeterReading) -> None:
        global_key = self.key_schema.global_feed_key()
        site_key = self.key_schema.feed_key(meter_reading.site_id)
        serialized_meter_reading = MeterReadingSchema().dump(meter_reading)

        p = self.redis.pipeline()
        p.xadd(global_key, serialized_meter_reading)
        p.xadd(site_key, serialized_meter_reading)
        p.execute()

    def get_recent_global(self, limit: int) -> List[MeterReading]:
        return self.get_recent(self.key_schema.global_feed_key(), limit)

    def get_recent_for_site(self, site_id: int, limit: int) -> List[MeterReading]:
        return self.get_recent(self.key_schema.feed_key(site_id), limit)

    def get_recent(self, key: str, limit: int) -> List[MeterReading]:
        return [
            MeterReadingSchema().load(entry[1])
            for entry in self.redis.xrevrange(key, count=limit)
        ]
