import abc
import datetime
from typing import List, Deque
from typing import Set

from redisolar.models import CapacityReport
from redisolar.models import GeoQuery
from redisolar.models import Measurement
from redisolar.models import MeterReading
from redisolar.models import MetricUnit
from redisolar.models import Site
from redisolar.models import SiteStats


class SiteDaoBase(abc.ABC):
    @abc.abstractmethod
    def insert(self, site: Site, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def insert_many(self, *sites: Site, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def find_by_id(self, site_id: int, **kwargs) -> Site:
        pass

    @abc.abstractmethod
    def find_all(self, **kwargs) -> Set[Site]:
        pass


class SiteGeoDaoBase(SiteDaoBase):
    @abc.abstractmethod
    def find_by_geo(self, query: GeoQuery, **kwargs) -> Set[Site]:
        pass


class SiteStatsDaoBase(abc.ABC):
    @abc.abstractmethod
    def find_by_id(self,
                   site_id: int,
                   day: datetime.datetime = None,
                   **kwargs) -> SiteStats:
        pass

    @abc.abstractmethod
    def update(self, meter_reading: MeterReading, **kwargs) -> None:
        pass


class CapacityDaoBase(abc.ABC):
    @abc.abstractmethod
    def update(self, meter_reading: MeterReading, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def get_report(self, limit: int, **kwargs) -> CapacityReport:
        pass

    @abc.abstractmethod
    def get_rank(self, site_id: int, **kwargs) -> float:
        pass


class MetricDaoBase(abc.ABC):
    @abc.abstractmethod
    def insert(self, meter_reading: MeterReading, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def get_recent(self, site_id: int, unit: MetricUnit, time: datetime.datetime,
                   limit: int, **kwargs) -> Deque[Measurement]:
        pass


class FeedDaoBase(abc.ABC):
    @abc.abstractmethod
    def insert(self, meter_reading: MeterReading, **kwargs) -> None:
        pass

    @abc.abstractmethod
    def get_recent_global(self, limit: int, **kwargs) -> List[MeterReading]:
        pass

    @abc.abstractmethod
    def get_recent_for_site(self, site_id: int, limit: int,
                            **kwargs) -> List[MeterReading]:
        pass


class MeterReadingDaoBase(abc.ABC):
    @abc.abstractmethod
    def add(self, meter_reading: MeterReading, **kwargs) -> None:
        pass


class RateLimiterDaoBase(abc.ABC):
    @abc.abstractmethod
    def hit(self, name: str) -> None:
        pass
