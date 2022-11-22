import re, io, csv
import datetime as dt
import requests, zipfile
from typing import Union, Dict, List

from . import static
from .auth import AUTH
from .constants import METRA_BASE
from .utils import filters, now
from .datamodels import CalendarService, Trip

def schedule_zip() -> bytes:
    url = METRA_BASE + "/raw/schedule.zip"
    resp = requests.get(url,auth=AUTH,stream=True)
    return resp.content

def active_services(date:dt.date=None) -> List[CalendarService]:
    cal = static.calendar()
    
    if date is None:
        date = dt.datetime.today()
    elif type(date) is dt.date:
        date = dt.datetime.combine(date,dt.time())
    elif type(date) is dt.datetime:
        pass
    else:
        raise TypeError("'date' should be a datetime.date object")
        
    cal = filter(lambda d: filters.active_services(d, date), cal)
    cal = list(cal)
    return cal

def active_trips(date:dt.date=None) -> List[Trip]:
    _services = active_services(date)
    service_ids = [s['service_id'] for s in _services]
    _trips = static.trips()
    _trips = filter(lambda t: filters.active_trips(t, service_ids), _trips)
    _trips = list(_trips)
    return _trips

def upcoming_arrivals(stop_id: str) -> List[Dict]:
    ...

def trip_stop_times(*,trip_id:str=None, 
                    stop_id:str=None,
                    active_only=True, 
                    upcoming_only=True,
                    datetime:dt.datetime=None,
                    ) -> List[Dict]:
    keys = ('trip_id','arrival_time','stop_id','stop_sequence',
            'pickup_type','drop_off_type','center_boarding',
            'south_boarding','bikes_allowed','notice')
    
    if datetime is None:
        datetime = now()
    
    _active_trips_list = None
    if active_only:
        _active_trips_list = active_trips(datetime)
        _active_trips_list = [t['trip_id'] for t in _active_trips_list]
    
    rows = []
    with zipfile.ZipFile(io.BytesIO(schedule_zip()), mode='r') as zfp:
        strio = io.BytesIO(zfp.read('stop_times.txt'))
        csvreader = csv.reader(strio.read().decode('utf-8').splitlines())
        for row in csvreader:
            if row[0] == 'trip_id':
                # row = [(x.strip(),i) for i, x in enumerate(row)]
                # console.log(row)
                continue
            
            if trip_id and (row[0] != trip_id):
                continue
            
            if stop_id and (row[3].strip() != stop_id):
                continue
            
            if active_only and (row[0] not in _active_trips_list):
                continue
            # if row[0] not in _active_trips_list:
            #     continue
            
            row = [x.strip() for x in row]
            
            h, m, s = re.findall("[0-9][0-9]",row[1])
            h, m, s = int(h), int(m), int(s)
            tdelta = dt.timedelta(hours=h,minutes=m,seconds=s)
            
            arrival_dt = dt.datetime.combine(now(), dt.time()) + tdelta
            row[1] = arrival_dt
            # row indexes 4 through 10 should be converted to ints
            for i in range(4,11):
                row[i] = int(row[i])
            
            row.pop(2)
            row = dict(zip(keys,row))
            
            if upcoming_only and arrival_dt < datetime:
                continue
            
            rows.append(row)
    
    return rows
