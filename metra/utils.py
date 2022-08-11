import pickle
import requests
import datetime as dt
from requests.auth import HTTPBasicAuth
from dateutil.parser import parse

from .paths import DATA_PATH
from .constants import METRA_BASE
from .auth import METRA_API_KEY, METRA_SECRET_KEY

AUTH = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)
PUBLISHED_FMT = r'%m/%d/%Y %I:%M:%S %p'

def get_publish_time() -> dt.datetime:
    url = METRA_BASE + "/raw/published.txt"
    resp = requests.get(url,auth=AUTH)
    time = resp.text
    with open(f'{DATA_PATH}/last_published.txt','w+') as txtfile:
        txtfile.write(time)
    return dt.datetime.strptime(time,PUBLISHED_FMT)

def get_last_local_publish() -> dt.datetime:
    try:
        with open(f'{DATA_PATH}/last_published.txt','r+') as txtfile:
            time = txtfile.read()
            return dt.datetime.strptime(time,PUBLISHED_FMT)
    except:
        return get_publish_time()
    