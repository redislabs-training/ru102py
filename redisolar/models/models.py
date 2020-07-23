import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List
from typing import Union
from typing import Any

import marshmallow
from marshmallow_dataclass import NewType


def deserialize_timestamp(v: str) -> datetime.datetime:
    """
    Convert a timestamp, stored either as a str or float, into a datetime.

    Raises a TypeError if the v cannot be converted to a float.
    """
    safe_v = float(v)
    return datetime.datetime.fromtimestamp(safe_v)


def serialize_timestamp(val: Any) -> str:
    """
    Serialize a value to a UNIX timestamp.

    If the object has a 'timestamp' method, call that method
    to obtain the timestamp.

    Otherwise, assume the value is already a timestamp.
    """
    try:
        return val.timestamp()
    except AttributeError:
        return str(val)


class DateTime(marshmallow.fields.DateTime):
    """
    Extend DateTime support to add a "timestamp" format.

    The "timestamp" format serializes and deserializes datetime
    to and from UNIX timestamps.
    """

    SERIALIZATION_FUNCS = marshmallow.fields.DateTime.SERIALIZATION_FUNCS.copy()
    DESERIALIZATION_FUNCS = marshmallow.fields.DateTime.DESERIALIZATION_FUNCS.copy()
    SERIALIZATION_FUNCS['timestamp'] = serialize_timestamp
    DESERIALIZATION_FUNCS['timestamp'] = deserialize_timestamp

    def _serialize(self, value, attr, obj, **kwargs):
        """
        When we serialize a UNIX timestamp, return it as a float.

        Without doing this, we'd return UNIX timestamps as strings, which
        isn't quite what we want.
        """
        result = super()._serialize(value, attr, obj, **kwargs)
        data_format = self.format or self.DEFAULT_FORMAT

        if data_format == 'timestamp':
            return float(result)
        return result


# A field that serializes datetime objects as UNIX timestamps.
TimestampField = NewType("TimestampField",
                         datetime.datetime,
                         field=DateTime,
                         format="timestamp")


class MetricUnit(Enum):
    """Supported measurement metrics."""
    WH_GENERATED = "whG"
    WH_USED = "whU"
    TEMP_CELSIUS = "tempC"


class GeoUnit(Enum):
    """Geographic units available for geo queries."""
    M = "m"
    KM = "km"
    MI = "mi"
    FT = "ft"


@dataclass(frozen=True, eq=True)
class Coordinate:
    """A coordinate pair."""
    lng: float
    lat: float


@dataclass(frozen=True, eq=True)
class Site:
    """A solar power installation."""
    id: int
    capacity: float
    panels: int
    address: str
    city: str
    state: str
    postal_code: str
    coordinate: Union[Coordinate, None] = None


@dataclass(frozen=True, eq=True)
class SiteCapacityTuple:
    """Capacity at a site."""
    capacity: float
    site_id: int


@dataclass(frozen=True, eq=True)
class CapacityReport:
    """A site capacity report."""
    highest_capacity: List[SiteCapacityTuple]
    lowest_capacity: List[SiteCapacityTuple]


@dataclass(frozen=True, eq=True)
class GeoQuery:
    """Parameters for a geo query."""
    coordinate: Coordinate
    radius: float
    radius_unit: GeoUnit
    only_excess_capacity: bool = False


@dataclass(frozen=True, eq=True)
class Measurement:
    """A measurement taken for a site."""
    site_id: int
    value: float
    metric_unit: MetricUnit
    timestamp: TimestampField


@dataclass(frozen=True, eq=True)
class MeterReading:
    """A reading taken from a site."""
    site_id: int
    wh_used: float
    wh_generated: float
    temp_c: float
    timestamp: TimestampField

    @property
    def current_capacity(self):
        return self.wh_generated - self.wh_used


@dataclass(frozen=True, eq=True)
class Plot:
    """A plot of measurements."""
    measurements: List[Measurement]
    name: str


@dataclass(frozen=True, eq=True)
class SiteStats:
    """Reporting stats for a site."""
    last_reporting_time: datetime.datetime
    meter_reading_count: int
    max_wh_generated: float
    min_wh_generated: float
    max_capacity: float

    # Make commonly-referenced SiteStats fields available.
    LAST_REPORTING_TIME = "last_reporting_time"
    COUNT = "meter_reading_count"
    MAX_WH = "max_wh_generated"
    MIN_WH = "min_wh_generated"
    MAX_CAPACITY = "max_capacity"
