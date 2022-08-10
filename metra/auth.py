from .paths import KEYS_PATH
from .constants import METRA_API_KEY
from .constants import METRA_SECRET_KEY

if METRA_API_KEY == "" or METRA_SECRET_KEY == "":
    try:
        with open(KEYS_PATH,'r') as txt:
            lines = txt.readlines()
            METRA_API_KEY = lines[0].strip()
            METRA_SECRET_KEY = lines[1].strip()
    except:
        print('''ERROR: You must provide your own API credentials.\n
              There are two ways of doing this:\n
              1) Populate METRA_API_KEY & METRA_SECRET_KEY constants located 
              in the "constants.py" file\n
              2) Create a file called "keys.txt" in the package's root directory.
              Insert the API Key on the first line and the secret key on the second
              ''')