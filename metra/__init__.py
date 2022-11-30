import re, io, csv
import datetime as dt
import requests, zipfile
from typing import Union, Dict, List

from . import static
from .constants import ROUTE_NAMES

"""
Naperville to Chicago
inbound departures
inbound arrivals

outbound departures
outbound arrivals

"""