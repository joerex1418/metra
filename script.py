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
from metra import api
from metra import utils

# utils.update_schedule_zip()

static = api.StaticAPI()
rt = api.RealTimeAPI()

datetime = dt.datetime.today()

# data = static.next_trains("NAPERVILLE", "CUS", datetime=dt.datetime(2023,9,11,5))
# data = static.trip_stops("BNSF_BN1206_V2_C")
# data = static.upcoming_trips("NAPERVILLE", "CUS", date=dt.date(2023, 9, 11))

# n = 5
# result = timeit.timeit(stmt='static.next_trains("NAPERVILLE", "CUS", datetime=dt.datetime(2023,9,11,5))', globals=globals(), number=n)
# result = timeit.timeit(stmt='static.trip_stops("BNSF_BN1206_V2_C", return_generator=True)', globals=globals(), number=n)
# result = timeit.timeit(stmt='static.upcoming_trips("NAPERVILLE", "CUS", date=dt.date(2023, 9, 11))', globals=globals(), number=n)
# rich.print(f"Avg execution time is {result/n} seconds")

# rich.print(data)
# print(pd.DataFrame(data))

