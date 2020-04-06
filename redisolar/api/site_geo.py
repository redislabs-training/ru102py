from flask_restful import abort
from marshmallow import validate
from webargs import fields
from webargs.flaskparser import use_args

from redisolar.api.base import DaoResource
from redisolar.models import Coordinate
from redisolar.models import GeoQuery
from redisolar.models import GeoUnit
from redisolar.schema import SiteSchema

DEFAULT_RADIUS = 10.0
DEFAULT_GEO_UNIT = GeoUnit.KM

SITE_LIST_ARGS = {
    "lat":
    fields.Str(),
    "lng":
    fields.Str(),
    "radius":
    fields.Float(missing=DEFAULT_RADIUS),
    "radius_unit":
    fields.Str(missing=DEFAULT_GEO_UNIT.value,
               validate=validate.OneOf([u.value for u in GeoUnit])),
    "only_excess_capacity":
    fields.Bool(missing=False)
}


class SiteGeoListResource(DaoResource):
    @use_args(SITE_LIST_ARGS, location='query')
    def get(self, args):
        lng = args.get('lng')
        lat = args.get('lat')
        no_coordinates = lng is None and lat is None
        coordinates_provided = lng is not None and lat is not None

        if no_coordinates:
            return SiteSchema(many=True).dump(self.dao.find_all())
        if coordinates_provided:
            coord = Coordinate(lng=lng, lat=lat)
            query = GeoQuery(coordinate=coord,
                             radius=args['radius'],
                             radius_unit=GeoUnit(args['radius_unit']),
                             only_excess_capacity=args['only_excess_capacity'])
            return SiteSchema(many=True).dump(self.dao.find_by_geo(query))
        return 404


class SiteGeoResource(DaoResource):
    def get(self, site_id):
        site = self.dao.find_by_id(site_id)
        if not site:
            return abort(404, message=f"Site {site_id} does not exist")
        return SiteSchema().dump(site)
