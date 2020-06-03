import datetime

from redisolar.models import MetricUnit

DEFAULT_KEY_PREFIX = "ru102py-test"


def prefixed_key(f):
    def prefixed_method(self, *args, **kwargs):
        key = f(self, *args, **kwargs)
        return f"{self.prefix}:{key}"

    return prefixed_method


class KeySchema:
    """
    Methods to generate key names for Redis data structures.

    These key names are used by the DAO classes. This class therefore contains
    a reference to all possible key names used by this application.
    """
    def __init__(self, prefix: str = DEFAULT_KEY_PREFIX):
        self.prefix = prefix

    @prefixed_key
    def site_hash_key(self, site_id):
        """
        sites:info:[site_id]
        Redis type: hash
        """
        return f"sites:info:{site_id}"

    @prefixed_key
    def site_ids_key(self):
        """
        sites:ids
        Redis type: set
        """
        return "sites:ids"

    @prefixed_key
    def site_geo_key(self):
        """
        sites:geo
        Redis type: geo
        """
        return "sites:geo"

    @prefixed_key
    def site_stats_key(self, site_id, day):
        """
        sites:stats:[year-month-day]:[site_id]
        Redis type: sorted set
        """
        return f"sites:stats:{day.strftime('%Y-%m-%d')}:{site_id}"

    @prefixed_key
    def capacity_ranking_key(self):
        """
        sites:capacity:ranking
        Redis type: sorted set
        """
        return "sites:capacity:ranking"

    @prefixed_key
    def day_metric_key(self, site_id: int, unit: MetricUnit, time: datetime.datetime):
        """
        metric:[unit-name]:[year-month-day]:[site_id]
        Redis type: sorted set
        """
        return f"metric:{unit.value}:{time.strftime('%Y-%m-%d')}:{site_id}"

    @prefixed_key
    def global_feed_key(self):
        """
        sites:feed
        Redis type: stream
        """
        return "sites:feed"

    @prefixed_key
    def feed_key(self, site_id):
        """
        sites:feed:[site_id]
        Redis type: stream
        """
        return f"sites:feed:{site_id}"

    @prefixed_key
    def fixed_rate_limiter_key(self, name: str, minute_block: int,
                               max_hits: float) -> str:
        """
        limiter:[name]:[duration]:[max_hits]
        Redis type: string of type integer
        """
        return f"limiter:{name}:{minute_block}:{max_hits}"

    @prefixed_key
    def sliding_window_rate_limiter_key(self, name: str, window_size_ms: int,
                                        max_hits: float) -> str:
        """
        limiter:[name]:[window_size_ms]:[max_hits]
        Redis type: string of type integer
        """
        return f"limiter:{name}:{window_size_ms}:{max_hits}"
