import requests
import datetime as dt
from dateutil.parser import parse

from .paths import *

def needs_update() -> bool:
    last_updated: dt.datetime
    with open(f"{DATA_PATH}/last_update.txt","r") as txtfile:
        last_updated = parse(txtfile.read())
    if dt.datetime.now() < last_updated:
        return True
    else:
        return False
