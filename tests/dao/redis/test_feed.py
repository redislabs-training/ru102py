import datetime

import pytest

from redisolar.dao.redis import FeedDaoRedis
from redisolar.models import MeterReading

TESTING_SITE_ID = 1
NOW = datetime.datetime.utcnow()


@pytest.fixture
def feed_dao(redis, key_schema):
    yield FeedDaoRedis(redis, key_schema)


def generate_meter_reading(site_id: int, datetime: datetime.datetime):
    return MeterReading(site_id=site_id,
                        timestamp=datetime,
                        temp_c=15.0,
                        wh_generated=0.025,
                        wh_used=0.015)


def test_basic_insert_returns_recent(feed_dao):
    now = datetime.datetime.now()
    reading0 = generate_meter_reading(1, now)
    reading1 = generate_meter_reading(1, now - datetime.timedelta(minutes=1))
    feed_dao.insert(reading0)
    feed_dao.insert(reading1)

    global_list = feed_dao.get_recent_global(100)
    assert len(global_list) == 2
    assert global_list[0] == reading1
    assert global_list[1] == reading0

    site_list = feed_dao.get_recent_for_site(1, 100)
    assert len(site_list) == 2
    assert site_list[0] == reading1
    assert site_list[1] == reading0
