import pytest

from redisolar.api import api
from redisolar.api import SiteGeoListResource
from redisolar.api import SiteGeoResource
from redisolar.dao.redis import SiteGeoDaoRedis
from redisolar.models import Coordinate
from redisolar.models import GeoUnit
from redisolar.models import Site
from redisolar.schema import SiteSchema

PORTLAND = Coordinate(lat=45.523064, lng=-122.676483)
BEAVERTON = Coordinate(lat=45.485168, lng=-122.804489)


@pytest.fixture
def geo_enabled_app(redis, key_schema, app):
    api.add_resource(SiteGeoListResource,
                     '/sites/geo',
                     resource_class_args=(SiteGeoDaoRedis(redis, key_schema), ))
    api.add_resource(SiteGeoResource,
                     '/sites/geo/<int:site_id>',
                     resource_class_args=(SiteGeoDaoRedis(redis, key_schema), ))
    yield app


@pytest.fixture
def sites(redis, key_schema):
    site_dao = SiteGeoDaoRedis(redis, key_schema)

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

    site_dao.insert_many(site1, site2, site3)

    yield [site1, site2, site3]


def test_find_by_id(sites, client, geo_enabled_app):
    site_id = 1
    found_site = client.get(f'/sites/geo/{site_id}').json
    assert SiteSchema().load(found_site) == sites[0]


def test_find_all(sites, client, geo_enabled_app):
    resp = client.get('/sites/geo').json
    resp_sites = SiteSchema(many=True).load(resp)
    assert set(resp_sites) == set(sites)


def test_find_by_geo(sites, client, geo_enabled_app):
    resp = client.get(
        f"/sites/geo?lat={PORTLAND.lat}&lng={PORTLAND.lng}&radius=1&radius_unit={GeoUnit.M.value}"
    ).json
    resp_sites = SiteSchema(many=True).load(resp)
    portland_sites = {
        Site(id=1,
             capacity=10.0,
             panels=100,
             address="100 SE Pine St.",
             city="Portland",
             state="OR",
             postal_code="97202",
             coordinate=PORTLAND),
        Site(id=2,
             capacity=25.0,
             panels=110,
             address="101 SW Ankeny",
             city="Portland",
             state="OR",
             postal_code="97203",
             coordinate=PORTLAND)
    }
    assert set(resp_sites) == set(portland_sites)
