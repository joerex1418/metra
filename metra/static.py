import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint as pp

from .schemas import TripsResponse
from .schemas import StopsResponse
from .schemas import StopTimesResponse

from .constants import METRA_BASE
from .auth import METRA_API_KEY
from .auth import METRA_SECRET_KEY

class Static:
    def __init__(self) -> None:
        self.__auth = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)
    
    def get_stops(self) -> StopsResponse:
        url = METRA_BASE + "/schedule/stops"
        resp = requests.get(url,auth=self.__auth)
        return StopsResponse(resp.json())
    
    def get_stop_times(self,trip_id:str=None) -> StopTimesResponse:
        if trip_id is None:
            url = METRA_BASE + "/schedule/stop_times"
        else:
            url = METRA_BASE + f"/schedule/stop_times/{trip_id}"
        resp = requests.get(url,auth=self.__auth)
        return StopTimesResponse(resp.json())
        
    def get_trips(self) -> TripsResponse:
        url = METRA_BASE + "/schedule/trips"
        resp = requests.get(url,auth=self.__auth)
        return TripsResponse(resp.json())
        
    def get_shapes(self):
        url = METRA_BASE + "/schedule/shapes"
        resp = requests.get(url,auth=self.__auth)
        pp(resp.json())
        
    def get_routes(self):
        url = METRA_BASE + "/schedule/routes"
        resp = requests.get(url,auth=self.__auth)
        pp(resp.json())
    
    def get_calendar(self):
        url = METRA_BASE + "/schedule/calendar"
        resp = requests.get(url,auth=self.__auth)
        pp(resp.json())
        
    def get_calendar_dates(self):
        url = METRA_BASE + "/schedule/calendar_dates"
        resp = requests.get(url,auth=self.__auth)
        pp(resp.json())