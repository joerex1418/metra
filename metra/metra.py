from types import NoneType
from .constants import *

from .utils import prettify_time
from .utils import get_distance
from .utils_metra import *


# ====================================================================================================
# Metra Objects
# ====================================================================================================
class Route:
    """
    Metra Route
    ===========

    #### List of Metra Routes                      
    - BNSF
    - HC
    - MD-N
    - MD-W
    - ME
    - NCS
    - RI
    - SWS
    - UP-N
    - UP-NW
    - UP-W
    
    """
    def __init__(self,route):
        self.__route_id = ROUTES_SHORTHAND[route]
        df = get_static_routes(False)

        row = df[df["route_id"]==self.__route_id]
        self.__route_name = row.route_long_name.item()
        self.__route_url = row.route_url.item()
        self.__route_color = row.route_color.item()
        self.__route_text_color = row.route_text_color.item()

        self.__stop_times = self.__filter_stop_times()
        self.__trips = self.__filter_trips()
        self.__shapes = self.__filter_shapes()
        self.__calendar = get_static_calendar(False)
        self.__calendar_dates = get_static_calendar_dates(False)
        self.__fare_rules = get_static_fare_rules(False)
        self.__fare_attributes = get_static_fare_attributes(False)
    
    def route_id(self):
        return self.__route_id
    
    def route_name(self):
        return self.__route_name

    def route_color(self):
        return self.__route_color

    def route_text_color(self):
        return self.__route_text_color
    
    def route_url(self):
        return self.__route_url

    def stop_times(self):
        return self.__stop_times

    def __filter_stop_times(self):
        df = get_static_stop_times(False)
        return df[df["route_id"]==self.__route_id]

    def trips(self):
        return self.__trips

    def __filter_trips(self):
        df = get_static_trips(False)
        return df[df["route_id"]==self.__route_id]

    def shapes(self):
        return self.__shapes

    def __filter_shapes(self):
        df = get_static_shapes(False)
        rows_to_include = []
        for idx in range(len(df)):
            row = df.iloc[idx]
            if self.__route_id in row.shape_id:
                rows_to_include.append(row)
        return pd.DataFrame(rows_to_include)

class Trip:
    def __init__(self,trip_id):
        self.__trip_id = trip_id
        self.__position = self.follow()

    def position(self):
        """Return data without updating"""
        return self.__position

    def follow(self):
        """Get geo data for a specific train"""
        return get_rt_positions(self.__trip_id)

class RouteSketch:
    def __init__(self,sketch_type,data):
        pass

class TransitData:
    """
    Interface with The Regional Transportation Authority (RTA) Data API to get Ridership & survey Data.
    """
    def __init__(self):
        self.__datasets = self.__get_datasets()
    
    def datasets(self):
        return self.__datasets
    
    def line_monthly(self):
        df = self.__get_line_monthly()
        return df
    
    def zone_monthly(self):
        df = self.__get_zone_monthly()
        return df

    def __get_line_monthly(self):
        url = "https://rtams.org/sites/default/files/Metra_Monthly_Ridership_by_Line_2003_2021_5.csv"
        return pd.read_csv(url,index_col=False).astype({"RIDES":"int"})

    def __get_zone_monthly(self):
        url = "https://rtams.org/sites/default/files/Metra_Monthly_Ridership_by_FareZone_2010_2021_5.csv"
        return pd.read_csv(url,index_col=False)

    def __get_datasets(self):
        url = "https://rtams.org/api/3/action/package_show?id=6a0c8a89-1fc7-4505-adb3-395484b0641d"
        resp = requests.get(url)
        
        data = []
        resources = resp.json()["result"][0]["resources"]
        for res in resources:
            data.append(res)
        
        df = pd.DataFrame(data)
        return df


