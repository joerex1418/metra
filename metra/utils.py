import io
import zipfile
import requests
import datetime as dt
from requests.auth import HTTPBasicAuth

import pandas as pd

from .paths import DATA_PATH
from .constants import METRA_BASE
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
        self.__calendars = self.__get_calendars()
    
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
    
    def calendars(self) -> pd.DataFrame:
        return self.__calendars
    
    def __convert_time_strings(self,time:str):
        time = time.strip()
        hh, mm, ss = (int(time[:2]), int(time[3:5]), int(time[-2:]))
        return self.__base_dt + dt.timedelta(hours=hh,minutes=mm,seconds=ss)
    
    def __get_stops(self) -> pd.DataFrame:
        bytes_io = io.BytesIO(self.__zip.read('stops.txt'))
        df = pd.read_csv(bytes_io)
        df.columns = list(map(lambda x: str(x).strip(),df.columns))
        df.drop(columns=['stop_url'],inplace=True)
        for col in ['stop_id','stop_name','stop_desc','zone_id']:
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

    def __get_calendars(self) -> pd.DataFrame:
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
            time = txtfile.read()
            return dt.datetime.strptime(time,PUBLISHED_FMT)
    except:
        return get_publish_time()
    
def update_schedule_zip():
    url = METRA_BASE + "/raw/schedule.zip"
    resp = requests.get(url,auth=AUTH)
    
    with open(f'{DATA_PATH}/schedule.zip','wb') as output:
        output.write(resp.content)

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

# def get_schedule() -> StaticAPI:
#     """Creates a python object from a zipfile. The resulting allows reading individual files into Pandas Dataframes
#     """
#     return StaticAPI(zip_file=get_schedule_zip())