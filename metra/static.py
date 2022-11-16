import io
import zipfile
import requests
import datetime as dt
from requests.auth import HTTPBasicAuth
from typing import Union

import pandas as pd

from .schemas import Stops, Stop
from .schemas import StopTimes, StopTime
from .schemas import Trips, Trip
from .schemas import Shapes, Shape
from .schemas import Routes, Route
from .schemas import Calendars, Calendar
from .constants import METRA_BASE
from .constants import DASH_FMT
from .constants import SLASH_FMT
from .auth import METRA_API_KEY
from .auth import METRA_SECRET_KEY
from .paths import DATA_PATH

from .utils import get_last_local_publish
from .utils import get_schedule_zip
from .utils import CALENDAR_FMT
from .utils import PUBLISHED_FMT

AUTH = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)

class StaticAPI:
    def __init__(self):
        self.__zip = get_schedule_zip()
        self.__published_date = get_last_local_publish()
        self.__base_dt = dt.datetime.combine(self.__published_date.date(),time=dt.time(0,0,0))
        
        self.__stops = self.__get_stops()
        self.__stop_times = self.__get_stop_times()
        self.__trips = self.__get_trips()
        self.__routes = self.__get_routes()
        self.__shapes = self.__get_shapes()
        self.__calendar = self.__get_calendar()
        self.__fare_rules = self.__get_fare_rules()
        self.__fare_attributes = self.__get_fare_attributes()
    
    def stops(self) -> pd.DataFrame:
        """Get dataframe of all serviced Metra stops"""
        return self.__stops
    
    def stop_times(self) -> pd.DataFrame:
        """Get stop times dataset provided by the Metra GTFS API"""
        return self.__stop_times
    
    def trips(self) -> pd.DataFrame:
        """Get dataset of each trip.
        
        Note that not every trip in the dataset may be currently active. 
        See the "calendar" dataset with the `StaticAPI.calendar()` method.
        
        For convenience, the built-in method `StaticAPI.active_calendar_services()`
        will provide a list of active service ids which can be used to filter
        currently active trips.
        """
        return self.__trips
    
    def routes(self) -> pd.DataFrame:
        """Get dataframe of all Metra routes"""
        return self.__routes
    
    def shapes(self) -> pd.DataFrame:
        """Get dataset of geographical points for all Metra services/routes"""
        return self.__shapes
    
    def calendar(self) -> pd.DataFrame:
        """Calendar dataset that details when certain trips and services
        become active/inactive"""
        return self.__calendar
    
    def fare_rules(self) -> pd.DataFrame:
        """Dataset that details fare prices. (Use with "fare_attributes"
        dataset"""
        return self.__fare_rules
    
    def fare_attributes(self) -> pd.DataFrame:
        """Dataset fare attributes. (Use with "fare_rules" dataset)"""
        return self.__fare_attributes
    
    def trip_fare(self,origin:str,destination:str):
        """Get transportation fare given the origin and destination stops
        
        Params:
        -------
        origin : str
            stop id for the start of a trip
        destination : str
            stop id for the end of a trip
        """
        stops_df = self.stops()
        stops_df.set_index('stop_id',inplace=True)
        origin_zone = stops_df.loc[origin]["zone_id"]
        destination_zone = stops_df.loc[destination]["zone_id"]
        
        rules = self.fare_rules()
        rules = rules[(rules["origin_id"]==origin_zone) & (rules["destination_id"]==destination_zone)]
        fare_id = rules.iloc[0]["fare_id"]
        return self.fare_attributes().set_index("fare_id").loc[fare_id]["price"]
    
    def trips_with_stop(self,stop_id:str) -> list[str]:
        df = self.upcoming_schedule()
        df = df[df['stop_id']==stop_id]
        return list(set(df['trip_id']))
    
    def stop_search(self,query:str) -> pd.DataFrame:
        """Search for stop from the \"stops\" dataset"""
        query = query.lower()
        rows = []
        for idx,row in self.__stops.iterrows():
            if query in row['stop_id'].lower() or query in row['stop_name'].lower():
                rows.append(row)
        return pd.DataFrame(rows)
                
    def next_trains(self,origin:str,destination:str,date:Union[str,dt.datetime]=None) -> pd.DataFrame:
        """Get dataframe of upcoming departure times for trains traveling from
        one point, "origin", to another, "destination"
        
        Params:
        -------
        origin : str
            stop id for the start of a trip
        destination : str
            stop id for the end of a trip
        """
        if type(date) is str:
            try:
                date = dt.datetime.strptime(date,DASH_FMT)
            except:
                try:
                    date = dt.datetime.strptime(date,SLASH_FMT)
                except:
                    date = dt.datetime.today()
        elif type(date) is dt.datetime:
            pass
        elif type(date) is dt.date:
            date = dt.datetime.combine(date,time=dt.time(3,1,0))
        else:
            date = dt.datetime.today()
            
        st = self.upcoming_schedule(date=date)
        ordered_cols = list(st.columns)
        relevant_st = st[st["stop_id"]==origin]
        relevant_triplist: str = list(set(relevant_st["trip_id"]))
        relevant_st = st[st['trip_id'].isin(relevant_triplist)]
        relevant_st = relevant_st[relevant_st["stop_id"]==destination]
        relevant_triplist: str = list(set(relevant_st["trip_id"]))
        relevant_st = st[st['trip_id'].isin(relevant_triplist)]
        
        dfs_that_matter = []
        for trip_id in relevant_triplist:
            df = relevant_st[relevant_st["trip_id"]==trip_id]
            df.set_index("stop_id",inplace=True)
            if df.loc[origin]["stop_sequence"] < df.loc[destination]["stop_sequence"]:
                dfs_that_matter.append(df.reset_index())
        
        df = pd.concat(dfs_that_matter)[ordered_cols]
        
        return df[df["stop_id"]==origin].sort_values(by="arrival_time").reset_index(drop=True)
        
    def upcoming_schedule(self,direction:str=None,date:dt.datetime=None) -> pd.DataFrame:
        """Filters the stop times dataset by only retrieving upcoming 
        arrivals/departure times
        
        Params:
        -------
        direction : Optional[str | int]
            General direction ("inbound" or "outbound") of trips to specify.
            Defaults to `None`
        """
        if type(date) is str:
            try:
                date = pd.to_datetime(dt.datetime.strptime(date,DASH_FMT))
            except:
                try:
                    date = pd.to_datetime(dt.datetime.strptime(date,SLASH_FMT))
                except:
                    date = pd.to_datetime(dt.datetime.today().date())
        elif type(date) is dt.datetime:
            now = pd.to_datetime(date)
        else:
            now = pd.to_datetime(dt.datetime.today())
        
        if type(direction) is str:
            if direction.lower() == "inbound" or direction.lower() == "ib":
                direction = 1
            elif direction.lower() == "outbound" or direction.lower() == "ob":
                direction = 0
        elif type(direction) is int:
            if direction != 0 and direction != 1:
                direction = None
        else:
            direction = None

        trips_df = self.active_trips(direction=direction,date=date)
        active_trips = list(set(trips_df['trip_id']))
        
        stop_times_df = self.__stop_times[self.__stop_times['trip_id'].isin(active_trips)]
        stop_times_df = stop_times_df[stop_times_df['arrival_time'] > now]
        
        return stop_times_df.reset_index(drop=True)
    
    def upcoming_route_schedule(self,route_id:str,direction:Union[Union[str,int],None]=None) -> pd.DataFrame:
        """Get a schedule of all scheduled stop times by route
        
        Parameters:
        -----------
        route_id : str
            The route identifier (the "Route" class in the module contains variables for all active routes)
        direction : str | int | None
            Filter results by direction ("inbound" or "outbound"). Alternatively, you can use the API's
            integer notation to indicate how to filter. 0 = "outbound", 1 = "inbound"
        """
        
        if type(direction) is str:
            if direction.lower() == "inbound" or direction.lower() == "ib":
                direction = 1
            elif direction.lower() == "outbound" or direction.lower() == "ob":
                direction = 0
        elif type(direction) is int:
            if direction != 0 and direction != 1:
                direction = None
        else:
            direction = None

        now = pd.to_datetime(dt.datetime.today())
        trips_df = self.active_trips(route_id=route_id.upper(),direction=direction)
        active_trips = list(set(trips_df['trip_id']))
        
        stop_times_df = self.__stop_times[self.__stop_times['trip_id'].isin(active_trips)]
        stop_times_df = stop_times_df[stop_times_df['arrival_time'] > now]
        
        return stop_times_df.reset_index(drop=True)
    
    def active_calendar_services(self,date:dt.datetime=None) -> list[str]:
        """Get list of currently active services"""
        if date is None:
            today = pd.to_datetime(dt.date.today())
        elif type(date) is str:
            date = dt.datetime.strptime(date,DASH_FMT)
            today = pd.to_datetime(date)
        elif type(date) is dt.datetime:
            today = pd.to_datetime(date)
            
        df = self.__calendar[self.__calendar['start_date'] <= today]
        df = df[df['end_date'] >= today]
        return list(set(df['service_id']))
    
    def active_trips(self,route_id:str=None,direction:Union[int,None]=None,date:dt.datetime=None) -> pd.DataFrame:
        df = self.__trips
        if type(route_id) is str:
            df = df[df['route_id']==route_id]
        df = df[df['service_id'].isin(self.active_calendar_services(date=date))]
        
        if type(direction) is int:
            df = df[df['direction_id']==direction]
        
        return df
    
    def __convert_time_strings(self,time:str):
        time = time.strip()
        hh, mm, ss = (int(time[:2]), int(time[3:5]), int(time[-2:]))
        return self.__base_dt + dt.timedelta(hours=hh,minutes=mm,seconds=ss)
    
    def __get_stops(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('stops.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        df.drop(columns=['stop_url','stop_desc'],inplace=True)
        for col in ['stop_id','stop_name','zone_id']:
            df[col] = df[col].apply(lambda x: str(x).strip())
        return df
    
    def __get_stop_times(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('stop_times.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        df.drop(columns=['departure_time','notice'],inplace=True)
        df['arrival_time'] = df['arrival_time'].apply(lambda time: self.__convert_time_strings(time))
        df['trip_id'] = df['trip_id'].apply(lambda x : str(x).strip())
        df['stop_id'] = df['stop_id'].apply(lambda x : str(x).strip())
        return df
    
    def __get_trips(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('trips.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        df.drop(columns=['block_id'],inplace=True)
        for col in ['route_id','service_id','trip_id','trip_headsign','shape_id']:
            df[col] = df[col].apply(lambda x: str(x).strip())
        return df
    
    def __get_routes(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('routes.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        df.rename(columns={'shape_pt_lat':'lat','shape_pt_lon':'lon'})
        df.drop(columns=['route_desc','route_url','agency_id'],inplace=True)
        for col in ['route_id','route_short_name','route_long_name','route_color','route_text_color']:
            df[col] = df[col].apply(lambda x: str(x).strip())
        return df
    
    def __get_shapes(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('shapes.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        for col in ['shape_id']:
            df[col] = df[col].apply(lambda x: str(x).strip())
        return df

    def __get_calendar(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('calendar.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        df['service_id'] = df['service_id'].apply(lambda x: str(x).strip())
        df['start_date'] = pd.to_datetime(df['start_date'],format=CALENDAR_FMT)
        df['end_date'] = pd.to_datetime(df['end_date'],format=CALENDAR_FMT)
        return df
    
    def __get_fare_rules(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('fare_rules.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        df.drop(columns=['route_id','contains_id'],inplace=True)
        for col in ['origin_id','destination_id']:
            df[col] = df[col].apply(lambda x: str(x).strip())
        return df
    
    def __get_fare_attributes(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('fare_attributes.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        for col in ['currency_type']:
            df[col] = df[col].apply(lambda x: str(x).strip())
        return df


def stops() -> Stops:
    url = METRA_BASE + "/schedule/stops"
    resp = requests.get(url,auth=AUTH)
    return Stops(resp.json())

def trips() -> Trips:
    url = METRA_BASE + "/schedule/trips"
    resp = requests.get(url,auth=AUTH)
    return Trips(resp.json())
    
def shapes() -> Shapes:
    url = METRA_BASE + "/schedule/shapes"
    resp = requests.get(url,auth=AUTH)
    return Shapes(resp.json())
    
def routes() -> Routes:
    url = METRA_BASE + "/schedule/routes"
    resp = requests.get(url,auth=AUTH)
    return Routes(resp.json())

def calendar():
    url = METRA_BASE + "/schedule/calendar"
    resp = requests.get(url,auth=AUTH)
    return Calendars(resp.json())

def calendar_dates():
    url = METRA_BASE + "/schedule/calendar_dates"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

def stop_times():
    url = METRA_BASE + "/schedule/stop_times"
    resp = requests.get(url,auth=AUTH)
    return resp.json()