# ====================================================================================================
# Metra API Wrappers
# ====================================================================================================
class Static:
    """
    # Metra GTFS Static Feed

    Interface with the static feed to display information from the local machine's GTFS txt files

    - Filters data by current date and time
    - Run 'metra.update_static_feed()' to download .txt files to local storage
    """
    def __init__(self,full_data=False):
        if full_data is False:
            self.__now = dt.datetime.now().strftime(r"%I:%M %p")
            self.__today_obj = dt.date.today()
            td = self.__today_obj
            self.__dow = td.strftime("%A").lower()

            self.__stops = get_static_stops(False)
            self.__routes = get_static_routes(False)
            self.__calendar = self.__filter_calendar()
            self.__calendar_dates = get_static_calendar_dates(False)
            self.__trips = self.__filter_trips()
            self.__shapes = self.__filter_shapes()
            self.__stop_times = self.__filter_stop_times()
            self.__fare_rules = get_static_fare_rules(False)
            self.__fare_attributes = get_static_fare_attributes(False)
        else:
            self.__stops = get_static_stops(False)
            self.__routes = get_static_routes(False)
            self.__calendar = get_static_calendar(False)
            self.__calendar_dates = get_static_calendar_dates(False)
            self.__trips = get_static_trips(False)
            self.__shapes = get_static_shapes(False)
            self.__stop_times = get_static_stop_times(False)
            self.__fare_rules = get_static_fare_rules(False)
            self.__fare_attributes = get_static_fare_attributes(False)

    def stops(self):
        """
        Get dataframe of information for each stop including their geolocation, zone, url, etc
        """
        return self.__stops

    def trips(self):
        """
        Trips for each route. A trip is a sequence of two or more stops that occur during a specific time period
        """
        return self.__trips

    def stop_times(self,upcoming_only=True):
        """
        Times that a vehicle arrives at and departs from stops for each trip
        """
        n = get_now().timetuple()
        now_ts = pd.Timestamp(year=n[0],day=n[2],month=n[1],hour=n[3],minute=n[4],second=n[5])
        df = self.__stop_times.copy()
        if upcoming_only is True:
            lst = list(now_ts < pd.to_datetime(df["arrival_time"],format=ISO_FMT))
            df.insert(4,"passed",lst)
            return df[df.passed==False]
        else:
            return df

    def shapes(self):
        """
        Rules for mapping vehicle travel paths, sometimes referred to as route alignments
        """
        return self.__shapes
    
    def routes(self):
        """
        Get Metra routes; A group of trips that are displayed to riders as a single service.
        """
        return self.__routes
    
    def calendar(self):
        """
        Get information on which services are running for the day
        """
        return self.__calendar
    
    def calendar_dates(self):
        """
        Exceptions for the services defined in the calendar.txt files
        """
        return self.__calendar_dates

    def fare_attributes(self):
        """
        Fare information for a transit agency's routes.
        """
        return self.__fare_attributes

    def fare_rules(self):
        """
        Rules to apply fares for itineraries.
        """
        return self.__fare_rules

    def inbound_trips(self):
        """
        Filter the 'trips' dataframe by INBOUND trips only
        """
        df = self.trips()
        return df[df["direction_id"]=="1"]

    def inbound_schedule(self,stop_id=None,route_id=None):
        """
        Get a schedule of all INBOUND trains' arrival times to Chicago for a specific stop ('stop_id') or for a specific route ('route_id')
        """
        trps = self.trips()
        df = stop_times()
        trps = trps[trps["direction_id"]=="1"]
        trip_ids = set(trps["trip_id"])
        if stop_id is not None:
            df = df[(df["trip_id"].isin(trip_ids)) & (df['stop_id']==stop_id.upper())]
        elif route_id is not None:
            df = df[(df["trip_id"].isin(trip_ids)) & (df['route_id']==route_id.upper())] 

        # df = df.sort_values(by="arrival_time",ascending=True)
        df = df.sort_values(by=["trip_id","arrival_time"],ascending=[True,True])
        return df.reset_index(drop=True)

    def outbound_trips(self):
        """
        Filter the 'trips' dataframe by OUTBOUND trips only
        """
        df = self.trips()
        return df[df["direction_id"]=="0"]

    def outbound_schedule(self,stop_id=None,route_id=None):
        """
        Get a schedule of all OUTBOUND trains' arrival times from Chicago for a specific stop ('stop_id') or for a specific route ('route_id')
        """
        trps = self.trips()
        df = stop_times()
        trps = trps[trps["direction_id"]=="0"]
        trip_ids = set(trps["trip_id"])
        if stop_id is not None:
            df = df[(df["trip_id"].isin(trip_ids)) & (df['stop_id']==stop_id.upper())]
        elif route_id is not None:
            df = df[(df["trip_id"].isin(trip_ids)) & (df['route_id']==route_id.upper())] 

        # df = df.sort_values(by="arrival_time",ascending=True)
        df = df.sort_values(by=["trip_id","arrival_time"],ascending=[True,True])
        return df.reset_index(drop=True)

    def trip_fare(self,origin,destination):
        """
        Get fare for a trip given the origin and destination zone IDs
        """
        df = self.__fare_rules
        if len(origin) != 1:origin_zone_id = self.__determine_zone(origin)
        else:origin_zone_id = origin

        if len(destination) != 1:dest_zone_id = self.__determine_zone(destination)
        else:dest_zone_id = destination

        trip_row = df[(df["origin_id"]==origin_zone_id) & (df["destination_id"]==dest_zone_id)]
        fare_id = trip_row.fare_id.item()
        df = self.__fare_attributes
        fare = df[df["fare_id"]==fare_id]
        return str(fare.price.item())
            
    def trip_stop_times(self,trip_id):
        """
        Get all stop times for a specific trip
        """
        df = self.__stop_times
        return df[df["trip_id"]==trip_id]
    
    def shape_coords(self,trip_id,return_df=False):
        """
        Get shape data for a given trip's route
        
        Params:
        -------
        - 'trip_id' (str): trip identifier - Required
            - e.g. - 'BNSF_BN1200_V4_C'
        - 'as_nested_list' (bool): whether to return the shape coordinates in a dataframe or as a nested list of coordinates for each point
            - Default: TRUE
        """
        tdf = self.__trips
        tdf = tdf[tdf["trip_id"]==trip_id]
        shape_id = tdf.iloc[0].shape_id
        sdf = self.__shapes
        shape_df = sdf[sdf["shape_id"]==shape_id]
        if return_df is True:
            return shape_df
        else:
            all_coords = []
            for idx in range(len(shape_df)):
                row = shape_df.iloc[idx]
                all_coords.append([round(float(row.pt_lat),10),round(float(row.pt_lon),10)])
            return all_coords

    def services(self):
        return self.__service_list
    
    def stations(self):
        """ALIAS for 'self.stops' method"""
        return self.stops()

    def __determine_zone(self,stop:str):
        if "chicago" in stop.lower() and "west" not in stop.lower():
            return "A"
        df = self.__stops
        for idx in range(len(df)):
            row = df.iloc[idx]
            if stop.lower() in row.stop_name.lower():
                return row.zone_id

    def __filter_calendar(self):
        today_obj = self.__today_obj
        df = get_static_calendar(False)
        active_rows = []
        for idx in range(len(df)):
            row = df.iloc[idx]

            sd = row.start_date
            sd_obj = dt.date(int(sd[:4]),int(sd[5:7]),int(sd[-2:]))
            ed = row.end_date
            ed_obj = dt.date(int(ed[:4]),int(ed[5:7]),int(ed[-2:]))

            if sd_obj <= today_obj <= ed_obj:
                active_rows.append(row)

        df = pd.DataFrame(active_rows)
        df = df[df[self.__dow]=="1"]
        self.__service_list = list(df["service_id"])
        return df
    
    def __filter_trips(self):
        df = get_static_trips(False)
        return df[df["service_id"].isin(self.__calendar["service_id"])].reset_index(drop=True)
    
    def __filter_stop_times(self):
        df = get_static_stop_times(False)
        trips = list(self.__trips["trip_id"])
        return df[df["trip_id"].isin(trips)].reset_index(drop=True)

    def __filter_shapes(self):
        df = get_static_shapes(False)
        shape_ids = tuple(self.__trips["shape_id"])
        return df[df["shape_id"].isin(shape_ids)]

    def __determine_direction(self,direction_id):
        pass

