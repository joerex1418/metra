import re, io, csv
import datetime as dt
import requests, zipfile
from typing import Union, Dict, List

from . import api
from .api import StaticAPI
from .api import RealTimeAPI
from .api import stops
from .api import trips
from .api import shapes
from .api import routes
from .api import calendar
from .api import calendar_dates
from .api import stop_times
from .api import last_publish

from .utils import update_schedule_zip

from .constants import ROUTE_NAMES