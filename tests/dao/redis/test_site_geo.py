import pytest

from redisolar.dao.redis import SiteGeoDaoRedis
from redisolar.models import Coordinate
from redisolar.models import GeoQuery
from redisolar.models import GeoUnit
from redisolar.models import Site

PORTLAND = Coordinate(lat=45.523064, lng=-122.676483)
BEAVERTON = Coordinate(lat=45.485168, lng=-122.804489)


@pytest.fixture
def site_geo_dao(redis, key_schema):
    yield SiteGeoDaoRedis(redis, key_schema)


def test_insert(redis, site_geo_dao):
    site = Site(id=1,
                capacity=10.0,
                panels=100,
                address="100 SE Pine St.",
                city="Portland",
                state="OR",
                postal_code="97202",
                coordinate=PORTLAND)

    site_geo_dao.insert(site)
    assert site_geo_dao.find_by_id(1) == site


def test_insert_many(site_geo_dao):
    site1 = Site(id=1,
                 capacity=10.0,
                 panels=100,
                 address="100 SE Pine St.",
                 city="Portland",
                 state="OR",
                 postal_code="97202",
                 coordinate=PORTLAND)

    site2 = Site(id=2,
                 capacity=25.0,
                 panels=110,
                 address="101 SW Ankeny",
                 city="Portland",
                 state="OR",
                 postal_code="97203",
                 coordinate=PORTLAND)

    site3 = Site(id=3,
                 capacity=100.0,
                 panels=155,
                 address="201 SE Burnside",
                 city="Portland",
                 state="OR",
                 postal_code="97204",
                 coordinate=PORTLAND)

    site_geo_dao.insert_many(site1, site2, site3)

    assert site_geo_dao.find_by_id(1) == site1
    assert site_geo_dao.find_by_id(2) == site2
    assert site_geo_dao.find_by_id(3) == site3


def test_find_by_id(site_geo_dao):
    site_id = 1
    site = Site(id=site_id,
                capacity=10.0,
                panels=100,
                address="100 SE Pine St.",
                city="Portland",
                state="OR",
                postal_code="97202",
                coordinate=PORTLAND)

    site_geo_dao.insert(site)
    found_site = site_geo_dao.find_by_id(site_id)

    assert found_site == site


def test_find_all(site_geo_dao):
    site1 = Site(id=1,
                 capacity=10.0,
                 panels=100,
                 address="100 SE Pine St.",
                 city="Portland",
                 state="OR",
                 postal_code="97202",
                 coordinate=PORTLAND)

    site2 = Site(id=2,
                 capacity=25.0,
                 panels=110,
                 address="101 SW Ankeny",
                 city="Portland",
                 state="OR",
                 postal_code="97203",
                 coordinate=PORTLAND)

    site3 = Site(id=3,
                 capacity=100.0,
                 panels=155,
                 address="201 SE Burnside",
                 city="Portland",
                 state="OR",
                 postal_code="97204",
                 coordinate=PORTLAND)

    site_geo_dao.insert_many(site1, site2, site3)
    assert site_geo_dao.find_all() == {site1, site2, site3}


def test_find_sites_by_geo(site_geo_dao):
    site1 = Site(id=1,
                 capacity=10.0,
                 panels=100,
                 address="100 SE Pine St.",
                 city="Portland",
                 state="OR",
                 postal_code="97202",
                 coordinate=PORTLAND)

    site2 = Site(id=2,
                 capacity=25.0,
                 panels=110,
                 address="101 SW Ankeny",
                 city="Portland",
                 state="OR",
                 postal_code="97203",
                 coordinate=PORTLAND)

    site3 = Site(id=3,
                 capacity=100.0,
                 panels=155,
                 address="9585 SW Washington Sq.",
                 city="Beaverton",
                 state="OR",
                 postal_code="97223",
                 coordinate=BEAVERTON)

    site_geo_dao.insert_many(site1, site2, site3)
    query = GeoQuery(coordinate=PORTLAND, radius=1, radius_unit=GeoUnit.MI)
    assert site_geo_dao.find_by_geo(query) == {site1, site2}
