from dataclasses import dataclass

from redisolar.schema import FlatSiteSchema
from redisolar.models.models import Coordinate
from redisolar.models.models import Site


def test_site_schema_loads_coordinate():
    site = Site(id=1,
                capacity=1,
                panels=1,
                address="Somewhere",
                city="Portland",
                state="OR",
                postal_code="97201",
                coordinate=Coordinate(lat=1.0, lng=1.1))
    json = {
        "id": 1,
        "capacity": 1,
        "panels": 1,
        "address": "Somewhere",
        "city": "Portland",
        "state": "OR",
        "postal_code": "97201",
        "lat": 1,
        "lng": 1.1
    }
    assert FlatSiteSchema().load(json) == site


def test_site_schema_dumps_coordinate():
    site = Site(id=1,
                capacity=1,
                panels=1,
                address="Somewhere",
                city="Portland",
                state="OR",
                postal_code="97201",
                coordinate=Coordinate(lat=1.0, lng=1.1))
    json = {
        "id": 1,
        "capacity": 1,
        "panels": 1,
        "address": "Somewhere",
        "city": "Portland",
        "state": "OR",
        "postal_code": "97201",
        "lat": 1,
        "lng": 1.1
    }
    assert FlatSiteSchema().dump(site) == json
