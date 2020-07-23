import os
import signal

from flask import Blueprint
from flask_restful import Api
from redis import exceptions

from redisolar.api.capacity import CapacityReportResource
from redisolar.api.meter_reading import GlobalMeterReadingResource
from redisolar.api.meter_reading import SiteMeterReadingResource
from redisolar.api.metrics import MetricsResource
from redisolar.api.site import SiteListResource
from redisolar.api.site import SiteResource
from redisolar.api.site_geo import SiteGeoListResource
from redisolar.api.site_geo import SiteGeoResource
from redisolar.core.connections import get_redis_timeseries_connection
from redisolar.dao import CapacityReportDaoRedis
from redisolar.dao import FeedDaoRedis
from redisolar.dao import MeterReadingDaoRedis
from redisolar.dao import MetricDaoRedisTimeseries
from redisolar.dao import SiteDaoRedis
from redisolar.dao import SiteGeoDaoRedis
from redisolar.dao.redis.key_schema import KeySchema

blueprint = Blueprint("api", __name__)
api = Api(blueprint)


def configure(app):
    key_schema = KeySchema(app.config['REDIS_KEY_PREFIX'])
    redis_client = get_redis_timeseries_connection(app.config['REDIS_HOST'],
                                                   app.config['REDIS_PORT'])

    try:
        redis_client.ping()
    except exceptions.AuthenticationError:
        app.logger.error("Redis authentication failed. Make sure you set "
                         "$REDISOLAR_REDIS_PASSWORD to the correct password "
                         "for your Redis instance. Stopping server.")
        raise
    app.do_teardown_appcontext()
    if app.config.get('USE_GEO_SITE_API'):
        api.add_resource(SiteGeoListResource,
                         '/sites',
                         resource_class_args=(SiteGeoDaoRedis(redis_client,
                                                              key_schema), ))
        api.add_resource(SiteGeoResource,
                         '/sites/<int:site_id>',
                         resource_class_args=(SiteGeoDaoRedis(redis_client,
                                                              key_schema), ))
    else:
        api.add_resource(SiteListResource,
                         '/sites',
                         resource_class_args=(SiteDaoRedis(redis_client, key_schema), ))
        api.add_resource(SiteResource,
                         '/sites/<int:site_id>',
                         resource_class_args=(SiteDaoRedis(redis_client, key_schema), ))

    api.add_resource(CapacityReportResource,
                     '/capacity',
                     resource_class_args=(CapacityReportDaoRedis(
                         redis_client, key_schema), ))
    api.add_resource(GlobalMeterReadingResource,
                     '/meter_readings',
                     resource_class_args=(MeterReadingDaoRedis(redis_client, key_schema),
                                          FeedDaoRedis(redis_client, key_schema)))
    api.add_resource(SiteMeterReadingResource,
                     '/meter_readings/<int:site_id>',
                     resource_class_args=(FeedDaoRedis(redis_client, key_schema), ))
    api.add_resource(MetricsResource,
                     '/metrics/<int:site_id>',
                     resource_class_args=(MetricDaoRedisTimeseries(redis_client, key_schema), ))
