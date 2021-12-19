from .constants import *

from .utils import prettify_time
from .utils import get_distance
from .utils_metra import *

class StaticFeed:
    """
    # Metra GTFS Static Feed

    Interface with the static feed to display information from the local machine's GTFS txt files

    - Filters data by current date and time
    - Run 'metra.update_static_feed()' to download .txt files to local storage

    """
    def __init__(self):
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
        
        # Aliases --------------
        # stations = stops

        # ----------------------

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
            lst = list(now_ts < pd.to_datetime(df["arrival_time"]))
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

    def trains_to(self,destination):
        """
        Get a dataframe of trips going to a specific destination
        """
        df = self.__trips
        if "chicago" == destination.lower():
            return df[df["direction_id"]=="1"]
        elif "ogilvie" in destination.lower():
            destination = "Chicago OTC"
        elif "otc" in destination.lower():
            destination = "Chicago OTC"
        elif "union station" in destination.lower():
            destination = "Chicago Union Station"
        including = []
        for idx, loc in enumerate(df.trip_headsign):
            if destination.lower() in loc.lower():
                including.append(df.iloc[idx])
        return pd.DataFrame(including)

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

    def inbound(self):
        df = self.trips()
        return df[df["direction_id"]=="1"]

    def outbound(self):
        df = self.trips()
        return df[df["direction_id"]=="0"]

    def services(self):
        return self.__service_list

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

class RealTimeFeed:
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

# API Wrappers ====================================================================================

class RealTimeAPI:
    """
    Metra GTFS-RealTime API
    ========================
    Wrapper object to communicate with the API for Metra's RealTime Transit Feed

    ## From Metra website
    - Realtime data is provided in both RAW and JSON format. This data is updated every 30 seconds, so there is no need to check any more frequently. If at any time realtime data is not available for any schedule or trip, it is assumed that the static schedule is correct.

    - Alerts 
        - "Regardless of the 'active_period' defined in an alert, if an alert is in the feed it is assumed to be active. Conversely, if an alert is not in the feed (regardless of the end specified in active_period) it is assumed to no longer be active."

    - Vehicle Positions
        - "On occasion when a train is underground or at a terminal it will lose sight with the GPS satellites. When a train is scheduled to have begun a trip and no vehicle position is available it is assumed that the train is in route."

    - Trip Updates 
        - "Trip updates will provide realtime information for the scheduled trip. When a train is tracking (reporting GPS coordinates) a trip update will be provided for the trip. If no trip update is available and a trip is scheduled to have begun, it is assumed that the train is running according to schedule. Note that a trip update does not always indicate a running train. Trip updates may be provided hours ahead of time in an instance of an annulled or added train. Also, in cases where the trip is modified such as having a stop added or removed, a trip update will be available regardless of the start time for the trip."

    """
    def __init__(self):
        self.__auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)

    def __repr__(self) -> str:
        return """<metra.RealTimeAPI RealTime Wrapper>"""

    def alerts(self):
        """
        Get all active alerts/service bulletins for routes and stations
        """
        url = METRA_BASE + "/alerts"
        return requests.get(url,auth=self.__auth).json()
    
    def positions(self,trip_id=None):
        """
        Get the current positions and other info of all trains currently being tracked in realtime

        Specify a 'trip_id' to filter results by trip (e.g. "UP-W_UW46_V1_C")
        """
        if trip_id is None:
            endpoint = "/positions"
        else:
            endpoint = f"/positions/{trip_id}"
        url = METRA_BASE + endpoint
        return requests.get(url,auth=self.__auth).json()

    def trip_updates(self,route_id=None):
        """
        Get trip updates for trains being tracked in realtime.

        Specify a 'route_id' to filter results by route (e.g. "BNSF")
        """
        if route_id is None:
            endpoint = "/tripUpdates"
        else:
            endpoint = f"/tripUpdates/{route_id}"
        url = METRA_BASE + endpoint
        return requests.get(url,auth=self.__auth).json()

