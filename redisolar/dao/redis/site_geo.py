from typing import Set

from redisolar.dao.base import SiteGeoDaoBase
from redisolar.dao.redis.base import RedisDaoBase
from redisolar.models import GeoQuery
from redisolar.models import Site
from redisolar.schema import FlatSiteSchema

CAPACITY_THRESHOLD = 0.2


class SiteGeoDaoRedis(SiteGeoDaoBase, RedisDaoBase):
    """SiteGeoDaoRedis persists and queries Sites in Redis."""
    def insert(self, site: Site, **kwargs):
        """Insert a Site into Redis."""
        hash_key = self.key_schema.site_hash_key(site.id)
        self.redis.hset(hash_key, mapping=FlatSiteSchema().dump(site))  # type: ignore
        client = kwargs.get('pipeline', self.redis)

        if not site.coordinate:
            raise ValueError("Site coordinates are required for Geo insert")

        client.geoadd(  # type: ignore
            self.key_schema.site_geo_key(), site.coordinate.lng, site.coordinate.lat,
            site.id)

    def insert_many(self, *sites: Site, **kwargs) -> None:
        """Insert multiple Sites into Redis."""
        for site in sites:
            self.insert(site, **kwargs)

    def find_by_id(self, site_id: int, **kwargs) -> Site:
        """Find a Site by ID in Redis."""
        hash_key = self.key_schema.site_hash_key(site_id)
        site_hash = self.redis.hgetall(hash_key)
        return FlatSiteSchema().load(site_hash)

    def _find_by_geo(self, query: GeoQuery, **kwargs) -> Set[Site]:
        site_ids = self.redis.georadius(  # type: ignore
            self.key_schema.site_geo_key(), query.coordinate.lng, query.coordinate.lat,
            query.radius, query.radius_unit.value)
        sites = [
            self.redis.hgetall(self.key_schema.site_hash_key(site_id))
            for site_id in site_ids
        ]
        return {FlatSiteSchema().load(site) for site in sites}

    # Challenge #5
    def _find_by_geo_with_capacity_noop(self, query: GeoQuery) -> Set[Site]:
        return set()

    def _find_by_geo_with_capacity(self, query: GeoQuery, **kwargs) -> Set[Site]:
        # START Challenge #5
        # Your task: Get the sites matching the GEO query.
        coord = query.coordinate
        site_ids = self.redis.georadius(  # type: ignore
            self.key_schema.site_geo_key(), coord.lng, coord.lat, query.radius,
            query.radius_unit.value)
        # END Challenge #5

        p = self.redis.pipeline(transaction=False)

        # START Challenge #5
        #
        # Your task: Populate a dictionary called "scores" whose keys are site
        # IDs and whose values are the site's capacity.
        #
        # Make sure to run any Redis commands against the Pipeline object
        # "p" for better performance.
        for site_id in site_ids:
            p.zscore(self.key_schema.capacity_ranking_key(), site_id)
        site_id_ints = [int(site_id) for site_id in site_ids]
        scores = dict(zip(site_id_ints, reversed(p.execute())))
        # END Challenge #5

        sites_with_capacity = {
            site_id for site_id in site_id_ints
            if scores[site_id] and scores[site_id] > CAPACITY_THRESHOLD
        }

        for site_id in sites_with_capacity:
            p.hgetall(self.key_schema.site_hash_key(site_id))
        site_hashes = p.execute()

        return {FlatSiteSchema().load(site) for site in site_hashes}

    def find_by_geo(self, query: GeoQuery, **kwargs) -> Set[Site]:
        """Find Sites using a geographic query."""
        if query.only_excess_capacity:
            return self._find_by_geo_with_capacity(query)
        return self._find_by_geo(query)

    def find_all(self, **kwargs) -> Set[Site]:
        """Find all Sites."""
        site_ids = self.redis.zrange(self.key_schema.site_geo_key(), 0, -1)
        sites = set()
        p = self.redis.pipeline(transaction=False)
        for site_id in site_ids:
            p.hgetall(self.key_schema.site_hash_key(site_id))
        site_hashes = p.execute()

        for site_hash in [h for h in site_hashes if h is not None]:
            site_model = FlatSiteSchema().load(site_hash)
            sites.add(site_model)

        return sites
