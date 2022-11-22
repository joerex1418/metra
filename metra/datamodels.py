import datetime
from typing import TypedDict
from typing import NamedTuple

class Route(TypedDict):
    route_id: str
    route_short_name: str
    route_long_name: str
    agency_id: str
    route_type: int
    route_color: str
    route_text_color: str
    route_url: str

class Stop(TypedDict):
    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float
    zone_id: str
    stop_url: str
    wheelchair_boarding: str

class StopTime(TypedDict):
    trip_id: str
    arrival_time: datetime.datetime
    arrival_time_str: str
    stop_id: str
    stop_sequence: int
    pickup_type: int
    drop_off_type: int
    center_boarding: int
    south_boarding: int
    bikes_allowed: int
    notice: int

class CalendarService(TypedDict):
    service_id: str
    monday: int
    tuesday: int
    wednesday: int
    thursday: int
    friday: int
    saturday: int
    sunday: int
    start_date: str
    end_date: str

class Trip(TypedDict):
    route_id: str
    service_id: str
    trip_id: str
    trip_headsign: str
    block_id: str
    shape_id: str
    direction_id: int

class _TimeData(NamedTuple):
    dt: datetime.datetime
    string: str
