from flask_restful import abort

from redisolar.api.base import DaoResource
from redisolar.schema import SiteSchema


class SiteListResource(DaoResource):
    def get(self):
        return SiteSchema(many=True).dump(self.dao.find_all())


class SiteResource(DaoResource):
    def get(self, site_id):
        site = self.dao.find_by_id(site_id)
        if not site:
            return abort(404, message=f"Site {site_id} does not exist")
        return SiteSchema().dump(site)
