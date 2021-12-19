import os
import requests
import pandas as pd

import datetime as dt
from dateutil import tz

from .constants import METRA_API_KEY
from .constants import METRA_SECRET_KEY

UTC_ZONE = tz.tzutc()
ET_ZONE = tz.gettz("America/New_York")
CT_ZONE = tz.gettz("America/Chicago")
MT_ZONE = tz.gettz("America/Phoenix")
PT_ZONE = tz.gettz("America/Los_Angeles")

STANDARD_FMT = r"%-I:%M %p"
MILITARY_FMT = r"%H:%M"
MILITARY_FMT_S = r"%H:%M:%S"
ISO_FMT = r"%Y-%m-%dT%H:%M:%SZ"
ISO_FMT_ALT = r"%Y-%m-%dT%H:%M:%S"
ISO_FMT_MS = r"%Y-%m-%dT%H:%M:%S.%fZ"
SHORT_DATE_FMT = r"%b %-d"
FULL_DATE_FMT = r"%m/%d/%Y %I:%M:%S %p"

today = dt.date.today()
tmrw = today + dt.timedelta(days=1)

from .constants import *

def check_feed():
    metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
    url = f"{METRA_BASE}/raw/published.txt"
    response = requests.get(url,auth=metra_auth)
    return response.text.strip()

    # Unsure if I need this anymore -----
    
    # with open(os.path.abspath("./metra/metra_google_transit/today.txt")) as txtfile:
    #     last_published = txtfile.read()
    # return last_published
    
    # -----------------------------------

def get_now(tz=CT_ZONE):
    return dt.datetime.today().astimezone(tz=tz)

def split_date(date_str):
    d = date_str
    date = d[:8]
    date = f"{date[:4]}-{date[4:6]}-{date[6:]}"
    return date

def time_to_standard_with_date(time_str):
    # 04:08:00
    t = time_str
    isTmrw = False
    if t[:2] == "24":
        t = f"00:{t[3:5]}:{t[-2:]}"
        isTmrw = True
    try:
        t_obj = dt.datetime.strptime(t,MILITARY_FMT_S)
        if isTmrw is False:
            return f'{dt.datetime.strftime(t_obj,STANDARD_FMT)}'
        else:
            return f'{dt.datetime.strftime(t_obj,STANDARD_FMT)} (nd)'
    except:
        return ""

