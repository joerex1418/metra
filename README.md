# metra
[Package Dependencies](#package-dependencies) | [Setup](#setup) | [Getting Started](#getting-started) | [Example Usage](#example-usage)

Unofficial Python wrapper for interacting with the Metra GTFS API

## Package Dependencies
This repository relies heavily on [Pandas](https://pandas.pydata.org/docs/). Aside from that, it is recommended that you use Python 3.8+ since the following modules from the standard library are utilized as well:
- [io](https://docs.python.org/3/library/io.html)
- [zipfile](https://docs.python.org/3/library/zipfile.html)
- [requests](https://requests.readthedocs.io/en/latest/)

<i>**Things to note:**
- API credentials are required. Obtain your personal API Key and Secret Key by filling out the form at the [Metra Developer Home Page](https://metra.com/developers)
- This library depends on the use of static data that Metra updates once a day. When the `StaticAPI` class is initiated, it will check to make ensure the data on your local drive is up to date. Data is stored in a ~20 KB zip file within the packaged directory</i>

## Setup
### 1. Download the repository
```bash
# clone the repo with git
git clone https://github.com/joerex1418/metra.git
```
### 2. Setup your API Credentials
The Metra GTFS API Feed utilizes basic authentication for accessing the data. Once you have your API credentials, create a `keys.txt` file in the library's root directory (where the `__init__.py` file is located).

On the first line in your `keys.txt` file, type in your assigned **API Key**. On the second line, put in your assigned **Secret Key**

<i>`keys.txt` Format</i>
```
<YOUR_API_KEY_HERE>
<YOUR_SECRET_KEY_HERE>
```
Save this file and you should be all set.

## Getting Started
```python
import metra

s = metra.StaticAPI()
```
## Example Usage
```python
# Stops Dataframe
>>> df = s.stops()
>>> df.head()
        stop_id             stop_name   stop_lat   stop_lon zone_id  wheelchair_boarding
0        GENEVA                Geneva  41.881667 -88.310000       H                    1
1      WCHICAGO          West Chicago  41.881111 -88.198889       F                    1
2      WINFIELD              Winfield  41.870000 -88.156944       F                    1
3       WHEATON               Wheaton  41.864444 -88.111944       E                    1
4    COLLEGEAVE           College Ave  41.868333 -88.090278       E                    1

# Next Train Departures (leaving the Naperville station, going to Chicago Union Station)
>>> df = s.next_trains("NAPERVILLE","CUS")
>>> df[["trip_id","arrival_time","stop_id"]].head()

            trip_id        arrival_time     stop_id
0  BNSF_BN1260_V2_B 2022-08-13 13:15:00  NAPERVILLE
1  BNSF_BN1262_V2_B 2022-08-13 14:15:00  NAPERVILLE
2  BNSF_BN2018_V2_B 2022-08-13 14:33:00  NAPERVILLE
3  BNSF_BN1264_V2_B 2022-08-13 15:15:00  NAPERVILLE
4  BNSF_BN2020_V2_B 2022-08-13 15:35:00  NAPERVILLE

# Search for stop entries from the "stops" dataset
>>> s.stop_search(query="clybourn")
     stop_id stop_name   stop_lat   stop_lon zone_id  wheelchair_boarding
55  CLYBOURN  Clybourn  41.916944 -87.668056       A                    0
```
