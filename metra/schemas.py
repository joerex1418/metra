import datetime as dt

import pandas as pd
from tabulate import tabulate as tab

# from .constants import METRA_BASE
# from .auth import METRA_API_KEY
# from .auth import METRA_SECRET_KEY

from .utils import get_publish_time
from .utils import get_last_local_publish

# Trips Response objects
class Trips:
    def __init__(self,resp:list[dict]):
        self.trips = [Trip(d) for d in resp]
        self.__column_format = "{:<20}{:<22}{:<10}{:<6}{:<6}"
        header = self.__column_format.format('id','headsign','direction','route','service')
        divider = '-' * len(header)
        rows = [self.__column_format.format(t.trip_id,t.trip_headsign,t.direction,t.route_id,t.service_id) for t in self.trips]
        self.__reprdata = '\n'.join(([header,divider] + rows))
        
    def __getitem__(self,idx):
        return self.trips[idx]
        
    def __iter__(self):
        return iter(self.trips)
    
    def __repr__(self) -> str:
        return self.__reprdata

class Trip:
    """Represents a single trip on the static schedule"""
    def __init__(self,data:dict):
        self.route_id = data.get('route_id','')
        self.service_id = data.get('service_id','')
        self.trip_id = data.get('trip_id','')
        self.trip_headsign = data.get('trip_headsign','')
        self.block_id = data.get('block_id','')
        self.shape_id = data.get('shape_id','')
        self.direction_id = data.get('direction_id',-1)
        self.direction = 'inbound' if self.direction_id == 1 else 'outbound'
            
    def __repr__(self) -> str:
        return f"<{self.trip_id} ({self.trip_headsign})>"

# Stops Response objects
class Stops:
    def __init__(self,resp:list[dict]):
        self.stops = [Stop(d) for d in resp]
        
    def __getitem__(self,idx):
        return self.stops[idx]
        
    def __iter__(self):
        return iter(self.stops)
    
    def search(self,query:str) -> None:
        query = query.lower()
        for stop in self.stops:
            if query in stop.name.lower():
                print('{:<20}{:<}'.format(stop.stop_id,stop.name))
            elif query in stop.stop_id.lower():
                print('{:<20}{:<}'.format(stop.stop_id,stop.name))

class Stop:
    def __init__(self,data:dict):
        self.stop_id: str = data.get('stop_id','')
        self.name: str = data.get('stop_name','')
        self.desc: str = data.get('stop_desc','')
        self.lat = data.get('stop_lat')
        self.lon = data.get('stop_lon')
        self.zone_id: str = data.get('zone_id','')
        self.url: str = data.get('stop_url','')
        self.has_wheelchair_boarding: bool = True if data.get('wheelchair_boarding',0) == 1 else False
    
    def __repr__(self) -> str:
        return f"<{self.stop_id} ({self.name})>"

# Stop Times Response objects
class StopTimes:
    """Detailed stop time info for today's scheduled trips"""
    def __init__(self,resp:list[dict]):
        published_date = get_last_local_publish()
        self.__base_dt = dt.datetime.combine(published_date.date(),time=dt.time(0,0,0))
        df = pd.DataFrame(resp).drop(columns=['departure_time'])
        df['arrival_time'] = df['arrival_time'].apply(lambda time: self.__convert_time_strings(time))
        self.__df = df
        self.stop_times = [StopTime(d) for d in resp]
        
    def __getitem__(self,idx):
        return self.stop_times[idx]
        
    def __iter__(self):
        return iter(self.stop_times)
    
    def df(self) -> pd.DataFrame:
        return self.__df
    
    def __convert_time_strings(self,time:str):
        hh, mm, ss = (int(time[:2]), int(time[3:5]), int(time[-2:]))
        return self.__base_dt + dt.timedelta(hours=hh,minutes=mm,seconds=ss)

class StopTime:
    def __init__(self,data:dict):
        self.trip_id = data.get('trip_id','')
        self.arrival_time = data.get('arrival_time','')
        self.departure_time = data.get('departure_time','')
        self.stop_id = data.get('stop_id','')
        self.stop_sequence: int = data.get('stop_sequence',-1)
        self.pickup_type = True if data.get('pickup_type',-1) == 1 else False
        self.drop_off_type = True if data.get('drop_off_type',-1) == 1 else False
        self.center_boarding = True if data.get('center_boarding',-1) == 1 else False
        self.south_boarding = True if data.get('south_boarding',-1) == 1 else False
        self.bikes_allowed = True if data.get('bikes_allowed',-1) == 1 else False
        self.notice = True if data.get('notice',-1) == 1 else False
        
    def __repr__(self) -> str:
        return f"<(SEQ: {self.stop_sequence}) {self.arrival_time} {self.stop_id}>"
    
    @property
    def arrival_datetime(self) -> dt.datetime:
        """Arrival time as a Python Datetime Object"""
        return dt.datetime.strptime(self.arrival_time,r"%H:%M:%S")
    
    @property
    def departure_datetime(self) -> dt.datetime:
        """Departure time as a Python Datetime Object"""
        return dt.datetime.strptime(self.departure_time,r"%H:%M:%S")

