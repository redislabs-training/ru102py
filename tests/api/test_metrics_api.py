import datetime
from typing import Generator
from typing import List

import pytest

from redisolar.dao.redis import MetricDaoRedis
from redisolar.models import Measurement
from redisolar.models import MeterReading
from redisolar.schema import MeasurementSchema

TESTING_SITE_ID = 1
NOW = datetime.datetime.utcnow()


@pytest.fixture
def metric_dao(redis, key_schema):
    yield MetricDaoRedis(redis, key_schema)


@pytest.fixture
def readings(metric_dao) -> Generator[List[MeterReading], None, None]:
    readings = []
    time = NOW
    for i in range(72 * 60):
        readings.append(
            MeterReading(site_id=1,
                         temp_c=i * 1.0,
                         wh_used=i * 1.0,
                         wh_generated=i * 1.0,
                         timestamp=time))
        time = time - datetime.timedelta(minutes=1)
    yield readings


def _check_measurements(measurements: List[Measurement], limit: int):
    assert len(measurements) == limit

    i = limit
    for measurement in measurements:
        assert measurement.value == (i - 1) * 1.0
        i -= 1


# Callenge #2

@pytest.mark.skip("Remove for challenge #2")
def _test_insert_and_retrieve(client, readings: List[MeterReading],
                              metric_dao: MetricDaoRedis, limit: int):
    for reading in readings:
        metric_dao.insert(reading)

    resp = client.get(f'/metrics/{TESTING_SITE_ID}?count={limit}').json
    plots = resp['plots']

    for plot in plots:
        measurements = MeasurementSchema(many=True).load(plot['measurements'])
        _check_measurements(measurements, limit)


@pytest.mark.skip("Remove for challenge #2")
def test_datetime_is_unix_timestamp(metric_dao, client):
    reading = MeterReading(site_id=1,
                           temp_c=1.0,
                           wh_used=1.0,
                           wh_generated=1.0,
                           timestamp=NOW)
    metric_dao.insert(reading)

    resp = client.get(f'/metrics/{TESTING_SITE_ID}?count=1').json
    plots = resp['plots']
    measurement = plots[0]['measurements'][0]
    mdt = datetime.datetime.fromtimestamp(measurement['timestamp'])
    rdt = reading.timestamp
    assert mdt.hour == rdt.hour and mdt.minute == rdt.minute \
        and mdt.day == mdt.day and mdt.year == rdt.year


@pytest.mark.skip("Remove for challenge #2")
def test_small(metric_dao, readings, client):
    _test_insert_and_retrieve(client, readings, metric_dao, 1)


@pytest.mark.skip("Remove for challenge #2")
def test_large(metric_dao, readings, client):
    _test_insert_and_retrieve(client, readings, metric_dao, 100)
