import io, os, re
import datetime as dt
import csv, requests, zipfile
from typing import Dict, List, Union, Optional

from tabulate import tabulate

from . import paths, utils
from .auth import AUTH
from .constants import METRA_BASE
from .datamodels import _TimeData
from .datamodels import Trip, Stop, Route, StopTime, CalendarService
from .utils import filters, determine_direction, normalize_direction

LAST_PUBLISH  = os.path.join(paths.DATA, "last_publish.txt")
LAST_DOWNLOAD = os.path.join(paths.DATA, "last_download.txt")

class StaticFeed:
    def __init__(self):
        # ---------------------------------------------------------- #
        # Check if the most recent static feed is available locally
        # ---------------------------------------------------------- #
        _needs_update = True
        cloud_publish = self._get_last_publish_cloud()
        local_publish = self._get_last_publish_local()
        
        if local_publish.dt == cloud_publish.dt:
            _needs_update = False
        
        if _needs_update:
            # ------------------------------------------------------ #
            # Download schedule zip file
            # ------------------------------------------------------ #
            url = METRA_BASE + "/raw/schedule.zip"
            resp = requests.get(url,auth=AUTH)
            with open(os.path.join(paths.DATA,"schedule.zip"),'wb') as f:
                f.write(resp.content)

            # ------------------------------------------------------ #
            # Log the publish time
            #   This timestamp reflects the time
            #   the static feed was last published to the server
            # ------------------------------------------------------ #
            _log_path = os.path.join(paths.DATA,"last_published.txt")
            with open(_log_path,'w') as f:
                f.write(cloud_publish.string)
    
    def stops(self,**kws):
        stops: List[Stop] = []
        with zipfile.ZipFile(os.path.join(paths.DATA,"schedule.zip")) as z:
            with z.open("stops.txt") as f:
                reader = csv.reader(f.read().decode('utf-8').splitlines())
                next(reader)
                for row in reader:
                    row = [x.strip() for x in row]
                    stops.append(
                        Stop(
                            stop_id=row[0],
                            stop_name=row[1],
                            # not including stop_desc (row[2])
                            # value is always empty
                            stop_lat=float(row[3]),
                            stop_lon=float(row[4]),
                            zone_id=row[5],
                            stop_url=row[6],
                            wheelchair_boarding=int(row[7])
                            )
                        )
        if kws.get('cmd'):
            tbl = tabulate(stops,headers="keys",tablefmt="psql")
            print(tbl)
        else:
            return stops
    
    def routes(self):
        _routes = []
        with zipfile.ZipFile(os.path.join(paths.DATA,"schedule.zip")) as z:
            with z.open("routes.txt") as f:
                reader = csv.reader(f.read().decode('utf-8').splitlines())
                next(reader)
                for row in reader:
                    row = [x.strip() for x in row]
                    _routes.append(
                        Route(
                            route_id=row[0],
                            route_short_name=row[1],
                            route_long_name=row[2],
                            # not including route_desc (row[3])
                            # value is always empty
                            agency_id=row[4],
                            route_type=int(row[5]),
                            route_color=row[6],
                            route_text_color=row[7],
                            route_url=row[8]
                            )
                        )
        return _routes
    
    def trips(self):
        _trips = []
        with zipfile.ZipFile(os.path.join(paths.DATA,"schedule.zip")) as z:
            with z.open("trips.txt") as f:
                reader = csv.reader(f.read().decode('utf-8').splitlines())
                next(reader)
                for row in reader:
                    row = [x.strip() for x in row]
                    _trips.append(
                        Trip(
                            route_id = row[0],
                            service_id = row[1],
                            trip_id = row[2],
                            trip_headsign = row[3],
                            block_id = row[4],
                            shape_id = row[5],
                            direction_id = int(row[6])
                            )
                        )
        return _trips
    
    def calendar(self):
        services = []
        with zipfile.ZipFile(os.path.join(paths.DATA,"schedule.zip")) as z:
            with z.open("calendar.txt") as f:
                reader = csv.reader(f.read().decode('utf-8').splitlines())
                next(reader)
                for row in reader:
                    row = [x.strip() for x in row]
                    start, end = row[8], row[9]
                    services.append(
                        CalendarService(
                            service_id=row[0],
                            monday=int(row[1]),
                            tuesday=int(row[2]),
                            wednesday=int(row[3]),
                            thursday=int(row[4]),
                            friday=int(row[5]),
                            saturday=int(row[6]),
                            sunday=int(row[7]),
                            start_date=start,
                            end_date=end
                            )
                        )
        return services
    
    def stop_times(self) -> List[StopTime]:
        _stop_times = []
        publish_dt = self._get_last_publish_local().dt
        basedate = dt.datetime.combine(publish_dt.date(),dt.time(0,0,0))
        with zipfile.ZipFile(os.path.join(paths.DATA,"schedule.zip")) as z:
            with z.open("stop_times.txt") as f:
                reader = csv.reader(f.read().decode('utf-8').splitlines())
                next(reader)
                for row in reader:
                    row = [x.strip() for x in row]
                    h, m, s = re.findall("[0-9][0-9]",row[1])
                    h, m, s = int(h), int(m), int(s)
                    tdelta = dt.timedelta(hours=h,minutes=m,seconds=s)
                    arrival_dt = basedate + tdelta
                    _stop_times.append(
                        StopTime(
                            trip_id=row[0],
                            arrival_time=arrival_dt,
                            stop_id=row[3],
                            stop_sequence=int(row[4]),
                            pickup_type=int(row[5]),
                            drop_off_type=int(row[6]),
                            center_boarding=int(row[7]),
                            south_boarding=int(row[8]),
                            bikes_allowed=int(row[9]),
                            notice=int(row[10])
                        )
                    )
        return _stop_times

    def departures(self,
                   origin_id:str,
                   destination_id:str,
                   datetime:dt.datetime=None,
                   **kws) -> list:

        if datetime is None:
            datetime = dt.datetime.today()

        direction = determine_direction(origin_id, destination_id)

        _stop_times = self._active_stop_times(datetime,direction)

        # ---------------------------------------------------------- #
        # Filter stop times to only those that match the origin stop
        # ---------------------------------------------------------- #
        origin_sts = list(filter(lambda x: x['stop_id'] == origin_id, _stop_times))
        trips = list({_['trip_id'] for _ in origin_sts})

        # ---------------------------------------------------------- #
        # Of the trips that match the origin stop, filter to only
        #   those that match the destination stop
        # ---------------------------------------------------------- #
        _stop_times = filter(
            lambda x: x['trip_id'] in trips, _stop_times
            )
        _stop_times = list(_stop_times)
        
        dest_sts = filter(
            lambda x: x['stop_id'] == destination_id, _stop_times
            )
        
        # ---------------------------------------------------------- #
        # These trips are the ones that match the origin and
        #   destination stops
        # ---------------------------------------------------------- #
        trips = list({x['trip_id'] for x in dest_sts})
        
        _stop_times = filter(
            lambda x: x['trip_id'] in trips, _stop_times
            )
        _stop_times = list(_stop_times)

        _stop_times = filter(
            lambda x: x['stop_id'] == origin_id, _stop_times
            )
        _stop_times = list(_stop_times)
        
        _stop_times = filter(
            lambda x: x['arrival_time'] > datetime, _stop_times
            )
        _stop_times = list(_stop_times)
        
        # ---------------------------------------------------------- #
        # Sort by arrival time
        # ---------------------------------------------------------- #
        _stop_times = sorted(
            _stop_times, key=lambda x: x['arrival_time']
            )
        
        if kws.get('cmd'):
            tbl = tabulate(_stop_times, headers='keys', tablefmt='psql')
            print(tbl)
        else:
            return _stop_times
    
    def get_stop(self, stop_id:str) -> Stop:
        stops = self.stops()
        for stop in stops:
            if stop['stop_id'] == stop_id:
                return stop
        return None
    
    def active_services(self,
                        date:dt.date=None) -> List[CalendarService]:
        cal = self.calendar()
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

    def upcoming_trips(self,
                   origin_id:str,
                   destination_id:str,
                   date:dt.date=None) -> List[str]:
        
        origin_stop = self.get_stop(origin_id)
        dest_stop = self.get_stop(destination_id)
        if origin_stop['zone_id'] > dest_stop['zone_id']:
            direction = 1
        elif origin_stop['zone_id'] < dest_stop['zone_id']:
            direction = 0
        else:
            direction = None
        
        _stop_times = self._active_stop_times(date,direction)
        # _stop_times = filter(lambda d: filters.origin_destination(d, origin_id, destination_id), _stop_times)
        _stop_times = filter(lambda t: t['stop_id'] == origin_id, stop_times)
        _stop_times = filter(lambda t: t["arrival_time"] >= dt.datetime.today(), _stop_times)
        _stop_times = list(_stop_times)
        _trip_ids = [st["trip_id"] for st in _stop_times]
        return list(set(_trip_ids))

    def next_trains(self,
                    origin_id:str,
                    date:dt.date=None,
                    direction=None) -> List[StopTime]:
        direction = normalize_direction(direction)
        
        _stop_times = self._active_stop_times(date,direction)
        _stop_times = filter(lambda t: t["stop_id"] == origin_id, _stop_times)
        _stop_times = filter(lambda t: t["arrival_time"] >= dt.datetime.today(), _stop_times)
        
        return list(_stop_times)

    def _active_trips(self,
                     date:dt.date=None,
                     direction=None) -> List[str]:
        _services = self.active_services(date)
        service_ids = [s["service_id"] for s in _services]
        _trips = self.trips()
        _trips = filter(lambda t: t["service_id"] in service_ids, _trips)
        if direction is not None:
            if str(direction) in ['i','ib','inbound','1']:
                direction = 1
            elif str(direction) in ['o','ob','outbound','0']:
                direction = 0
            _trips = filter(lambda t: t["direction_id"] == direction, _trips)
        _trips = list(_trips)
        return _trips
    
    def _active_stop_times(self,
                          date:dt.datetime,
                          direction=None) -> List[StopTime]:
        # if date is None:
        #     date = dt.datetime.today()
        _trips = self._active_trips(date,direction)
        _trips = [t["trip_id"] for t in _trips]
        _active_stop_times = []
        basedate = dt.datetime.combine(dt.date.today(),dt.time(0,0,0))
        with zipfile.ZipFile(os.path.join(paths.DATA,"schedule.zip")) as z:
            with z.open("stop_times.txt") as f:
                reader = csv.reader(f.read().decode('utf-8').splitlines())
                next(reader)
                for row in reader:
                    row = [x.strip() for x in row]
                    if row[0] in _trips:
                        h, m, s = re.findall("[0-9][0-9]",row[1])
                        h, m, s = int(h), int(m), int(s)
                        tdelta = dt.timedelta(hours=h,minutes=m,seconds=s)
                        arrival_dt = basedate + tdelta
                        arrival_time_str=(
                            f'{arrival_dt:%m/%d/%Y %I:%M:%S}')
                        _active_stop_times.append(
                            StopTime(
                                trip_id=row[0],
                                arrival_time=arrival_dt,
                                arrival_time_str=arrival_time_str,
                                stop_id=row[3],
                                stop_sequence=int(row[4]),
                                pickup_type=int(row[5]),
                                drop_off_type=int(row[6]),
                                center_boarding=int(row[7]),
                                south_boarding=int(row[8]),
                                bikes_allowed=int(row[9]),
                                notice=int(row[10])
                            )
                        )
        
        return _active_stop_times
    
    def _get_last_publish_local(self) -> _TimeData:
        _path = os.path.join(paths.DATA, "last_published.txt")
        with open(_path,'r') as f:
            dtstring = f.read()
            _pdt = _TimeData(_parse_publish_time(dtstring),dtstring)
            return _pdt
    
    def _get_last_publish_cloud(self) -> _TimeData:
        dtstring = last_publish(return_dt=False)
        _pdt = _TimeData(_parse_publish_time(dtstring),dtstring)
        return _pdt

    def _parse_date(self, date):
        if date is None:
            date = dt.datetime.today()
        elif type(date) is dt.date:
            date = dt.datetime.combine(date,dt.time())
        elif type(date) is dt.datetime:
            pass
        else:
            raise TypeError("'date' should be a datetime.date object")
        return date


