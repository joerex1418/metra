"""
# PyMetra
Metra Transit Wrapper for Python

AUTHOR: Joe Rechenmacher
GITHUB: joerex1418
"""
from .metra import RealTime
from .metra import Static
from .metra import Route
from .metra import Trip
from .metra import RouteSketch
from .metra import TransitData

from .metra import routes
from .metra import trips
from .metra import stops
stations = stops
from .metra import stop_times
from .metra import shapes
from .metra import calendar
from .metra import calendar_dates
from .metra import fare_attributes
from .metra import fare_rules
from .metra import trip_info
from .metra import trip_fare
from .metra import trip_schedule
from .metra import inbound_schedule
from .metra import outbound_schedule
from .metra import schedule
from .metra import station_search
stop_search = station_search

from .metra import update_static_feed
from .metra import check_feed

# from .metra.metra import RealTimeFeed
# from .metra.metra import StaticFeed
# from .metra.metra import Route
# from .metra.metra import Trip
# from .metra.metra import RouteSketch
# from .metra.metra import RealTimeAPI
# from .metra.metra import StaticAPI

# from .metra.metra import routes
# from .metra.metra import trips
# from .metra.metra import stops
# from .metra.metra import stop_times
# from .metra.metra import shapes
# from .metra.metra import calendar
# from .metra.metra import calendar_dates
# from .metra.metra import fare_attributes
# from .metra.metra import fare_rules
# from .metra.metra import trip_info
# from .metra.metra import trip_schedule

# from .metra.metra import update_static_feed


