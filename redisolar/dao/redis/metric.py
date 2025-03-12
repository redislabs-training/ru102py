import datetime
from collections import deque
from typing import List, Deque

import redis

from redisolar.dao.base import MetricDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.models import Measurement
from redisolar.models import MeterReading
from redisolar.models import MetricUnit

MAX_METRIC_RETENTION_DAYS = 30
MAX_DAYS_TO_RETURN = 7
METRICS_PER_DAY = 60 * 24
METRIC_EXPIRATION_SECONDS = 60 * 60 * 24 * MAX_METRIC_RETENTION_DAYS + 1


class MeasurementMinute:
    """
    Utility class to convert between our sorted set members and their
    constituent measurement and minute values.

    Also rounds decimals before storing them.
    """
    def __init__(self, measurement: float, minute_of_day: int):
        self.measurement = measurement
        self.minute_of_day = minute_of_day

    @classmethod
    def from_zset_value(cls, zset_value: str):
        parts = zset_value.split(":")

        if len(parts) == 2:
            return MeasurementMinute(float(parts[0]), int(parts[1]))

        raise ValueError(
            "Cannot convert zset_value {} to MeasurementMinute".format(zset_value))

    def __str__(self) -> str:
        return f"{self.measurement:.2f}:{self.minute_of_day}"


class MetricDaoRedis(MetricDaoBase, RedisDaoBase):
    def _get_measurements_for_date(self, site_id: int, date: datetime.datetime,
                                   unit: MetricUnit, count: int) -> List[Measurement]:
        """
        Return up to `count` elements from the sorted set corresponding to
        the site_id, date, and metric unit specified here.
        """
        measurements = []

        # Get the metric key for the day implied by the date.
        # metric:[unit-name]:[year-month-day]:[site-id]
        # e.g.: metrics:whU:2020-01-01:1
        key = self.key_schema.day_metric_key(site_id, unit, date)

        # Get `count` number of items from the end of the sorted set.
        metrics = self.redis.zrevrange(key, 0, count - 1, withscores=True)

        for metric in metrics:
            # `zrevrange()` returns (member, score) tuples, and within these
            # tuples, "member" is a string of the form [measurement]:[minute].
            # The MeasurementMinute class abstracts this for us.
            mm = MeasurementMinute.from_zset_value(metric[0])

            # Derive the datetime for the measurement using the date and
            # the minute of the day. Note that this always returns datetime
            # objects whose seconds value is zero.
            date = self._get_date_from_day_minute(date, mm.minute_of_day)

            # Add a new measurement to the list of measurements.
            measurements.append(
                Measurement(site_id=site_id,
                            metric_unit=unit,
                            timestamp=date,
                            value=mm.measurement))

        return measurements

    def _get_day_minute(self, date: datetime.datetime) -> int:
        """
        Return the minute of the day. For example:
        01:12 is the 72nd minute of the day
        5:00 is the 300th minute of the day
        """
        hour = date.hour
        minute = date.minute

        return hour * 60 + minute

    def _get_date_from_day_minute(self, date: datetime.datetime,
                                  day_minute: int) -> datetime.datetime:
        start = datetime.datetime(year=date.year, month=date.month, day=date.day,
                                  hour=0, minute=0)
        return start + datetime.timedelta(minutes=day_minute)

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
        """Insert a specific metric."""
        metric_key = self.key_schema.day_metric_key(site_id, unit, time)
        minute_of_day = self._get_day_minute(time)

        # Create a MeasurementMinute object to encode measurement + minute into a single string.
        mm = MeasurementMinute(value, minute_of_day)
        
        # Add to the sorted set:
        # - member is the string representation of MeasurementMinute (e.g. "18.00:120")
        # - score is the integer minute of the day (e.g. 120 for 2:00 am)
        pipeline.zadd(metric_key, {str(mm): minute_of_day})
        
        # Optionally set an expiration to clean up older data:
        pipeline.expire(metric_key, METRIC_EXPIRATION_SECONDS)


    def get_recent(self, site_id: int, unit: MetricUnit, time: datetime.datetime,
                   limit: int, **kwargs) -> Deque[Measurement]:

        if limit > METRICS_PER_DAY * MAX_METRIC_RETENTION_DAYS:
            raise ValueError("Cannot request more than two weeks of minute-level data")

        measurements: deque = deque()
        current_date = time
        count = limit
        iterations = 0

        # We're going to start at the end of the sorted set and go backwards in
        # time until we reach the limit of measurements or max number of days
        # to return. That means that we're retrieving data from redis in
        # newest -> oldest sorted order.
        #
        # However, we want to give it to clients in oldest -> newest sorted
        # order. So, we use a double-ended queue and add data to its left side.
        # By adding data to the left side, we in effect reverse it, ending up
        # with all data sorted correctly in oldest -> newest order.
        while count > 0 and iterations < MAX_DAYS_TO_RETURN:
            ms = self._get_measurements_for_date(site_id, current_date, unit, count)
            measurements.extendleft(ms)
            count -= len(ms)
            current_date = current_date - datetime.timedelta(days=1)
            iterations += 1

        return measurements
