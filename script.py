import timeit
import typing
import pprint
import itertools
import datetime as dt
import io, os, re, csv
import zipfile, tempfile

import rich
import pandas as pd
from tabulate import tabulate

import metra
from metra import api, utils

# utils.update_schedule_zip()

static = api.StaticAPI()
rt = api.RealTimeAPI()

stop_times = api.stop_times()
stop_times_df = pd.DataFrame(stop_times)
del stop_times

routes = api.routes()
route_ids = [x["route_id"] for x in routes]

route_stop_orders = {}

datetime = dt.datetime.today()

# data = static.next_trains("NAPERVILLE", "CUS", datetime=dt.datetime(2023,9,11,5))
# data = static.trip_stops("BNSF_BN1206_V2_C")
# data = static.upcoming_trips("NAPERVILLE", "CUS", date=dt.date(2023, 9, 11))

n = 5
# result = timeit.timeit(stmt='static.next_trains("NAPERVILLE", "CUS", datetime=dt.datetime(2023,9,11,5))', globals=globals(), number=n)
# result = timeit.timeit(stmt='static.trip_stops("BNSF_BN1206_V2_C", return_generator=True)', globals=globals(), number=n)
result = timeit.timeit(stmt='static.upcoming_trips("NAPERVILLE", "CUS", date=dt.date(2023, 9, 11))', globals=globals(), number=n)
rich.print(f"Avg execution time is {result/n} seconds")

# rich.print(data)
# print(pd.DataFrame(data))

# for route_id in route_ids:
#     route_trip_ids = {x["trip_id"] for x in api.trips() if x["route_id"] == route_id}
    
#     df = stop_times_df[stop_times_df["trip_id"].isin(route_trip_ids)]
#     df = df.drop_duplicates(subset="stop_id")
    
#     route_stops: typing.List[typing.Dict] = []
#     for row_idx, row in df.iterrows():
#         stop_id = row["stop_id"]
#         route_stops.append({"stop_id": stop_id, "zone_id": static.get_stop(stop_id)["zone_id"]})
    
#     route_stops.sort(key=lambda x: x["zone_id"])
    
#     route_zones = [x["zone_id"] for x in route_stops]
    
#     for route_stop in route_stops:
#         route_stop["digit"] = 0
#         route_stop["decimal"] = 0
    
#     route_stops_copy = route_stops.copy()
    
#     for idx, route_stop in enumerate(route_stops_copy):
#         if idx - 1 == -1: continue
        
#         previous_route_stop = route_stops_copy[idx - 1].copy()
#         current_route_stop = route_stops_copy[idx].copy()
        
#         if current_route_stop["zone_id"] == previous_route_stop["zone_id"]:
#             route_stops[idx]["decimal"] = previous_route_stop["decimal"] + 1
        
#         if current_route_stop["zone_id"] != previous_route_stop["zone_id"]:
#             route_stops[idx]["digit"] = previous_route_stop["digit"] + 1
#         else:
#             route_stops[idx]["digit"] = previous_route_stop["digit"]
            
#     route_stop_orders[route_id] = {}
#     for route_stop in route_stops:
#         stop_id = route_stop["stop_id"]
#         stop_order = float(f"{route_stop['digit']}.{route_stop['decimal']}")
        
#         route_stop["order"] = stop_order
        
#         route_stop_orders[route_id][stop_id] = stop_order
    