class RealTime:
    """
    # Metra GTFS Realtime Feed 

    Interface with Metra's Realtime API to display train, routes, and other information from the transit system in an easy-to-read format
    """
    def __init__(self):
        self.__update_now()
        self.__positions = get_rt_positions()
        self.__alerts = get_rt_alerts()
        self.__trip_updates = get_rt_trip_updates()
        
        self.__shapes = get_static_shapes(False)
        self.__stops = get_static_stops(False)
        self.__trips = get_static_trips(False)

    def alerts(self,update_on_call=True) -> pd.DataFrame:
        if update_on_call is True:
            self.__update_now()
            self.update(alerts=True)
        print(self.now)
        response = self.__alerts
        data = []
        for a in response:
            alert = a.get("alert",{})
            active_period_array = alert.get("active_period",[{}])
            start = active_period_array[0].get("start",{}).get("low")
            end = active_period_array[0].get("end",{}).get("low")
            try:start = prettify_time(start,input_tzone='utc')
            except:pass
            try:end = prettify_time(end,input_tzone='utc')
            except:pass

            inf_ent = alert.get("informed_entity",[{}])[0]

            if type(inf_ent) is dict:
                route_id = inf_ent.get("route_id",None)
                if route_id is None:
                    try:route_id = inf_ent.get("trip",{}).get("route_id")
                    except:route_id = None

                try:trip_id = inf_ent["trip"]["trip_id"]
                except:trip_id = None

                stop_id = inf_ent.get("stop_id",None)
            else:
                route_id = None
                trip_id = None
                stop_id = None


            short_desc = alert.get("header_text",{}).get("translation",[{}])[0].get("text","")
            full_desc = alert.get("description_text",{}).get("translation",[{}])[0].get("text","")

            data.append([
                # a.get("id",""),
                # a.get("is_deleted",False),
                a.get("trip_update",None),
                # a.get("vehicle",None),
                route_id,
                trip_id,
                stop_id,
                short_desc,
                full_desc,
                start,
                end])
        
        return pd.DataFrame(data=data,columns=("trip_update","route_id","trip_id","stop_id","short_desc","full_desc","start","end"))
    
    def positions(self,direction=None,update_on_call=True) -> pd.DataFrame:
        """
        Get the geographic position of all trains in currently in service
        """
        if update_on_call is True:
            self.__update_now()
            self.update(positions=True)
        print(self.now)
        response = self.__positions
        data = []
        try:
            for pos in response:
                # not cols --------------------------------------
                vehicle = pos["vehicle"] # vehicle dict
                t = vehicle["trip"]      # inner trip dict
                v = vehicle["vehicle"]   # inner vehicle dict
                p = vehicle["position"]  # inner position dict
                ts = vehicle["timestamp"]# inner timestamp dict
                # -----------------------------------------------

                # is_deleted = pos["is_deleted"]
                # trip_update = pos["trip_update"]

                trip_id = t["trip_id"]
                route_id = t["route_id"]
                dir_id = self.__get_direction_by_trip(trip_id)
                start_time = time_to_standard_with_date(t["start_time"])
                start_date = split_date(t["start_date"])

                # vehicle_id = v["id"]
                vehicle_label = v["label"]
                # license_plate = v["license_plate"]

                lat = str(round(float(p["latitude"]),15))
                lon = str(round(float(p["longitude"]),15))
                # bearing = p["bearing"]
                # odometer = p["odometer"]
                # speed = p["speed"]

                curr_stop_sequence = vehicle["current_stop_sequence"]
                stop_id = vehicle["stop_id"]
                status = vehicle["current_status"]

                low = prettify_time(ts["low"],input_tzone='utc')
                high = ts["high"]
                # unsigned = ts["unsigned"]

                # congestion_lvl = vehicle["congestion_level"]
                # occupancy_status = vehicle["occupancy_status"]

                # alert = pos["alert"]

                row_data = [
                    trip_id,
                    route_id,
                    # vehicle_id,
                    vehicle_label,
                    lat,
                    lon,
                    dir_id,
                    curr_stop_sequence, # specifically regarding Metra's feed, this either represents the current stop (when 'status' = 0) or the next stop (when 'status' = 2)
                    status,
                    stop_id,
                    start_time,
                    start_date,
                    # license_plate,
                    # trip_update,
                    # is_deleted,
                    low]

                data.append(row_data)

            df = pd.DataFrame(data=data,columns=POSITION_COLS)

            if direction is not None:
                if direction[0].lower()=="i":
                    df = df[df["dir_id"]=="1"]
                elif direction[0].lower()=="o":
                    df = df[df["dir_id"]=="0"]

        except:
            df = pd.DataFrame()


        return df

    def position(self,identifer:str|int,update_on_call=True) -> pd.DataFrame:
        """
        Get geo data for a specific train

        Params:
        -------
        - identifer (str): trip ID ('trip_id') or vehicle label (not 'vehicle_id')
        - update_on_call (bool): whether or not to update the data before returning values
            - Default = TRUE
        """
        identifer = str(identifer)
        df = self.positions(update_on_call=update_on_call)
        if identifer.isdigit():
            return df[df["vehicle_label"]==identifer]
        else:
            return df[df["trip_id"]==identifer]

    def trip_updates(self,route_id=None,direction=None,delayed=False,update_on_call=True) -> pd.DataFrame:
        """
        Get trip updates for a specific train

        Params:
        -------
        - route_id (str): filter data by route (e.g. "BNSF", "UP-NW")
        - direction (str): filter data by relative direction of travel; to or from the Chicago stations
            - "inbound" | "i"
            - "outbound" | "o"
        - delayed (bool): include data for delayed trains
            - NOTE: if there are no delayed trains in the dataset, this filter will not be applied
        - next_stop (bool):
        - update_on_call (bool): whether or not to update the data before returning values
            - Default = TRUE
        """
        if update_on_call is True:
            self.__update_now()
            self.update(trip_updates=True)
        response = self.__trip_updates
        data = []
        n = self.now_obj
        now_obj = dt.datetime(
            year=n.year,
            month=n.month,
            day=n.day,
            hour=n.hour,
            minute=n.minute,
            tzinfo=CT_ZONE)
        for update in response:
            # NOT COLS ---------------------
            tu = update.get("trip_update",{})
            stop_time_updates = tu["stop_time_update"]

            position = tu.get("position",{})
            
            trip_id = tu.get("trip",{}).get("trip_id","")
            rt_id = tu.get("trip",{}).get("route_id","")
            dir_id = self.__get_direction_by_trip(trip_id)
            # vehicle_id = tu.get("vehicle",{}).get("id","")
            vehicle_label = tu.get("vehicle",{}).get("label","")
            
            lat = str(position.get("vehicle",{}).get("position",{}).get("latitude",""))
            lon = str(position.get("vehicle",{}).get("position",{}).get("longitude",""))
            
            status =  tu.get("position",{}).get("vehicle",{}).get("current_status","")

            trip_start_time = tu.get("trip",{}).get("start_time")
            # ts_update = tu.get("timestamp",{}).get("low","")
            # ts_vehicle = position.get("vehicle",{}).get("timestamp",{}).get("low","")

         # ---- Stop Time Update -----------
            for stu in stop_time_updates:
                schedArrival = stu["arrival"]["time"]["low"]
                schedArrival = prettify_time(schedArrival,input_tzone='utc')
                schedDepart = stu["departure"]["time"]["low"]
                # schedDepart = prettify_time(schedDepart,input_tzone='utc')
                #schedDepart = dt.datetime.strptime(schedDepart,ISO_FMT_MS) #.astimezone(UTC_ZONE).strftime(ISO_FMT_MS)
                at_obj = dt.datetime.strptime(schedDepart,ISO_FMT_MS)
                arr_obj = dt.datetime(
                    year=at_obj.year,
                    month=at_obj.month,
                    day=at_obj.day,
                    hour=at_obj.hour,
                    minute=at_obj.minute,
                    tzinfo=UTC_ZONE).astimezone(CT_ZONE)
                eta = (arr_obj - now_obj).seconds
                stop_updates = [
                    time_to_standard_with_date(trip_start_time),
                    # ts_update,
                    # ts_vehicle,
                    trip_id,
                    rt_id,
                    dir_id,
                    # vehicle_id,
                    vehicle_label,
                    lat,
                    lon,
                    status,
                    stu["stop_sequence"],
                    stu["stop_id"],
                    stu["arrival"]["delay"],
                    schedArrival,                       # scheduled arrival time
                    # stu["arrival"]["time"]["high"],
                    # stu["arrival"]["time"]["unsigned"],
                    # stu["arrival"]["uncertainty"],
                    # stu["departure"]["delay"],
                    eta,                                # estimated arrival time in seconds
                    # stu["departure"]["time"]["high"],
                    # stu["departure"]["time"]["unsigned"],
                    # stu["departure"]["uncertainty"],
                    # stu["schedule_relationship"]
                    ]

                data.append(stop_updates)
        
        df = pd.DataFrame(data=data,columns=TRIP_UPDATE_COLS).sort_values(by=["trip_id","stop_sequence"],ascending=[True,True])
        
        if route_id is not None:
            df = df[df["route_id"]==route_id]

        if delayed is True:
            if len(df[df["arrDly"]!=0]) != 0:
                df = df[df["arrDly"]!=0]
        if direction is not None:
            if direction[0].lower()=="i":
                df = df[df["dir_id"]=="1"]
            elif direction[0].lower()=="o":
                df = df[df["dir_id"]=="0"]
        return df

    def trip_update(self,trip_id,update_on_call=True) -> pd.DataFrame:
        """
        Get trip updates for a specific train

        Params:
        -------
        - trip_id (str): trip ID to retrieve data for
        - update_on_call (bool): whether or not to update the data before returning values
            - Default = TRUE
        """
        df = self.trip_updates(update_on_call=update_on_call)
        return df[df["trip_id"]==trip_id]

    def update(self,positions=False,alerts=False,trip_updates=False):
        """
        Fetch specified datasets to update data from API

        EXAMPLES:\n
        - `update(alerts=True)`
            - update the 'alerts' dataset only
        - `update(positions=True,trip_updates=True)` 
            - update the 'positions' and 'trip_updates' datasets (does not update 'alerts')
        """
        if positions is True:
            self.__positions = get_rt_positions()
        if alerts is True:
            self.__alerts = get_rt_alerts()
        if trip_updates is True:
            self.__trip_updates = get_rt_trip_updates()

    def update_all(self):
        self.__positions = get_rt_positions()
        self.__alerts = get_rt_alerts()
        self.__trip_updates = get_rt_trip_updates()
    
    def __update_now(self):
        self.now_obj = get_now()
        self.now_iso_str = self.now_obj.isoformat()
        self.now = self.now_obj.strftime(r"%I:%M %p")

    def __get_direction_by_trip(self,trip_id):
        tdf = self.__trips
        tdf = tdf[tdf.trip_id==trip_id]
        return tdf.iloc[0]["direction_id"]
    
   # ALIASES =======================================================================================
    def notices(self,update_on_call=True) -> pd.DataFrame:
        """
        ALIAS for 'alerts()'
        """
        return self.alerts(update_on_call)
    def stop_times(self,route_id=None,direction=None,delayed=False,update_on_call=True) -> pd.DataFrame:
        """
        ALIAS for 'trip_updates()'
        """
        return self.trip_updates(route_id,direction,delayed,update_on_call)
    def locations(self,direction=None,update_on_call=True) -> pd.DataFrame:
        """
        ALIAS for 'positions()'
        """
        return self.positions(direction,update_on_call)
    def location(self,identifer:str|int,update_on_call=True) -> pd.DataFrame:
        """
        ALIAS for 'position()'
        """
        return self.position(identifer,update_on_call)
   # ===============================================================================================


