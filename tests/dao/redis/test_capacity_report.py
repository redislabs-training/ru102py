import datetime

import pytest

from redisolar.dao.redis import CapacityReportDaoRedis
from redisolar.models import MeterReading


@pytest.fixture
def capacity_report_dao(redis, key_schema):
    yield CapacityReportDaoRedis(redis, key_schema)


@pytest.fixture
def readings():
    now = datetime.datetime.utcnow()
    yield [
        MeterReading(site_id=i, timestamp=now, wh_used=1.2, wh_generated=i, temp_c=22.0)
        for i in range(10)
    ]


def test_update(redis, readings, capacity_report_dao, key_schema):
    capacity_ranking_key = key_schema.capacity_ranking_key()

    for reading in readings:
        capacity_report_dao.update(reading)

    results = redis.zrevrange(capacity_ranking_key, 0, 20, withscores=True)
    assert len(results) == 10


def test_get_report(readings, capacity_report_dao):
    for reading in readings:
        capacity_report_dao.update(reading)

    report = capacity_report_dao.get_report(5)
    highest = report.highest_capacity
    lowest = report.lowest_capacity

    assert len(highest) == 5
    assert len(lowest) == 5

    assert highest[0].capacity > highest[1].capacity
    assert lowest[0].capacity < lowest[1].capacity
    assert lowest[4].capacity > lowest[0].capacity


def test_get_rank(readings, capacity_report_dao):
    for reading in readings:
        capacity_report_dao.update(reading)
    assert capacity_report_dao.get_rank(readings[0].site_id) == 9
    assert capacity_report_dao.get_rank(readings[9].site_id) == 0
