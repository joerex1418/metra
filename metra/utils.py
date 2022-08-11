import requests
import zipfile as z
import datetime as dt
from dateutil.parser import parse
from urllib.request import urlopen
import base64 as base

from .paths import *
from .constants import METRA_BASE


def needs_update() -> bool:
    last_updated: dt.datetime
    z.ZipFile()
    try:
        with open(f"{DATA_PATH}/last_update.txt","r") as txtfile:
            last_updated = parse(txtfile.read())
        if dt.datetime.now() < last_updated:
            return True
        else:
            return False
    except:
        return True
    
def get_last_updated() -> dt.datetime:
    url = METRA_BASE + "/raw/published.txt"
    
def update_stop_times():
    if needs_update():
        pass