# ====================================================================================================
# Functions
# ====================================================================================================
def routes():
    return get_static_routes(False)

def trips():
    return get_static_trips(False)

def stops():
    return get_static_stops(False)

def stop_times():
    return get_static_stop_times(False)

def shapes():
    return get_static_shapes(False)

def calendar():
    return get_static_calendar(False)

def calendar_dates():
    return get_static_calendar_dates(False)

def fare_attributes():
    return get_static_fare_attributes(False)

def fare_rules():
    return get_static_fare_rules(False)

def trip_info(trip_id):
    df = get_static_trips(False)
    trp = df[df.trip_id==trip_id].iloc[0]
    trp["direction"] = "inbound" if trp["direction_id"] == "1" else "outbound"
    return trp

def trip_fare(origin_id,destination_id):
    """
    Get fare for a trip given the origin station ID & destination station ID

    Required Params:
    ----------------
    - 'origin_id': station ID of train-boarding
    - 'destination_id': station ID of train disembark
    """
    df = get_static_fare_rules(False)

    origin_zone_id = determine_zone_util(origin_id)

    dest_zone_id = determine_zone_util(destination_id)

    trip_row = df[(df["origin_id"]==origin_zone_id) & (df["destination_id"]==dest_zone_id)]
    try:
        fare_id = trip_row.fare_id.item()
        df = get_static_fare_attributes(False)
        fare = df[df["fare_id"]==fare_id]
        fare_amt = str(fare.price.item())
        if fare_amt[-2] == ".":
            fare_amt = fare_amt + "0"
        return fare_amt
    except:
        print("ERROR: Unable to retrieve fare information")
        return None

