import datetime

import pytest

from redisolar.api.meter_reading import MeterReadingsSchema
from redisolar.models import MeterReading


@pytest.fixture
def readings():
    now = datetime.datetime.utcnow()
    yield [
        MeterReading(site_id=i,
                     timestamp=now - datetime.timedelta(minutes=i),
                     wh_used=1.2,
                     wh_generated=i,
                     temp_c=22.0) for i in range(9, -1, -1)
    ]


@pytest.mark.skip("Uncomment for challenge #6")
def test_global_readings_get(client, readings):
    data = MeterReadingsSchema().dump({"readings": readings})
    readings_post = client.post('/meter_readings', json=data)
    assert readings_post.status_code == 202

    readings_get = client.get('/meter_readings')
    assert readings_get.status_code == 200
    assert len(readings_get.json['readings']) == 10


@pytest.mark.skip("Uncomment for challenge #6")
def test_global_readings_get_custom_count(client, readings):
    data = MeterReadingsSchema().dump({"readings": readings})
    readings_post = client.post('/meter_readings', json=data)
    assert readings_post.status_code == 202

    readings_get = client.get('/meter_readings?count=1')
    assert readings_get.status_code == 200
    assert readings_get.json == MeterReadingsSchema().dump({"readings": [readings[9]]})


@pytest.mark.skip("Uncomment for challenge #6")
def test_site_readings_get(client, readings):
    data = MeterReadingsSchema().dump({"readings": readings})
    readings_post = client.post('/meter_readings', json=data)
    assert readings_post.status_code == 202

    readings_get = client.get('/meter_readings/2')
    readings_json = readings_get.json['readings']
    assert readings_get.status_code == 200

    assert len(readings_json) == 1
    assert readings_json[0]['site_id'] == 2


@pytest.mark.skip("Uncomment for challenge #6")
def test_site_readings_get_custom_count(client):
    now = datetime.datetime.utcnow()
    readings = [
        MeterReading(site_id=2,
                     timestamp=now - datetime.timedelta(minutes=i),
                     wh_used=1.2,
                     wh_generated=i,
                     temp_c=22.0) for i in range(9, -1, -1)
    ]
    data = MeterReadingsSchema().dump({"readings": readings})
    readings_post = client.post('/meter_readings', json=data)
    assert readings_post.status_code == 202

    readings_get = client.get('/meter_readings?count=2')
    assert readings_get.status_code == 200
    assert readings_get.json == MeterReadingsSchema().dump(
        {"readings": [readings[9], readings[8]]})
