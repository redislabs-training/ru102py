import marshmallow
import marshmallow_dataclass

from redisolar.models import CapacityReport
from redisolar.models import MeterReading
from redisolar.models import Plot
from redisolar.models import Site
from redisolar.models import SiteStats
from redisolar.models import Measurement


class FlatCoordinateSchema(marshmallow.Schema):
    @marshmallow.pre_load
    def flat_to_nested_coordinate(self, in_data, **kwargs):
        # Ignore if this is a Coordinate object -- i.e. it only has
        # 'lat' and 'lng' keys.
        if list(in_data.keys()) == ['lat', 'lng']:
            return in_data

        # For all other objects, deserialize a flat coordinate pair
        # to a nested object.
        lat = in_data.pop('lat', None)
        lng = in_data.pop('lng', None)
        if lat and lng:
            in_data['coordinate'] = {'lat': lat, 'lng': lng}
        return in_data

    @marshmallow.post_dump
    def nested_to_flat(self, out_data, **kwargs):
        coordinate = out_data.pop('coordinate', None)
        if coordinate:
            out_data['lat'] = coordinate['lat']
            out_data['lng'] = coordinate['lng']
        return out_data


# This Site schema is used to serialize and deserialize a Site to and from a
# "flat" hash in Redis. That is, the Site's Coordinate is flattened to
# top-level "lat" and "lng" keys. This is because Redis Hashes cannot contain
# nested values.
FlatSiteSchema = marshmallow_dataclass.class_schema(Site, base_schema=FlatCoordinateSchema)

# This Site schema is used to serialize a Site to and from a nested JSON object
# used by the frontend to display site data.
SiteSchema = marshmallow_dataclass.class_schema(Site)

CapacityReportSchema = marshmallow_dataclass.class_schema(CapacityReport)
MeterReadingSchema = marshmallow_dataclass.class_schema(MeterReading)
PlotSchema = marshmallow_dataclass.class_schema(Plot)
SiteStatsSchema = marshmallow_dataclass.class_schema(SiteStats)
MeasurementSchema = marshmallow_dataclass.class_schema(Measurement)


class PlotsSchema(marshmallow.Schema):
    plots = marshmallow.fields.Nested(PlotSchema(many=True))


class MeterReadingsSchema(marshmallow.Schema):
    readings = marshmallow.fields.Nested(MeterReadingSchema(many=True))