def trip_schedule(trip_id):
    df = get_static_stop_times(False)
    return df[df.trip_id==trip_id]

def inbound_schedule(route_id=None,date=None):
    """
    Get a schedule of all INBOUND trains' arrival times to Chicago for a specific route. A departure schedule for a specific date can be specified as well. Otherwise it will default to today's date

    Params:
    -------
    - 'route_id': route identifer
    - 'date': format, YYYY-mm-dd (Default is today's date)
    """
    c = get_static_calendar(False)
    trps = get_static_trips(False)
    # MIGHT BE MORE EFFICIENT IF ONLY NECESSARY STOP TIMES DATA IS RETRIEVED (INBOUND vs OUTBOUND)
    st = get_static_stop_times(False)

    dat = date
    if dat is None:
        dat_obj = dt.datetime.today()
    else:
        dat_obj = dt.datetime.strptime(date,STANDARD_DATE_FMT)

    dow = dat_obj.strftime("%A") # day of the week

    # filtering 'calendar' df for applicable date ranges
    results = []
    for idx in range(len(c)):
        row = c.iloc[idx]
        start_obj = dt.datetime.strptime(row.start_date,STANDARD_DATE_FMT)
        end_obj = dt.datetime.strptime(row.end_date,STANDARD_DATE_FMT)
        if start_obj <= dat_obj <= end_obj:
            results.append(row)
    cal_df = pd.DataFrame(results)
    cal_df = cal_df[cal_df[dow.lower()]=="1"]

    # collecting relevant service IDs
    sids = list(cal_df['service_id'])

    # filtering 'trips' dataframe by relevant service IDs
    trps = trps[trps['service_id'].isin(sids)]

    # collecting INBOUND trip IDs
    trps = trps[trps["direction_id"]=="1"]
    trip_ids = set(trps["trip_id"])

    # filtering 'stop times' dataframe by relevant trip IDs
    if route_id is not None:
        if len(route_id) > 5:
            route_id = ROUTE_NAMES[route_id.title()]
        else:
            route_id = ROUTES_SHORTHAND[route_id.lower()]
        st = st[st["route_id"]==route_id]

    st = st[st["trip_id"].isin(trip_ids)]
    st = st.sort_values(by="arrival_time",ascending=True)
    st = st.sort_values(by=["trip_id","arrival_time"],ascending=[True,True])
    return st.reset_index(drop=True)

