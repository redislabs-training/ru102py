import datetime

import pytest

from redisolar.dao.redis import SiteStatsDaoRedis
from redisolar.models import MeterReading


@pytest.fixture
def site_stats_dao(redis, key_schema):
    yield SiteStatsDaoRedis(redis, key_schema)


def test_update(site_stats_dao: SiteStatsDaoRedis):
    reading1 = MeterReading(site_id=1,
                            timestamp=datetime.datetime.now(),
                            temp_c=15.0,
                            wh_generated=1.0,
                            wh_used=0.0)
    reading2 = MeterReading(site_id=1,
                            timestamp=datetime.datetime.now(),
                            temp_c=15.0,
                            wh_generated=2.0,
                            wh_used=0.0)

    site_stats_dao.update(reading1)
    site_stats_dao.update(reading2)

    stats = site_stats_dao.find_by_id(1, reading1.timestamp)

    assert stats.max_wh_generated == 2.0
    assert stats.min_wh_generated == 1.0
    assert stats.max_capacity == 2.0
