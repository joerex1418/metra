import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint as pp

from .schemas import Stops
from .schemas import StopTimes
from .schemas import Trips
from .schemas import Shapes
from .schemas import Routes
from .schemas import Calendars

from .constants import METRA_BASE
from .auth import METRA_API_KEY
from .auth import METRA_SECRET_KEY

AUTH = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)

def get_stops() -> Stops:
    url = METRA_BASE + "/schedule/stops"
    resp = requests.get(url,auth=AUTH)
    return Stops(resp.json())

def get_stop_times(trip_id:str=None) -> StopTimes:
    if trip_id is None:
        url = METRA_BASE + "/schedule/stop_times"
    else:
        url = METRA_BASE + f"/schedule/stop_times/{trip_id}"
    resp = requests.get(url,auth=AUTH)
    return StopTimes(resp.json())
    
def get_trips() -> Trips:
    url = METRA_BASE + "/schedule/trips"
    resp = requests.get(url,auth=AUTH)
    return Trips(resp.json())
    
def get_shapes() -> Shapes:
    url = METRA_BASE + "/schedule/shapes"
    resp = requests.get(url,auth=AUTH)
    return Shapes(resp.json())
    
def get_routes() -> Routes:
    url = METRA_BASE + "/schedule/routes"
    resp = requests.get(url,auth=AUTH)
    return Routes(resp.json())

def get_calendar():
    url = METRA_BASE + "/schedule/calendar"
    resp = requests.get(url,auth=AUTH)
    return Calendars(resp.json())
    
def get_calendar_dates():
    url = METRA_BASE + "/schedule/calendar_dates"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

