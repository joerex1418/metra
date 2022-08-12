import io
import zipfile
import requests
import datetime as dt
import base64
from requests.auth import HTTPBasicAuth
from typing import Union

import pandas as pd

from .paths import DATA_PATH
from .constants import METRA_BASE
from .constants import ZONES
from .constants import ROUTES_SHORTHAND
from .auth import METRA_API_KEY, METRA_SECRET_KEY

AUTH = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)
PUBLISHED_FMT = r'%m/%d/%Y %I:%M:%S %p'
CALENDAR_FMT = r'%Y%m%d'

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
    
    def stops(self) -> pd.DataFrame:
        return self.__stops
    
    def stop_times(self) -> pd.DataFrame:
        return self.__stop_times
    
    def trips(self) -> pd.DataFrame:
        return self.__trips
    
    def routes(self) -> pd.DataFrame:
        return self.__routes
    
    def shapes(self) -> pd.DataFrame:
        return self.__shapes
    
    def calendar(self) -> pd.DataFrame:
        return self.__calendar
    
    def trips_with_stop(self,stop_id:str) -> list[str]:
        df = self.upcoming_schedule()
        df = df[df['stop_id']==stop_id]
        return list(set(df['trip_id']))
    
    def next_trains(self,origin:str,destination:str) -> pd.DataFrame:
        st = self.upcoming_schedule()
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
        
        return df[df["stop_id"]==origin].sort_values(by="arrival_time")
    
    def next_inbound(self,origin:str) -> pd.DataFrame:
        df = self.upcoming_schedule(direction="ib")
        df = df[df['trip_id'].isin(self.trips_with_stop(origin.upper()))]
        return df[df["stop_id"]==origin].reset_index(drop=True)
        
    def upcoming_schedule(self,direction:str=None) -> pd.DataFrame:
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

        trips_df = self.__active_trips(direction=direction)
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
        trips_df = self.__active_trips(route_id=route_id.upper(),direction=direction)
        active_trips = list(set(trips_df['trip_id']))
        
        stop_times_df = self.__stop_times[self.__stop_times['trip_id'].isin(active_trips)]
        stop_times_df = stop_times_df[stop_times_df['arrival_time'] > now]
        
        return stop_times_df.reset_index(drop=True)
    
    def active_calendar_services(self) -> list:
        today = pd.to_datetime(dt.date.today())
        df = self.__calendar[self.__calendar['start_date'] <= today]
        df = df[df['end_date'] >= today]
        return list(set(df['service_id']))
    
    def __active_trips(self,route_id:str=None,direction:Union[int,None]=None) -> pd.DataFrame:
        df = self.__trips
        if type(route_id) is str:
            df = df[df['route_id']==route_id]
        df = df[df['service_id'].isin(self.active_calendar_services())]
        
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

def get_publish_time() -> dt.datetime:
    url = METRA_BASE + "/raw/published.txt"
    resp = requests.get(url,auth=AUTH)
    time = resp.text
    with open(f'{DATA_PATH}/last_published.txt','w+') as txtfile:
        txtfile.write(time)
    return dt.datetime.strptime(time,PUBLISHED_FMT)

def get_last_local_publish() -> dt.datetime:
    try:
        with open(f'{DATA_PATH}/last_published.txt','r+') as txtfile:
            datetime = txtfile.read()
            datetime = dt.datetime.strptime(datetime,PUBLISHED_FMT)
            # if dt.datetime.combine(datetime.date(),time=dt.time(3,0,0)) > dt.datetime.now():
            if datetime.date() < dt.datetime.today().date():
                datetime = get_publish_time()
            return datetime
    except:
        return get_publish_time()

# from urllib.request import urlopen, Request
    
def update_schedule_zip():
    url = METRA_BASE + "/raw/schedule.zip"
    resp = requests.get(url,auth=AUTH)
    updated_zip = zipfile.ZipFile(io.BytesIO(resp.content),'r')
    new_zip = zipfile.ZipFile(f'{DATA_PATH}/schedule.zip','w')
    
    for f in ['stop_times','stops','calendar','calendar_dates','routes','shapes','trips','fare_rules','fare_attributes']:
        fbytes = updated_zip.read(f'{f}.txt')
        new_zip.writestr(f'{f}.txt',fbytes,zipfile.ZIP_DEFLATED)
    updated_zip.close()
    new_zip.close()
        
def get_schedule_zip() -> zipfile.ZipFile:
    try:
        with open(f'{DATA_PATH}/schedule.zip','rb') as fp:
            bytes_io = io.BytesIO(fp.read())
            return zipfile.ZipFile(bytes_io, mode='r')

    except:
        update_schedule_zip()
        with open(f'{DATA_PATH}/schedule.zip','rb') as fp:
            bytes_io = io.BytesIO(fp.read())
            return zipfile.ZipFile(bytes_io, mode='r')
