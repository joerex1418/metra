import datetime
datetime.datetime

# Trips Response objects
class TripsResponse:
    def __init__(self,resp:list[dict]):
        self.trips = [Trip(d) for d in resp]
        
    def __getitem__(self,idx):
        return self.trips[idx]
        
    def __iter__(self):
        return iter(self.trips)
        
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
    
    def __repr__(self) -> str:
        return f"<{self.trip_id} ({self.trip_headsign})>"
    
    
# Stops Response objects
class StopsResponse:
    def __init__(self,resp:list[dict]):
        self.stops = [Stop(d) for d in resp]
        
    def __getitem__(self,idx):
        return self.stops[idx]
        
    def __iter__(self):
        return iter(self.stops)

class Stop:
    def __init__(self,data:dict):
        self.stop_id = data.get('stop_id','')
        self.name = data.get('stop_name','')
        self.desc = data.get('stop_desc','')
        self.lat = data.get('stop_lat')
        self.lon = data.get('stop_lon')
        self.zone_id = data.get('zone_id','')
        self.url = data.get('stop_url','')
        self.has_wheelchair_boarding = True if data.get('wheelchair_boarding',0) == 1 else False
    
    def __repr__(self) -> str:
        return f"<{self.stop_id} ({self.name})>"
    
class StopTimesResponse:
    def __init__(self,resp:list[dict]):
        self.stop_times = [StopTime(d) for d in resp]
        
    def __getitem__(self,idx):
        return self.stop_times[idx]
        
    def __iter__(self):
        return iter(self.stop_times)
    
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
        return f"<#{self.stop_sequence} {self.arrival_time} {self.stop_id}>"
    