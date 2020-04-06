from redisolar.dao.base import CapacityDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.models import CapacityReport
from redisolar.models import MeterReading
from redisolar.models import SiteCapacityTuple


class CapacityReportDaoRedis(CapacityDaoBase, RedisDaoBase):
    """Persists and queries CapacityReports in Redis."""
    def update(self, meter_reading: MeterReading) -> None:
        capacity_ranking_key = self.key_schema.capacity_ranking_key()
        self.redis.zadd(capacity_ranking_key,
                        {meter_reading.site_id: meter_reading.current_capacity})

    def get_report(self, limit: int) -> CapacityReport:
        capacity_ranking_key = self.key_schema.capacity_ranking_key()
        p = self.redis.pipeline()
        p.zrange(capacity_ranking_key, 0, limit - 1, withscores=True)
        p.zrevrange(capacity_ranking_key, 0, limit - 1, withscores=True)
        low_capacity, high_capacity = p.execute()

        low_capacity_list = [
            SiteCapacityTuple(site_id=v[0], capacity=v[1]) for v in low_capacity
        ]
        high_capacity_list = [
            SiteCapacityTuple(site_id=v[0], capacity=v[1]) for v in high_capacity
        ]

        return CapacityReport(high_capacity_list, low_capacity_list)

    # Challenge 6
    def get_rank(self, site_id: int) -> float:
        capacity_ranking_key = self.key_schema.capacity_ranking_key()
        return self.redis.zrevrank(capacity_ranking_key, site_id)
