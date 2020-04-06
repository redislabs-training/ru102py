import datetime

import pytest

from redisolar.dao.redis import CapacityReportDaoRedis
from redisolar.models import MeterReading


@pytest.fixture
def readings():
    now = datetime.datetime.utcnow()
    yield [
        MeterReading(site_id=i, timestamp=now, wh_used=1.2, wh_generated=i, temp_c=22.0)
        for i in range(10)
    ]


@pytest.fixture
def capacity_report_dao(redis, key_schema):
    yield CapacityReportDaoRedis(redis, key_schema)


def test_get_report(readings, capacity_report_dao, client):
    for reading in readings:
        capacity_report_dao.update(reading)

    report = client.get('/capacity').json
    highest = report['highest_capacity']
    lowest = report['lowest_capacity']

    assert len(highest) == 10
    assert len(lowest) == 10

    assert highest[0]['capacity'] > highest[1]['capacity']
    assert lowest[0]['capacity'] < lowest[1]['capacity']
    assert lowest[4]['capacity'] > lowest[0]['capacity']


def test_specifying_limit(readings, capacity_report_dao, client):
    for reading in readings:
        capacity_report_dao.update(reading)

    report = client.get('/capacity?limit=1').json
    assert len(report['highest_capacity']) == 1
