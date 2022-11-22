import pprint
import itertools
import datetime as dt
import io, os, re, csv
import zipfile, tempfile
from typing import Dict, List, Union, Optional, TypedDict

import pandas as pd
from tabulate import tabulate

from metra import static
from metra import trip_stop_times, active_services, active_trips

# x = "BNSF_BN1262_V2_C"
# y = "BNSF_UPW1284_V2_C"
# z = "BNSF_U1268_V3_C"

# regex_string = r"([\D]+)_([\D]+)(\d{4})"
# ptrn = re.compile(regex_string)

