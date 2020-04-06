from typing import Set

from redisolar.models import Site
from redisolar.dao.base import SiteDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.schema import FlatSiteSchema


class SiteDaoRedis(SiteDaoBase, RedisDaoBase):
    """SiteDaoRedis persists Site models to Redis.

    This class allows persisting (and querying for) Sites in Redis.
    """
    def insert(self, site: Site):
        """Insert a Site into Redis."""
        hash_key = self.key_schema.site_hash_key(site.id)
        site_ids_key = self.key_schema.site_ids_key()
        self.redis.hmset(hash_key, FlatSiteSchema().dump(site))
        self.redis.sadd(site_ids_key, hash_key)

    def insert_many(self, *sites: Site) -> None:
        """Insert multiple Sites into Redis."""
        for site in sites:
            self.insert(site)

    def find_by_id(self, site_id: int) -> Site:
        """Find a Site by ID in Redis."""
        hash_key = self.key_schema.site_hash_key(site_id)
        site_hash = self.redis.hgetall(hash_key)
        return FlatSiteSchema().load(site_hash)

    def find_all(self) -> Set[Site]:
        """Find all Sites in Redis."""
        site_ids_key = self.key_schema.site_ids_key()
        site_keys = self.redis.smembers(site_ids_key)

        p = self.redis.pipeline()
        for site_key in site_keys:
            p.hgetall(site_key)
        site_hashes = p.execute()

        return {FlatSiteSchema().load(site_hash) for site_hash in site_hashes}
