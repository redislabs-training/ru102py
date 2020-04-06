import datetime
from typing import Dict

from webargs import fields
from webargs.flaskparser import use_args

from redisolar.api.base import DaoResource
from redisolar.models import MetricUnit
from redisolar.models import Plot
from redisolar.schema import PlotsSchema

DEFAULT_METRIC_COUNT = 120


class MetricsResource(DaoResource):
    """A RESTful resource representing site metrics."""
    @use_args({"count": fields.Int(missing=DEFAULT_METRIC_COUNT)}, location='query')
    def get(self, args, site_id) -> Dict[str, Dict]:
        """Get recent metrics for a site."""
        generated = self.dao.get_recent(site_id, MetricUnit.WH_GENERATED,
                                        datetime.datetime.utcnow(), args.get("count"))
        used = self.dao.get_recent(site_id, MetricUnit.WH_USED,
                                   datetime.datetime.utcnow(), args.get("count"))

        plots = [Plot(name="Watt-Hours Generated", measurements=generated),
                 Plot(name="Watt-Hours Used", measurements=used)]

        return PlotsSchema().dump({"plots": plots})
