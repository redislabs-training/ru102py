import json
import os

import click
from progress.bar import Bar
from flask import current_app

from redisolar.core import get_redis_timeseries_connection
from redisolar.core import SampleDataGenerator  # pylint: disable=unused-import
from redisolar.dao.redis import SiteDaoRedis
from redisolar.dao.redis import SiteGeoDaoRedis
from redisolar.schema import FlatSiteSchema
from redisolar.dao.redis.key_schema import KeySchema

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_SITES_FILENAME = os.path.join(ROOT_DIR, "fixtures", "sites.json")


@click.option(
    "-f",
    "--filename",
    default=DEFAULT_SITES_FILENAME,
    help="The filename containing the JSON to load. (default: fixtures/sites.json)")
@click.option(
    "-t",
    "--delete-keys",
    default=False,
    is_flag=True,
    help="Delete any existing redisolar keys before loading")
def load(filename, delete_keys):
    """Load the specified JSON file into Redis"""
    conf = current_app.config
    hostname = conf['REDIS_HOST']
    port = conf['REDIS_PORT']
    key_prefix = conf['REDIS_KEY_PREFIX']
    key_schema = KeySchema(key_prefix)
    client = get_redis_timeseries_connection(hostname=hostname, port=port)
    site_dao = SiteDaoRedis(client, key_schema)
    site_geo_dao = SiteGeoDaoRedis(client, key_schema)

    if delete_keys:
        for key in client.scan_iter(f"{key_prefix}:*"):
            client.delete(key)

    with open(filename, 'r') as f:
        sites = [FlatSiteSchema().load(d) for d in json.loads(f.read())]

    sites_bar = Bar('Loading sites', max=len(sites))
    p = client.pipeline(transaction=False)
    for site in sites:
        sites_bar.next()
        site_dao.insert(site, pipeline=p)
        site_geo_dao.insert(site, pipeline=p)
    p.execute()

    print()
    sample_generator = SampleDataGenerator(client, sites, 1, key_schema)
    readings_bar = Bar('Generating metrics data', max=sample_generator.size)
    p = client.pipeline(transaction=False)
    for _ in sample_generator.generate(p):
        readings_bar.next()

    print("\nFinishing up...")
    p.execute()

    print("\nData load complete!")