# Shapes Response objects
class Shapes:
    def __init__(self,resp:list[dict]):
        self.shapes = [Shape(d) for d in resp]
        
    def __getitem__(self,idx):
        return self.shapes[idx]
        
    def __iter__(self):
        return iter(self.shapes)

class Shape:
    def __init__(self,data:dict):
        self.shape_id: str = data.get('shape_id','')
        self.lat = data.get('shape_pt_lat')
        self.lon = data.get('shape_pt_lon')
        self.sequence = data.get('shape_pt_sequence')
    
    def __repr__(self) -> str:
        return f'<{self.shape_id} (SEQ NUM: {self.sequence})>'

# Routes Response objects
class Routes:
    def __init__(self,resp:list[dict]):
        self.routes = [Route(d) for d in resp]
        self.bnsf_railway: Route
        self.herritage_corridor: Route
        self.milwaukee_north: Route
        self.milwaukee_west: Route
        self.metra_electric: Route
        self.north_central_service: Route
        self.rock_island: Route
        self.southwest_service: Route
        self.union_pacific_north: Route
        self.union_pacific_northwest: Route
        self.union_pacific_west: Route
        
        self.__assign_routes()
        
        self.bnsf = self.bnsf_railway
        self.hc = self.herritage_corridor
        self.mn = self.milwaukee_north
        self.mw = self.milwaukee_west
        self.me = self.metra_electric
        self.ncs = self.north_central_service
        self.ri = self.rock_island
        self.sws = self.southwest_service
        self.upn = self.union_pacific_north
        self.upnw = self.union_pacific_northwest
        self.upw = self.union_pacific_west
        
        rows = ["{:<8}{:<20}".format(r.route_id,r.long_name) for r in self.routes]
        self.__repr = "\n".join(rows)
        
    def __getitem__(self,idx):
        return self.routes[idx]
        
    def __iter__(self):
        return iter(self.routes)
    
    def __repr__(self) -> str:
        return self.__repr
    
    def __assign_routes(self):
        for r in self.routes:
            if r.route_id == "BNSF": self.bnsf_railway = r
            elif r.route_id == "HC": self.herritage_corridor = r
            elif r.route_id == "MD-N": self.milwaukee_north = r
            elif r.route_id == "MD-W": self.milwaukee_west = r
            elif r.route_id == "ME": self.metra_electric = r
            elif r.route_id == "NCS": self.north_central_service = r
            elif r.route_id == "RI": self.rock_island = r
            elif r.route_id == "SWS": self.southwest_service = r
            elif r.route_id == "UP-N": self.union_pacific_north = r
            elif r.route_id == "UP-NW": self.union_pacific_northwest = r
            elif r.route_id == "UP-W": self.union_pacific_west = r
            else: pass

class Route:
    def __init__(self,data:dict):
        self.route_id: str = data.get('route_id','')
        self.short_name: str = data.get('route_short_name','')
        self.long_name: str = data.get('route_long_name','')
        self.desc: str = data.get('route_desc','')
        self.agency_id: str = data.get('agency_id','')
        self.type: int = data.get('route_type','')
        self.color: str = data.get('route_color','')
        text_color = data.get('route_text_color','000000')
        self.text_color: str = text_color if text_color != 0 else "000000"
        self.url: str = data.get('route_url','')
        
    def __repr__(self) -> str:
        return f"<{self.route_id} ({self.long_name})>"

# Calendar Response objects
class Calendars:
    def __init__(self,resp:list[dict]):
        self.calendars = [Calendar(d) for d in resp]
        
    def __getitem__(self,idx):
        return self.calendars[idx]
        
    def __iter__(self):
        return iter(self.calendars)

    def get_active_calendars(self) -> list:
        calendars = []
        for c in self:
            if c.is_active:
                calendars.append(c)
        return calendars

class Calendar:
    def __init__(self,data:dict):
        self.service_id: str = data.get('service_id','')
        self.monday: bool = True if data.get('monday',0) == 1 else False
        self.tuesday: bool = True if data.get('tuesday',0) == 1 else False
        self.wednesday: bool = True if data.get('wednesday',0) == 1 else False
        self.thursday: bool = True if data.get('thursday',0) == 1 else False
        self.friday: bool = True if data.get('friday',0) == 1 else False
        self.saturday: bool = True if data.get('saturday',0) == 1 else False
        self.sunday: bool = True if data.get('sunday',0) == 1 else False
        self.start_date: str = data.get('start_date','')
        self.end_date: str = data.get('end_date','')
        self.is_active: bool = False
        if self.start_date_obj <= dt.date.today() <= self.end_date_obj:
            self.is_active = True

    def __repr__(self) -> str:
        return f"<{self.service_id} ({self.start_date_obj.strftime(r'%b %d')} - {self.end_date_obj.strftime(r'%b %d')})>"
    
    @property
    def start_date_obj(self) -> dt.date:
        """Start date as Python datetime object"""
        return dt.datetime.strptime(self.start_date,r'%Y-%m-%d').date()
    
    @property
    def end_date_obj(self) -> dt.date:
        """End date as Python datetime object"""
        return dt.datetime.strptime(self.end_date,r'%Y-%m-%d').date()


