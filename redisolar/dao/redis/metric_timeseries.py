import datetime
from itertools import islice
from typing import List

import redis

from redisolar.dao.base import MetricDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.models import Measurement
from redisolar.models import MeterReading
from redisolar.models import MetricUnit

RETENTION_MS = 60 * 60 * 24 * 14 * 1000


def unix_milliseconds(time):
    return int(time.timestamp() * 1000)


class MetricDaoRedisTimeseries(MetricDaoBase, RedisDaoBase):
    def insert(self, meter_reading: MeterReading, **kwargs) -> None:
        pipeline = kwargs.get('pipeline')
        execute = False

        if pipeline is None:
            execute = True
            pipeline = self.redis.pipeline()

        self.insert_metric(meter_reading.site_id, meter_reading.wh_generated,
                           MetricUnit.WH_GENERATED, meter_reading.timestamp, pipeline)
        self.insert_metric(meter_reading.site_id, meter_reading.wh_used,
                           MetricUnit.WH_USED, meter_reading.timestamp, pipeline)
        self.insert_metric(meter_reading.site_id, meter_reading.temp_c,
                           MetricUnit.TEMP_CELSIUS, meter_reading.timestamp, pipeline)

        if execute:
            pipeline.execute()

    def insert_metric(self, site_id: int, value: float, unit: MetricUnit,
                      time: datetime.datetime, pipeline: redis.client.Pipeline):
        metric_key = self.key_schema.timeseries_key(site_id, unit)
        time_ms = unix_milliseconds(time)
        self.redis.add(metric_key, time_ms, value, RETENTION_MS)  # type: ignore

    def get_recent(self, site_id: int, unit: MetricUnit, time: datetime.datetime,
                   limit: int, **kwargs) -> List[Measurement]:
        metric_key = self.key_schema.timeseries_key(site_id, unit)
        time_ms = unix_milliseconds(time)
        initial_timestamp = time_ms - (limit * 60) * 1000
        values = self.redis.range(metric_key, initial_timestamp, time_ms)  # type: ignore

        return [
            Measurement(site_id=site_id,
                        metric_unit=unit,
                        timestamp=value[0] / 1000,
                        value=value[1]) for value in islice(values, limit)
        ]
