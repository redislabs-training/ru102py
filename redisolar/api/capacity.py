from typing import Dict

from webargs import fields
from webargs.flaskparser import use_args

from redisolar.api.base import DaoResource
from redisolar.schema import CapacityReportSchema

DEFAULT_LIMIT = 10


class CapacityReportResource(DaoResource):
    """A RESTful resource representing a capacity report."""
    @use_args({"limit": fields.Int(missing=DEFAULT_LIMIT)}, location='query')
    def get(self, args) -> Dict:
        """Get a capacity report."""
        report = self.dao.get_report(args["limit"])
        return CapacityReportSchema().dump(report)
