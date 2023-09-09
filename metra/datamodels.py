import datetime
import typing
from typing import Any
from typing import TypedDict
from typing import NamedTuple
from typing import List, Dict, Union, Optional

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
    
class StopTimeRaw(TypedDict):
    trip_id: str
    arrival_time: str
    departure_time: str
    stop_id: str
    stop_sequence: int
    pickup_type: int
    drop_off_type: int
    center_boarding: int
    south_boarding: int
    bikes_allowed: int
    notice: int

class Trip(TypedDict):
    route_id: str
    service_id: str
    trip_id: str
    trip_headsign: str
    block_id: str
    shape_id: str
    direction_id: int
    
class Shape(TypedDict):
    shape_id: str
    shape_pt_lat: float
    shape_pt_lon: float
    shape_pt_sequence: int
    
class CalendarItem(TypedDict):
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

class CalendarException(TypedDict):
    service_id: str
    date: str
    exception_type: int

class _TimeData(NamedTuple):
    dt: datetime.datetime
    string: str

# ----------------------------------------
# Data models for RealTime GTFS responses
# ----------------------------------------
# Time Format -> %Y-%m-%dT%H:%M:%S.%fZ
TimestampData = TypedDict("Timestamp", {"low": str, "high": int, "unsigned": Optional[bool]})
StopTimeUpdate = TypedDict("StopTimeUpdate", {"delay": int, "time": TimestampData, "uncertainty": int})
StopTimeEvent = TypedDict("StopTimeEvent", {"stop_sequence": int, "stop_id": str, "arrival": StopTimeUpdate, "departure": StopTimeUpdate, "schedule_relationship": int })
VehicleDescriptor = TypedDict("VehicleDescriptor", {"id": str, "label": Optional[str], "license_plate": Optional[str]})

TripDescriptor = TypedDict("TripDescriptor", {
    "trip_id": str,
    "route_id": str,
    "direction_id": Optional[Union[int,str]],
    "start_time": str,
    "start_date": str,
    "schedule_relationship": int
})

TripUpdate = TypedDict("TripUpdate", {
    "trip": TripDescriptor,
    "vehicle": VehicleDescriptor,
    "stop_time_update": typing.List[StopTimeEvent],
    "timestamp": TimestampData,
    "delay": Optional[int],
    "position": Optional["PositionRT"]
})

class TripUpdateRT(TypedDict):
    id: str
    is_deleted: bool
    trip_update: TripUpdate
    vehicle: Optional[Any]
    alert: Optional[Any]


Position = TypedDict("Position", {"latitude": float, "longitude": float, "bearing": Optional[int], "odometer": Optional[Any], "speed": Optional[Any]})
VehiclePosition = TypedDict("VehiclePosition", {
    "trip": TripDescriptor,
    "vehicle": VehicleDescriptor,
    "position": Position,
    "current_stop_sequence": Optional[int],
    "stop_id": Optional[str],
    "current_status": int,
    "timestamp": TimestampData,
    "congestion_level": Optional[Any],
    "occupancy_status": Optional[Any]
})

class PositionRT(TypedDict):
    id: str
    is_deleted: bool
    trip_update: Optional[Any]
    vehicle: VehiclePosition
    alert: Optional[Any]

EntitySelector = List[
    TypedDict("Entity", {
        "agency_id": str, 
        "route_id": str, 
        "route_type": Optional[str], 
        "trip": Optional[TripDescriptor], 
        "stop_id": Optional[str]
    })
]
Translation = TypedDict("Translation", {"text": str, "language": str})
TranslatedString = TypedDict("TranslatedString", {"translation": List[Translation]})

_SingleTimestamp = TypedDict("_SingleTimestamp", {"low": str})
TimeRange = List[TypedDict("TimeData", {"start": _SingleTimestamp, "end": _SingleTimestamp})]

Alert = TypedDict("Alert", {
    "active_period": TimeRange,
    "informed_entity": EntitySelector,
    "cause": int,
    "effect": int,
    "url": TranslatedString,
    "header_text": TranslatedString,
    "description_text": TranslatedString
})
    
class AlertRT(TypedDict):
    id: str
    is_deleted: bool
    trip_update: Optional[TripUpdate]
    vehicle: Optional[VehiclePosition]
    alert: Alert