def outbound_schedule(route_id=None,date=None):
    """
    Get a schedule of all OUTBOUND trains' arrival times from Chicago for a specific route. A departure schedule for a specific date can be specified as well. Otherwise it will default to today's date

    Params:
    -------
    - 'route_id': route identifer
    - 'date': format, YYYY-mm-dd (Default is today's date)
    """
    c = get_static_calendar(False)
    trps = get_static_trips(False)
    # MIGHT BE MORE EFFICIENT IF ONLY NECESSARY STOP TIMES DATA IS RETRIEVED (INBOUND vs OUTBOUND)
    st = get_static_stop_times(False)

    dat = date
    if dat is None:
        dat_obj = dt.datetime.today()
    else:
        dat_obj = dt.datetime.strptime(date,STANDARD_DATE_FMT)

    dow = dat_obj.strftime("%A") # day of the week

    # filtering 'calendar' df for applicable date ranges
    results = []
    for idx in range(len(c)):
        row = c.iloc[idx]
        start_obj = dt.datetime.strptime(row.start_date,STANDARD_DATE_FMT)
        end_obj = dt.datetime.strptime(row.end_date,STANDARD_DATE_FMT)
        if start_obj <= dat_obj <= end_obj:
            results.append(row)
    cal_df = pd.DataFrame(results)
    cal_df = cal_df[cal_df[dow.lower()]=="1"]

    # collecting relevant service IDs
    sids = list(cal_df['service_id'])

    # filtering 'trips' dataframe by relevant service IDs
    trps = trps[trps['service_id'].isin(sids)]

    # collecting OUTBOUND trip IDs
    trps = trps[trps["direction_id"]=="0"]
    trip_ids = set(trps["trip_id"])

    # filtering 'stop times' dataframe by relevant trip IDs
    if route_id is not None:
        if len(route_id) > 5:
            route_id = ROUTE_NAMES[route_id.title()]
        else:
            route_id = ROUTES_SHORTHAND[route_id.lower()]
        st = st[st["route_id"]==route_id]

    st = st[st["trip_id"].isin(trip_ids)]
    st = st.sort_values(by="arrival_time",ascending=True)
    st = st.sort_values(by=["trip_id","arrival_time"],ascending=[True,True])
    return st.reset_index(drop=True)