class StaticAPI:
    """
    Metra GTFS-Static API
    ========================

    Wrapper object to communicate with the API for Metra's Static Transit Feed

    ## From Metra website
    - "The static file is updated periodically, reflecting the most recent schedule for Metra trains. 
    For convenience, we provide a text file with the date and time that the schedule was published.
    The schedule may update at any given time, so developers are encouraged use this to determine 
    if it is necessary to grab and rebuild the schedule. For a planned schedule update, the new 
    file will be published at 3:00:00 AM; however, occasionally there may be a sudden change that 
    requires us to push a new schedule immediately. Checking the published.txt file every few 
    minutes will ensure you get the most recent schedule regardless of when we publish it."
    
    """
    def __init__(self,call_once=False):
        self.__auth = requests.auth.HTTPBasicAuth(METRA_API_KEY, METRA_SECRET_KEY)
        self.__call_once = call_once
        if call_once is True:
            self.__routes = self.__get_routes()
            self.__trips = self.__get_trips()
            self.__stops = self.__get_stops()
            self.__stop_times = self.__get_stop_times()
            self.__shapes = self.__get_shapes()
            self.__calendar = self.__get_calendar()
            self.__calendar_dates = self.__get_calendar_dates()
            self.__fare_attributes = self.__get_fare_attributes()
            self.__fare_rules = self.__get_fare_rules()
            self.__agency = self.__get_agency()
            self.__published = self.__get_published()

    def __repr__(self) -> str:
        return """<metra.StaticAPI Static Feed Wrapper>"""

    def routes(self):
        if self.__call_once is True:
            return self.__routes
        else:
            return self.__get_routes()

    def trips(self):
        if self.__call_once is True:
            return self.__trips
        else:
            return self.__get_trips()

    def stops(self):
        if self.__call_once is True:
            return self.__stops
        else:
            return self.__get_stops()

    def stop_times(self,trip_id=None):
        if trip_id is not None:
            url = METRA_BASE + f"/schedule/stop_times/{trip_id}"
            return requests.get(url,auth=self.__auth).json()
        if self.__call_once is True:
            return self.__stop_times
        else:
            return self.__get_stop_times()

    def shapes(self):
        if self.__call_once is True:
            return self.__shapes
        else:
            return self.__get_shapes()

    def calendar(self):
        if self.__call_once is True:
            return self.__calendar
        else:
            return self.__get_calendar()

    def calendar_dates(self):
        if self.__call_once is True:
            return self.__calendar_dates
        else:
            return self.__get_calendar_dates()

    def fare_attributes(self):
        if self.__call_once is True:
            return self.__fare_attributes
        else:
            return self.__get_fare_attributes()

    def fare_rules(self):
        if self.__call_once is True:
            return self.__fare_rules
        else:
            return self.__get_fare_rules()

    def agency(self):
        if self.__call_once is True:
            return self.__agency
        else:
            return self.__get_agency()

    def published(self):
        if self.__call_once is True:
            return self.__published
        else:
            return self.__get_published()

    def __get_routes(self):
        url = METRA_BASE + "/schedule/routes"
        return requests.get(url,auth=self.__auth).json()

    def __get_trips(self):
        url = METRA_BASE + "/schedule/trips"
        return requests.get(url,auth=self.__auth).json()

    def __get_stops(self):
        url = METRA_BASE + "/schedule/stops"
        return requests.get(url,auth=self.__auth).json()

    def __get_stop_times(self):
        url = METRA_BASE + "/schedule/stop_times"
        return requests.get(url,auth=self.__auth).json()

    def __get_shapes(self):
        url = METRA_BASE + "/schedule/shapes"
        return requests.get(url,auth=self.__auth).json()

    def __get_calendar(self):
        url = METRA_BASE + "/schedule/calendar"
        return requests.get(url,auth=self.__auth).json()

    def __get_calendar_dates(self):
        url = METRA_BASE + "/schedule/calendar_dates"
        return requests.get(url,auth=self.__auth).json()

    def __get_fare_attributes(self):
        url = METRA_BASE + "/schedule/fare_attributes"
        return requests.get(url,auth=self.__auth).json()

    def __get_fare_rules(self):
        url = METRA_BASE + "/schedule/fare_rules"
        return requests.get(url,auth=self.__auth).json()

    def __get_agency(self):
        url = METRA_BASE + "/schedule/agency"
        return requests.get(url,auth=self.__auth).json()

    def __get_published(self):
        url = METRA_BASE + "/raw/published.txt"
        return requests.get(url,auth=self.__auth).text

# =================================================================================================

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
    return df[df.trip_id==trip_id]

def trip_schedule(trip_id):
    df = get_static_stop_times(False)
    return df[df.trip_id==trip_id]




