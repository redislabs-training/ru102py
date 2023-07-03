import pytest

from redisolar.dao.base import SiteNotFound
from redisolar.dao.redis import SiteDaoRedis
from redisolar.models import Site


@pytest.fixture
def site_dao(redis, key_schema):
    yield SiteDaoRedis(redis, key_schema)


def test_does_not_exist(site_dao):
    with pytest.raises(SiteNotFound):
        site_dao.find_by_id(0)


def test_insert(redis, site_dao):
    site = Site(id=1,
                capacity=10.0,
                panels=100,
                address="100 SE Pine St.",
                city="Portland",
                state="OR",
                postal_code="97202")

    site_dao.insert(site)
    assert site_dao.find_by_id(1) == site


def test_insert_many(site_dao):
    site1 = Site(id=1,
                 capacity=10.0,
                 panels=100,
                 address="100 SE Pine St.",
                 city="Portland",
                 state="OR",
                 postal_code="97202")

    site2 = Site(id=2,
                 capacity=25.0,
                 panels=110,
                 address="101 SW Ankeny",
                 city="Portland",
                 state="OR",
                 postal_code="97203")

    site3 = Site(id=3,
                 capacity=100.0,
                 panels=155,
                 address="201 SE Burnside",
                 city="Portland",
                 state="OR",
                 postal_code="97204")

    site_dao.insert_many(site1, site2, site3)

    assert site_dao.find_by_id(1) == site1
    assert site_dao.find_by_id(2) == site2
    assert site_dao.find_by_id(3) == site3


def test_find_by_id_existing_site(site_dao):
    site_id = 1
    site = Site(id=site_id,
                capacity=10.0,
                panels=100,
                address="100 SE Pine St.",
                city="Portland",
                state="OR",
                postal_code="97202")

    site_dao.insert(site)
    found_site = site_dao.find_by_id(site_id)

    assert found_site == site


def test_find_all(site_dao):
    site1 = Site(id=1,
                 capacity=10.0,
                 panels=100,
                 address="100 SE Pine St.",
                 city="Portland",
                 state="OR",
                 postal_code="97202")

    site2 = Site(id=2,
                 capacity=25.0,
                 panels=110,
                 address="101 SW Ankeny",
                 city="Portland",
                 state="OR",
                 postal_code="97203")

    site3 = Site(id=3,
                 capacity=100.0,
                 panels=155,
                 address="201 SE Burnside",
                 city="Portland",
                 state="OR",
                 postal_code="97204")

    site_dao.insert_many(site1, site2, site3)
    assert site_dao.find_all() == {site1, site2, site3}
