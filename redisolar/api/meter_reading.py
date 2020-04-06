from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from flask_restful import Resource
from marshmallow import fields
from webargs.flaskparser import use_args

from redisolar.api.base import DaoResource
from redisolar.models import MeterReading
from redisolar.schema import MeterReadingsSchema

MAX_RECENT_FEEDS = 1000
DEFAULT_RECENT_FEEDS = 100


def get_feed_count(count: Optional[int]):
    """Decide a safe number of feeds to return."""
    if count is None or count < 0:
        return DEFAULT_RECENT_FEEDS
    if count > MAX_RECENT_FEEDS:
        return MAX_RECENT_FEEDS
    return count


class GlobalMeterReadingResource(Resource):
    """A RESTful resource representing meter readings for all sites."""
    def __init__(self, meter_reading_dao: Any, feed_dao: Any):
        self.meter_reading_dao = meter_reading_dao
        self.feed_dao = feed_dao

    @use_args(MeterReadingsSchema)
    def post(self, meter_readings: Dict[str, List[MeterReading]]) -> Tuple[str, int]:
        """Create a new meter reading."""
        for reading in meter_readings['readings']:
            self.meter_reading_dao.add(reading)
        return "Accepted", 202

    @use_args({"count": fields.Int()}, location="query")
    def get(self, args: Dict[str, int]) -> Dict[str, Dict]:
        """Get a list of meter readings."""
        count = args.get('count')
        readings = self.feed_dao.get_recent_global(get_feed_count(count))
        return MeterReadingsSchema().dump({"readings": readings})


class SiteMeterReadingResource(DaoResource):
    """A RESTful resource representing meter readings for specific sites."""
    @use_args({"count": fields.Int()}, location="query")
    def get(self, args, site_id):
        """Get recent meter readings for a specific site."""
        count = args.get('count')
        readings = self.dao.get_recent_for_site(site_id, get_feed_count(count))
        return MeterReadingsSchema().dump({"readings": readings})