def get_static_stops(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/stops"
        response = requests.get(url,auth=metra_auth)
        data = []
        for stop in response.json():
            data.append([
                stop["stop_id"],
                stop["stop_name"],
                stop["stop_lat"],
                stop["stop_lon"],
                stop["zone_id"],
                stop["stop_url"],
                stop["wheelchair_boarding"]
            ])
        df = pd.DataFrame(data=data,columns=("stop_id","stop_name","lat","lon","zone_id","stop_url","wheelchair_boarding"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/stops.txt"),index=False)
    else:
        return pd.read_csv(os.path.abspath("./metra/metra_google_transit/stops.txt"),index_col=False,dtype="str")

def get_static_stop_times(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/stop_times"
        response = requests.get(url,auth=metra_auth)
        d_obj = dt.datetime.strptime(check_feed(),FULL_DATE_FMT)
        data = []
        resp = response.json()
        for idx,st in enumerate(resp):
            trip_id = st["trip_id"]

            arrivalTime = st["arrival_time"]
            

            tDelt = st["departure_time"]
            next_day = 0
            
            if int(tDelt[:2]) > 23:
                next_day = 1
                diff = abs(24 - int(tDelt[:2]))
                arrivalTime = f"0{diff}:{tDelt[3:5]}:{tDelt[-2:]}"
                at = dt.datetime.strptime(arrivalTime,MILITARY_FMT_S)
                arrivalTime = dt.datetime(year=d_obj.year,month=d_obj.month,day=d_obj.day,hour=at.hour,minute=at.minute,second=at.second)
                arrivalTime = arrivalTime + dt.timedelta(days=1)
            else:
                at = dt.datetime.strptime(arrivalTime,MILITARY_FMT_S)
                arrivalTime = dt.datetime(year=d_obj.year,month=d_obj.month,day=d_obj.day,hour=at.hour,minute=at.minute,second=at.second)
            
            arrivalTime = arrivalTime.strftime(FULL_DATE_FMT)

            # hours = int(tDelt[:2])
            # minutes = int(tDelt[3:5])
            # seconds = int(tDelt[-2:])

            if 'BNSF' in trip_id:
                route_id = 'BNSF'
            elif 'HC' in trip_id:
                route_id = 'HC'
            elif 'MD-N' in trip_id:
                route_id = 'MD-N'
            elif 'MD-W' in trip_id:
                route_id = 'MD-W'
            elif 'ME' in trip_id:
                route_id = 'ME'
            elif 'NCS' in trip_id:
                route_id = 'NCS'
            elif 'RI' in trip_id:
                route_id = 'RI'
            elif 'SWS' in trip_id:
                route_id = 'SWS'
            elif 'UP-N' in trip_id:
                route_id = 'UP-N'
            elif 'UP-NW' in trip_id:
                route_id = 'UP-NW'
            elif 'UP-W' in trip_id:
                route_id = 'UP-W'

            data.append([
                trip_id,
                route_id,
                arrivalTime,
                tDelt,
                next_day,
                st["stop_id"],
                st["stop_sequence"],
                st["pickup_type"],
                st["drop_off_type"],
                st["center_boarding"],
                st["south_boarding"],
                st["bikes_allowed"],
                st["notice"]])

        df = pd.DataFrame(data=data,columns=("trip_id","route_id","arrival_time","tDelt","nextDay","stop_id","stop_sequence","pickup_type","drop_off_type","center_boarding","south_boarding","bikes_allowed","notice"))
        df = df.sort_values(by=["trip_id","arrival_time"],ascending=[True,True])


        # Calculating and adding time elapsed for each trip ========================================================
        sep_dfs = []
        for trip in set(df.trip_id):
            sep_df = df[df["trip_id"]==trip]
            og_time = sep_df.iloc[0].arrival_time
            og_time_obj = dt.datetime.strptime(og_time,FULL_DATE_FMT)
            time_diffs = []
            time_diffs_overall = []
            for idx in range(len(sep_df)):
                if idx==0:
                    time_diffs.append("-")
                    time_diffs_overall.append("-")
                else:
                    prevRow = sep_df.iloc[idx-1]
                    currRow = sep_df.iloc[idx]
                    prevTime = prevRow.arrival_time
                    upcoTime = currRow.arrival_time
                    prevTime_obj = dt.datetime.strptime(prevTime,FULL_DATE_FMT)
                    upcoTime_obj = dt.datetime.strptime(upcoTime,FULL_DATE_FMT)
                    time_diffs.append(int((upcoTime_obj - prevTime_obj).seconds/60))
                    time_diffs_overall.append(int((upcoTime_obj - og_time_obj).seconds/60))
            sep_df.insert(2,"time_diff",time_diffs)
            sep_df.insert(2,"time_elapsed",time_diffs_overall)
            sep_dfs.append(sep_df)
        df = pd.concat(sep_dfs)
        # ===========================================================================================================
        
        df.to_csv(os.path.abspath("./metra/metra_google_transit/stop_times.txt"),index=False)
    else:
        return pd.read_csv(os.path.abspath("./metra/metra_google_transit/stop_times.txt"),index_col=False,dtype="str")

def get_static_trips(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/trips"
        response = requests.get(url,auth=metra_auth)
        data = []
        for t in response.json():
            data.append([
                t["route_id"],
                t["service_id"],
                t["trip_id"],
                t["trip_headsign"],
                t["shape_id"],
                t["direction_id"]])
        
        df = pd.DataFrame(data=data,columns=("route_id","service_id","trip_id","trip_headsign","shape_id","direction_id"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/trips.txt"),index=False)

    else:
        df = pd.read_csv(os.path.abspath("./metra/metra_google_transit/trips.txt"),index_col=False,dtype="str")
        return df

def get_static_shapes(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/shapes"
        response = requests.get(url,auth=metra_auth)
        data = []
        for s in response.json():
            data.append([
                s["shape_id"],
                s["shape_pt_lat"],
                s["shape_pt_lon"],
                s["shape_pt_sequence"]])
        
        df = pd.DataFrame(data=data,columns=("shape_id","pt_lat","pt_lon","pt_sequence"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/shapes.txt"),index=False)
    else:
        df = pd.read_csv(os.path.abspath("./metra/metra_google_transit/shapes.txt"),index_col=False,dtype="str")
        return df

def get_static_routes(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/routes"
        response = requests.get(url,auth=metra_auth)
        data = []
        for r in response.json():
            data.append([
                r["route_id"],
                r["route_long_name"],
                r["route_type"],
                r["route_color"],
                r["route_text_color"],
                r["route_url"]])

        df = pd.DataFrame(data=data,columns=("route_id","route_long_name","route_type","route_color","route_text_color","route_url"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/routes.txt"),index=False)
    else:
        df = pd.read_csv(os.path.abspath("./metra/metra_google_transit/routes.txt"),index_col=False,dtype="str")
        return df

def get_static_calendar(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/calendar"
        response = requests.get(url,auth=metra_auth)
        data = []
        for c in response.json():
            data.append([
                c["service_id"],
                c["sunday"],
                c["monday"],
                c["tuesday"],
                c["wednesday"],
                c["thursday"],
                c["friday"],
                c["saturday"],
                c["start_date"],
                c["end_date"]])

        df = pd.DataFrame(data=data,columns=("service_id","sunday","monday","tuesday","wednesday","thursday","friday","saturday","start_date","end_date"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/calendar.txt"),index=False)
    else:
        df = pd.read_csv(os.path.abspath("./metra/metra_google_transit/calendar.txt"),index_col=False,dtype="str")
        return df

def get_static_calendar_dates(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/calendar_dates"
        response = requests.get(url,auth=metra_auth)
        data = []
        for c in response.json():
            data.append([
                c["service_id"],
                c["date"],
                c["exception_type"]])

        df = pd.DataFrame(data=data,columns=("service_id","date","exception_type"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/calendar_dates.txt"),index=False)
    else:
        df = pd.read_csv(os.path.abspath("./metra/metra_google_transit/calendar_dates.txt"),index_col=False,dtype="str")
        return df

def get_static_fare_rules(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/fare_rules"
        response = requests.get(url,auth=metra_auth)
        data = []
        for f in response.json():
            data.append([
                f["fare_id"],
                f["origin_id"],
                f["destination_id"]])

        df = pd.DataFrame(data=data,columns=("fare_id","origin_id","destination_id"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/fare_rules.txt"),index=False)
    else:
        df = pd.read_csv(os.path.abspath("./metra/metra_google_transit/fare_rules.txt"),index_col=False,dtype="str")
        return df

def get_static_fare_attributes(__dlmode=True):
    if __dlmode is True:
        metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        url = f"{METRA_BASE}/schedule/fare_attributes"
        response = requests.get(url,auth=metra_auth)
        data = []
        for f in response.json():
            data.append([
                f["fare_id"],
                str(round(f["price"],2)),
                f["currency_type"],
                f["payment_method"],
                f["transfers"]
                # f["transfer_duration"]
                ])

        df = pd.DataFrame(data=data,columns=("fare_id","price","currency_type","payment_method","transfers"))
        df.to_csv(os.path.abspath("./metra/metra_google_transit/fare_attributes.txt"),index=False)
    else:
        df = pd.read_csv(os.path.abspath("./metra/metra_google_transit/fare_attributes.txt"),index_col=False,dtype="str")
        return df

def update_static_feed():
    """Updates Metra static data"""
    get_static_stops()
    get_static_stop_times()
    get_static_trips()
    get_static_shapes()
    get_static_routes()
    get_static_calendar()
    get_static_calendar_dates()
    get_static_fare_rules()
    get_static_fare_attributes()
    with open(os.path.abspath("./metra/metra_google_transit/today.txt"),"w+") as txtfile:
        txtfile.write(check_feed())

def get_rt_alerts():
    metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
    url = f"{METRA_BASE}/alerts"
    response = requests.get(url,auth=metra_auth)
    return response.json()

def get_rt_positions(trip_id=None):
    metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
    if trip_id is None:
        url = f"{METRA_BASE}/positions"
    else:
        url = f"{METRA_BASE}/positions/{trip_id}"
    response = requests.get(url,auth=metra_auth)
    return response.json()

def get_rt_trip_updates():
    metra_auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
    url = f"{METRA_BASE}/tripUpdates"
    response = requests.get(url,auth=metra_auth)
    return response.json()
