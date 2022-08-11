import zipfile
import pickle
import requests
import datetime as dt
from requests.auth import HTTPBasicAuth
from io import BytesIO

import pandas as pd

from .schemas import Stops, Stop
from .schemas import StopTimes, StopTime
from .schemas import Trips, Trip
from .schemas import Shapes, Shape
from .schemas import Routes, Route
from .schemas import Calendars, Calendar
from .constants import METRA_BASE
from .auth import METRA_API_KEY
from .auth import METRA_SECRET_KEY
from .paths import DATA_PATH
from .utils import get_publish_time
from .utils import get_last_local_publish
from .utils import PUBLISHED_FMT

AUTH = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)

def stops() -> Stops:
    url = METRA_BASE + "/schedule/stops"
    resp = requests.get(url,auth=AUTH)
    return Stops(resp.json())

def stop_times(trip_id:str=None) -> StopTimes:
    if trip_id is None:
        stop_times: StopTimes
        try:
            with open(f'{DATA_PATH}/last_updated_stop_times.txt','r+') as txt:
                last_updated = dt.datetime.strptime(txt.read(),PUBLISHED_FMT)
                if last_updated > get_last_local_publish():
                    stop_times = get_stop_times()
                else:
                    update_stop_times()
                    stop_times = get_stop_times()
        except:
            update_stop_times()
            stop_times = get_stop_times()
        
        return stop_times
    else:
        url = METRA_BASE + f"/schedule/stop_times/{trip_id}"
        resp = requests.get(url,auth=AUTH)
        return StopTimes(resp.json())
    
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

def get_route_stop_times(route_id: str) -> pd.DataFrame:
    df = stop_times().df()
    return df[df['trip_id'].str.contains(route_id.upper())]

# Helpers ---------------------
def update_stop_times():
    url = METRA_BASE + "/schedule/stop_times"
    resp = requests.get(url,auth=AUTH)
    stop_times = StopTimes(resp.json())
    
    with open(f'{DATA_PATH}/stop_times.pickle','wb') as pkl:
        pickle.dump(stop_times,pkl)
        
    with open(f'{DATA_PATH}/last_updated_stop_times.txt','w+') as txt:
        txt.write(dt.datetime.now().strftime(PUBLISHED_FMT))
        
def get_stop_times() -> StopTimes:
    try:
        with open(f'{DATA_PATH}/stop_times.pickle','rb') as pkl:
            return pickle.load(pkl)
    except:
        update_stop_times()
        with open(f'{DATA_PATH}/stop_times.pickle','rb') as pkl:
            return pickle.load(pkl)
     
def get_active_stop_times(direction: str=None) -> pd.DataFrame:
    st: pd.DataFrame = stop_times().df()
    if direction is None:
        trip_list = list(set(get_active_trips()['trip_id']))
    elif direction == 'inbound':
        trip_list = list(set(get_inbound_trips()['trip_id']))
    elif direction == 'outbound':
        trip_list = list(set(get_outbound_trips()['trip_id']))
    else:
        trip_list = list(set(get_active_trips()['trip_id']))
        
    df = st[st['trip_id'].isin(trip_list)]
    df.reset_index(drop=True,inplace=True)
    return df

def get_upcoming_stop_times(direction: str=None) -> pd.DataFrame:
    df = get_active_stop_times(direction)
    now = dt.datetime.now()
    df = df[df['arrival_time'] > pd.to_datetime(now)]
    df.reset_index(drop=True,inplace=True)
    return df
   
def get_active_trips() -> pd.DataFrame:
    """Get all trips on the currently active schedule"""
    service_ids = []
    active_calendars: list[Calendar] = calendar().get_active_calendars()
    for ac in active_calendars:
        service_ids.append(ac.service_id)
    
    active_trips = []
    for trip in trips():
        if trip.service_id in service_ids:
            active_trips.append(
                [
                    trip.trip_id,
                    trip.trip_headsign,
                    trip.route_id,
                    trip.direction,
                    trip.shape_id,
                    trip.service_id,
                ]
            )
    df = pd.DataFrame(data=active_trips,columns=['trip_id','trip_headsign','route_id','direction','shape_id','service_id'])
    df.reset_index(drop=True,inplace=True)
    
    return df

def get_inbound_trips() -> pd.DataFrame:
    df = get_active_trips()
    return df[df['direction'] == 'inbound']

def get_outbound_trips() -> pd.DataFrame:
    df = get_active_trips()
    return df[df['direction'] != 'inbound']