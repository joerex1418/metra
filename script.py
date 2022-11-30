import pprint
import itertools
import datetime as dt
import io, os, re, csv
import zipfile, tempfile
from typing import Dict, List, Union, Optional, TypedDict

# import pandas as pd
from tabulate import tabulate

from metra import static
# from metra import trip_stop_times, active_services, active_trips

api = static.StaticAPI()

results = api.next_trains('NAPERVILLE','CUS',datetime=dt.datetime(2022,11,30,5,0),cmd=True)
# route_trips = list(filter(lambda x: "BNSF" in x['trip_id'], api.trips()))

# all_stop_times = api.stop_times()
# for route in api.routes():
#     trips_by_stop_count = {}
#     for t in route_trips:
#         if t['trip_id'][-1] == 'C' and 'OB' in t['shape_id']:
#             trip_stop_times = list(filter(lambda x: x["trip_id"] == t['trip_id'], all_stop_times))
#             if len(trip_stop_times) in trips_by_stop_count.keys():
#                 trips_by_stop_count[len(trip_stop_times)].append(t['trip_id'])
#             else:
#                 trips_by_stop_count[len(trip_stop_times)] = []
#                 trips_by_stop_count[len(trip_stop_times)].append(t['trip_id'])
#     pprint.pprint(trips_by_stop_count)

# for st in api.trip_stops('BNSF_BN1239_V2_C'):
#     st['zone_id'] = api.get_stop(st['stop_id'])['zone_id']
#     print(f"{st['stop_id']:10} | {st['zone_id']:1} | {st['stop_sequence']:<2} | {st['arrival_time']}")

# pprint.pprint(results)

# x = "BNSF_BN1262_V2_C"
# y = "BNSF_UPW1284_V2_C"
# z = "BNSF_U1268_V3_C"

# regex_string = r"([\D]+)_([\D]+)(\d{4})"
# ptrn = re.compile(regex_string)

