import datetime
import unittest.mock as mock

import pytest

from redisolar.dao.redis import MeterReadingDaoRedis
from redisolar.models import MeterReading


@pytest.fixture
def meter_reading_dao(redis_timeseries, key_schema):
    with mock.patch('redisolar.dao.redis.CapacityReportDaoRedis.update') as mock_capacity, \
            mock.patch('redisolar.dao.redis.FeedDaoRedis.insert') as mock_feed, \
            mock.patch('redisolar.dao.redis.MetricDaoRedisTimeseries.insert') as mock_metric, \
            mock.patch('redisolar.dao.redis.SiteStatsDaoRedis.update') as mock_site_stats:
        meter_reading_dao = MeterReadingDaoRedis(redis_timeseries, key_schema)
        yield {
            "dao": meter_reading_dao,
            "mocks": {
                "capacity": mock_capacity,
                "feed": mock_feed,
                "metric": mock_metric,
                "site_stats": mock_site_stats
            }
        }


def test_calls_other_daos(meter_reading_dao):
    reading = MeterReading(site_id=1,
                           timestamp=datetime.datetime.now(),
                           temp_c=15.0,
                           wh_generated=0.025,
                           wh_used=0.015)

    meter_reading_dao['dao'].add(reading)
    mocks = meter_reading_dao['mocks']

    # Challenge #3
    assert mocks['site_stats'].called is True
    assert mocks['metric'].called is True
    assert mocks['feed'].called is True
    assert mocks['capacity'].called is True
