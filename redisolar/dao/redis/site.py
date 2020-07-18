from redisolar.dao.base import SiteDaoBase
from redisolar.dao.base import SiteNotFound
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.models import Site
from redisolar.schema import FlatSiteSchema
from typing import Set


class SiteDaoRedis(SiteDaoBase, RedisDaoBase):
    """SiteDaoRedis persists Site models to Redis.

    This class allows persisting (and querying for) Sites in Redis.
    """
    def insert(self, site: Site, **kwargs):
        """Insert a Site into Redis."""
        hash_key = self.key_schema.site_hash_key(site.id)
        site_ids_key = self.key_schema.site_ids_key()
        client = kwargs.get('pipeline', self.redis)
        client.hset(hash_key, mapping=FlatSiteSchema().dump(site))
        client.sadd(site_ids_key, site.id)

    def insert_many(self, *sites: Site, **kwargs) -> None:
        for site in sites:
            self.insert(site, **kwargs)

    def find_by_id(self, site_id: int, **kwargs) -> Site:
        """Find a Site by ID in Redis."""
        hash_key = self.key_schema.site_hash_key(site_id)
        site_hash = self.redis.hgetall(hash_key)

        if not site_hash:
            raise SiteNotFound()

        return FlatSiteSchema().load(site_hash)

    def find_all(self, **kwargs) -> Set[Site]:
        """Find all Sites in Redis."""
        # Challenge #1 solution.
        site_hashes = []
        site_ids_key = self.key_schema.site_ids_key()
        site_ids = self.redis.smembers(site_ids_key)

        for site_id in site_ids:
            key = self.key_schema.site_hash_key(site_id)
            site_hashes.append(self.redis.hgetall(key))

        return {FlatSiteSchema().load(site_hash) for site_hash in site_hashes}

    def find_all_pipeline(self, **kwargs) -> Set[Site]:
        """Find all Sites in Redis using a pipeline.

        Alternative Challenge #1 solution: pipelines.
        ---------------------------------------------
        We haven't introduced pipelines yet, so feel free to come back to this
        section next week. However, note that with enough latency between you
        and your Redis server, the solution code included this week will be
        unusably slow.

        The "correct" way to make many requests to Redis is to use a pipeline.
        The following alternative implementation of find_all() does just that.
        """
        site_ids_key = self.key_schema.site_ids_key()
        site_ids = self.redis.smembers(site_ids_key)

        p = self.redis.pipeline()
        for site_id in site_ids:
            key = self.key_schema.site_hash_key(site_id)
            p.hgetall(key)
        site_hashes = p.execute()

        return {FlatSiteSchema().load(site_hash) for site_hash in site_hashes}
