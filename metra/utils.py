import requests
import io, zipfile
import datetime as dt
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Optional

from .paths import DATA
from .constants import METRA_BASE, ZONES
from .auth import METRA_API_KEY, METRA_SECRET_KEY

AUTH = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)
PUBLISHED_FMT = r'%m/%d/%y %I:%M:%S %p'
CALENDAR_FMT  = r'%Y%m%d'

class filters:
    @staticmethod
    def active_services(d: Dict, date: dt.date) -> bool:
        try:
            dstart = dt.datetime.strptime(d['start_date'],r'%Y-%m-%d')
            dend = dt.datetime.strptime(d['end_date'],r'%Y-%m-%d')
        except:
            dstart = dt.datetime.strptime(d['start_date'],CALENDAR_FMT)
            dend = dt.datetime.strptime(d['end_date'],CALENDAR_FMT)
        if dstart <= date <= dend:
            return d[f'{date:%A}'.lower()]
    
    @staticmethod
    def active_trips(d: Dict, service_ids: List[str]) -> bool:
        if d['service_id'] in service_ids:
            return True
    
    @staticmethod
    def upcoming_arrivals(d: Dict, datetime: dt.datetime) -> bool:
        try:
            dtime = dt.datetime.strptime(d['arrival_time'],PUBLISHED_FMT)
        except:
            dtime = dt.datetime.strptime(d['arrival_time'],CALENDAR_FMT)
        if datetime <= dtime:
            return True

    @staticmethod
    def origin_destination(d: Dict, origin_id: str, destination_id: str) -> bool:
        if d['stop_id'] == origin_id or d['stop_id'] == destination_id:
            return True

def now() -> dt.datetime:
    """Returns the current datetime"""
    return dt.datetime.today()    

def get_publish_time() -> dt.datetime:
    url = METRA_BASE + "/raw/published.txt"
    resp = requests.get(url,auth=AUTH)
    time = resp.text
    with open(f'{DATA}/last_published.txt','w+') as txtfile:
        txtfile.write(time)
    return dt.datetime.strptime(time,PUBLISHED_FMT)
    
def update_schedule_zip():
    url = METRA_BASE + "/raw/schedule.zip"
    resp = requests.get(url,auth=AUTH)
    updated_zip = zipfile.ZipFile(io.BytesIO(resp.content),'r')
    new_zip = zipfile.ZipFile(f'{DATA}/schedule.zip','w')
    
    for f in ['stop_times','stops','calendar','calendar_dates','routes','shapes','trips','fare_rules','fare_attributes']:
        fbytes = updated_zip.read(f'{f}.txt')
        new_zip.writestr(f'{f}.txt',fbytes,zipfile.ZIP_DEFLATED)
    updated_zip.close()
    new_zip.close()
    
def determine_direction(origin_id: str, destination_id: str) -> int:
    """Determines the direction of travel based on origin and destination"""
    if ZONES[origin_id] > ZONES[destination_id]:
        return 0
    elif ZONES[origin_id] < ZONES[destination_id]:
        return 1
    else:
        return None
    
def normalize_direction(direction) -> Optional[int]:
    if str(direction).lower() in ['i','ib','inbound','1']:
        return 1
    elif str(direction).lower() in ['o','ob','outbound','0']:
        return 0
    else:
        return None