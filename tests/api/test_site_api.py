import pytest

from redisolar.dao.redis import SiteDaoRedis
from redisolar.models import Coordinate
from redisolar.models import Site
from redisolar.schema import SiteSchema


@pytest.fixture
def sites(redis, key_schema):
    site_dao = SiteDaoRedis(redis, key_schema)

    site1 = Site(id=1,
                 capacity=10.0,
                 panels=100,
                 address="100 SE Pine St.",
                 city="Portland",
                 state="OR",
                 postal_code="97202",
                 coordinate=Coordinate(lat=1, lng=1))

    site2 = Site(id=2,
                 capacity=25.0,
                 panels=110,
                 address="101 SW Ankeny",
                 city="Portland",
                 state="OR",
                 postal_code="97203",
                 coordinate=Coordinate(lat=1, lng=1))

    site3 = Site(id=3,
                 capacity=100.0,
                 panels=155,
                 address="201 SE Burnside",
                 city="Portland",
                 state="OR",
                 postal_code="97204",
                 coordinate=Coordinate(lat=1, lng=1))

    site_dao.insert_many(site1, site2, site3)

    yield [site1, site2, site3]


def test_find_by_id(sites, client):
    site_id = 1
    found_site = client.get(f'/sites/{site_id}').json
    assert SiteSchema().load(found_site) == sites[0]


def test_find_all(sites, client):
    resp = client.get('/sites').json
    resp_sites = SiteSchema(many=True).load(resp)
    assert set(resp_sites) == set(sites)
