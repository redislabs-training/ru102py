import datetime

import pytest

from redisolar.dao.base import SiteNotFound
from redisolar.dao.redis import CapacityReportDaoRedis
from redisolar.dao.redis import SiteGeoDaoRedis
from redisolar.models import Coordinate
from redisolar.models import GeoQuery
from redisolar.models import GeoUnit
from redisolar.models import MeterReading
from redisolar.models import Site

PORTLAND = Coordinate(lat=45.523064, lng=-122.676483)
BEAVERTON = Coordinate(lat=45.485168, lng=-122.804489)


@pytest.fixture
def site_geo_dao(redis, key_schema):
    yield SiteGeoDaoRedis(redis, key_schema)


@pytest.fixture
def capacity_dao(redis, key_schema):
    yield CapacityReportDaoRedis(redis, key_schema)


def test_does_not_exist(site_geo_dao):
    with pytest.raises(SiteNotFound):
        site_geo_dao.find_by_id(0)


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


def test_find_by_geo_with_excess_capacity(site_geo_dao, capacity_dao):
    site1 = Site(id=1,
                 capacity=10.0,
                 panels=100,
                 address="100 SE Pine St.",
                 city="Portland",
                 state="OR",
                 postal_code="97202",
                 coordinate=PORTLAND)

    site_geo_dao.insert(site1)

    # Check that this site is returned when we're not looking for excess capacity.
    query = GeoQuery(coordinate=PORTLAND, radius=1, radius_unit=GeoUnit.MI)
    assert site_geo_dao.find_by_geo(query) == {site1}

    # Simulate changing a meter reading with no excess capacity.
    reading = MeterReading(site_id=site1.id,
                           wh_used=1.0,
                           wh_generated=0.0,
                           temp_c=10,
                           timestamp=datetime.datetime.now())
    capacity_dao.update(reading)

    # In this case, no sites are returned for an excess capacity query.
    query = GeoQuery(coordinate=PORTLAND,
                     radius=1,
                     radius_unit=GeoUnit.MI,
                     only_excess_capacity=True)
    sites = site_geo_dao.find_by_geo(query)
    assert len(sites) == 0

    # Simulate changing a meter reading indicating excess capacity.
    reading = MeterReading(site_id=site1.id,
                           wh_used=1.0,
                           wh_generated=2.0,
                           temp_c=10,
                           timestamp=datetime.datetime.now())
    capacity_dao.update(reading)

    # Add more Sites -- none with excess capacity -- to make the test more
    # realistic.
    for i in range(2, 20, 1):  # Site 1 is our expected site - skip it!
        site = Site(id=i,
                    capacity=10,
                    panels=100,
                    address=f"100{i} SE Pine St.",
                    city="Portland",
                    state="OR",
                    postal_code="97202",
                    coordinate=PORTLAND)

        site_geo_dao.insert(site)

        reading = MeterReading(site_id=i,
                               wh_used=i,
                               wh_generated=0,
                               temp_c=10,
                               timestamp=datetime.datetime.now())
        capacity_dao.update(reading)

    # In this case, one site is returned on the excess capacity query
    sites = site_geo_dao.find_by_geo(query)
    assert site1 in sites