def schedule(station_id,direction,date=None):
    """
    Get dataframe of scheduled departures for a specific station. A departure schedule for a specific date can be specified as well. Otherwise it will default to today's date

    Params:
    -------
    - 'station_id': identifier for boarding station
    - 'direction': 'inbound' or 'outbound'
        - shorthand accepted -> 'ib' | 'ob'
    - 'date': format, YYYY-mm-dd (Default is today's date)
    """
    c = get_static_calendar(False)
    trps = get_static_trips(False)
    # MIGHT BE MORE EFFICIENT IF ONLY NECESSARY STOP TIMES DATA IS RETRIEVED (INBOUND vs OUTBOUND)
    st = get_static_stop_times(False)

    dat = date
    if dat is None:
        dat_obj = dt.datetime.today()
    else:
        dat_obj = dt.datetime.strptime(date,STANDARD_DATE_FMT)

    dow = dat_obj.strftime("%A") # day of the week

    # filtering 'calendar' df for applicable date ranges
    results = []
    for idx in range(len(c)):
        row = c.iloc[idx]
        start_obj = dt.datetime.strptime(row.start_date,STANDARD_DATE_FMT)
        end_obj = dt.datetime.strptime(row.end_date,STANDARD_DATE_FMT)
        if start_obj <= dat_obj <= end_obj:
            results.append(row)
    cal_df = pd.DataFrame(results)
    cal_df = cal_df[cal_df[dow.lower()]=="1"]

    # collecting relevant service IDs
    sids = list(cal_df['service_id'])

    # filtering 'trips' dataframe by relevant service IDs & direction (inbound/outbound)
    trps = trps[trps['service_id'].isin(sids)]
    direction = str(direction).lower()
    if direction == "inbound" or direction == "ib" or direction == "i" or direction == "1":
        trps = trps[trps["direction_id"]=="1"]
    elif direction == "outbound" or direction == "ob" or direction == "o" or direction == "0":
        trps = trps[trps["direction_id"]=="0"]

    # collecting relevant trip IDs
    trip_ids = set(trps["trip_id"])

    # filtering 'stop times' dataframe by relevant trip IDs & requested station ID ('origin' paramater)
    st = st[st["trip_id"].isin(trip_ids)]
    st = st[st["stop_id"]==station_id].sort_values(by="arrival_time",ascending=True)
    return st.reset_index(drop=True)

def station_search(query):
    return station_search_util(query)


