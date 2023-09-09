# metra
[Package Dependencies](#package-dependencies) | [Setup](#setup) | [Getting Started](#getting-started) | [Example Usage](#example-usage)

A Python wrapper for interacting with the Metra Transit Static & RealTime Feeds

## Package Dependencies
It is recommended that you use Python 3.8+. Outside the standard library, the following third-party libraries are used in certain cases:
- [rich](https://github.com/Textualize/rich)
- [tabulate](https://github.com/astanin/python-tabulate)

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

static = metra.StaticAPI()
```
## Example Usage
```python
# Stops Data
>>> 

# Next Train Departures 
# (Ex: From Naperville to Chicago Union Station)
>>> data = static.next_trains("NAPERVILLE","CUS")
```
