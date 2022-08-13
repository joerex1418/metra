import io
import zipfile
import requests
import datetime as dt
from requests.auth import HTTPBasicAuth

from .paths import DATA_PATH
from .constants import METRA_BASE
from .auth import METRA_API_KEY, METRA_SECRET_KEY

AUTH = HTTPBasicAuth(METRA_API_KEY,METRA_SECRET_KEY)
PUBLISHED_FMT = r'%m/%d/%Y %I:%M:%S %p'
CALENDAR_FMT = r'%Y%m%d'

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
            datetime = txtfile.read()
            datetime = dt.datetime.strptime(datetime,PUBLISHED_FMT)
            # if dt.datetime.combine(datetime.date(),time=dt.time(3,0,0)) > dt.datetime.now():
            if datetime.date() < dt.datetime.today().date():
                datetime = get_publish_time()
            return datetime
    except:
        return get_publish_time()
    
def update_schedule_zip():
    url = METRA_BASE + "/raw/schedule.zip"
    resp = requests.get(url,auth=AUTH)
    updated_zip = zipfile.ZipFile(io.BytesIO(resp.content),'r')
    new_zip = zipfile.ZipFile(f'{DATA_PATH}/schedule.zip','w')
    
    for f in ['stop_times','stops','calendar','calendar_dates','routes','shapes','trips','fare_rules','fare_attributes']:
        fbytes = updated_zip.read(f'{f}.txt')
        new_zip.writestr(f'{f}.txt',fbytes,zipfile.ZIP_DEFLATED)
    updated_zip.close()
    new_zip.close()
        
def get_schedule_zip() -> zipfile.ZipFile:
    try:
        with open(f'{DATA_PATH}/schedule.zip','rb') as fp:
            bytes_io = io.BytesIO(fp.read())
            return zipfile.ZipFile(bytes_io, mode='r')

    except:
        update_schedule_zip()
        with open(f'{DATA_PATH}/schedule.zip','rb') as fp:
            bytes_io = io.BytesIO(fp.read())
            return zipfile.ZipFile(bytes_io, mode='r')