def stops() -> Dict:
    url = METRA_BASE + "/schedule/stops"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

def trips() -> Dict:
    url = METRA_BASE + "/schedule/trips"
    resp = requests.get(url,auth=AUTH)
    return resp.json()
 
def shapes() -> Dict:
    url = METRA_BASE + "/schedule/shapes"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

def routes() -> Dict:
    url = METRA_BASE + "/schedule/routes"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

def calendar() -> Dict:
    url = METRA_BASE + "/schedule/calendar"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

def calendar_dates() -> Dict:
    url = METRA_BASE + "/schedule/calendar_dates"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

def stop_times(trip_id: str = None) -> Dict:
    "Not recommended - Takes a long time to retrieve this info"
    url = METRA_BASE + "/schedule/stop_times"
    if trip_id:
        url += f"/{trip_id}"
    resp = requests.get(url,auth=AUTH)
    return resp.json()

def _parse_publish_time(text: str) -> dt.datetime:
    re_date = re.search("[AP]M",text)
    text = text[:re_date.end()]
    return dt.datetime.strptime(text, utils.PUBLISHED_FMT)

def last_publish(return_dt:bool=False) -> Union[str,dt.datetime]:
    """
    Returns a timestamp of when Metra last published their schedule
    
    Parameters:
    return_dt: bool
        If True, returns a datetime object instead of a string
    """
    url = METRA_BASE + "/raw/published.txt"
    resp = requests.get(url,auth=AUTH)
    datestring = resp.text
    
    if return_dt:
        return _parse_publish_time(datestring)
    return datestring
