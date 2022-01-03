METRA_BASE = "https://gtfsapi.metrarail.com/gtfs"
METRA_API_KEY = "2fbb8926df23765437c88363a228d70a"
METRA_SECRET_KEY = "aa81976c54adda9c316e9bb34cdcba31"

SCHEDULES_BASE = "https://metrarail.com/maps-schedules"

ROUTE_NAMES = {
    "Burlington Northern":"BNSF",
    # "Burlington Northern Santa Fe":"bnsf",
    "Heritage Corridor":"HC",
    "Milwaukee District North":"MD-N",
    "Milwaukee District West":"MD-W",
    "Metra Electric":"ME",
    "North Central Services":"NCS",
    "Rock Island":"RI",
    "SouthWest Service":"SWS",
    "Union Pacific North":"UP-N",
    "Union Pacific Northwest":"UP-NW",
    "Union Pacific West":"UP-W"}

ROUTES_SHORTHAND = {
    "bnsf":"BNSF",
    "hc":"HC",
    "mdn":"MD-N",
    "md-n":"MD-N",
    "mdw":"MD-W",
    "md-w":"MD-W",
    "me":"ME",
    "ncs":"NCS",
    "ri":"RI",
    "sws":"SWS",
    "upn":"UP-N",
    "up-n":"UP-N",
    "upnw":"UP-NW",
    "up-nw":"UP-NW",
    "upw":"UP-W",
    "up-w":"UP-W"}

POSITION_COLS = [
                'trip_id',
                'route_id',
                # 'vehicle_id',
                'vehicle_label',
                'lat',
                'lon',
                'dir_id',
                'stop_seq',
                'status',
                'stop_id',
                'start_time',
                'start_date',
                'low']

TRIP_UPDATE_COLS = [
                "trip_start",
                # "ts_update",
                # "ts_vehicle",
                "trip_id",
                "route_id",
                "dir_id",
                # "vehicle_id",
                "vehicle_label",
                "lat",
                "lon",
                "status",
                "stop_sequence",
                "stop_id",
                "arrDly",
                "arr",
                # "depDly",
                "eta"]

ZONES = {
    "Geneva": "H",
    "West Chicago": "F",
    "Winfield": "F",
    "Wheaton": "E",
    "College Ave": "E",
    "Glen Ellyn": "E",
    "Lombard": "D",
    "Villa Park": "D",
    "Elmhurst": "D",
    "Berkeley": "C",
    "Bellwood": "C",
    "Melrose Park": "C",
    "Maywood": "C",
    "River Forest": "B",
    "Oak Park": "B",
    "Kedzie": "A",
    "Aurora": "H",
    "Route 59": "G",
    "Naperville": "F",
    "Lisle": "E",
    "Belmont": "E",
    "Downers Grove": "E",
    "Fairview Ave.": "E",
    "Westmont": "D",
    "Clarendon Hills": "D",
    "West Hinsdale": "D",
    "Hinsdale": "D",
    "Highlands": "D",
    "Western Springs": "D",
    "Stone Ave.": "C",
    "LaGrange Road": "C",
    "Congress Park": "C",
    "Brookfield": "C",
    "Hollywood": "C",
    "Riverside": "C",
    "Harlem Ave.": "B",
    "Berwyn": "B",
    "Lavergne": "B",
    "Cicero": "B",
    "Western Avenue": "A",
    "Halsted Street": "A",
    "Joliet": "H",
    "Lockport": "G",
    "Lemont": "E",
    "Willow Springs": "D",
    "Summit": "C",
    "Orland Park 179th": "F",
    "Orland Park 153rd": "E",
    "Orland Park 143rd": "E",
    "Palos Park": "E",
    "Worth": "D",
    "Chicago Ridge": "D",
    "Oak Lawn Patriot": "D",
    "Ashburn": "C",
    "Wrightwood": "C",
    "Clybourn": "A",
    "Ravenswood": "B",
    "Rogers Park": "B",
    "Main St.": "C",
    "Evanston (Davis St.)": "C",
    "Central St.": "C",
    "Wilmette": "C",
    "Kenilworth": "D",
    "Winnetka": "D",
    "Hubbard Woods": "D",
    "Glencoe": "D",
    "Braeside": "E",
    "Ravinia": "E",
    "Highland Park": "E",
    "Highwood": "E",
    "Fort Sheridan": "F",
    "Lake Forest.": "F",
    "Lake Bluff": "G",
    "Great Lakes": "G",
    "North Chicago": "G",
    "Waukegan": "H",
    "Zion": "I",
    "Winthrop Harbor": "I",
    "Fox Lake": "J",
    "Ingleside": "J",
    "Long Lake": "J",
    "Round Lake": "I",
    "Grayslake": "I",
    "Libertyville": "H",
    "Lake Forest": "F",
    "Deerfield": "E",
    "Lake-Cook": "E",
    "Northbrook": "E",
    "Glen/N. Glenview": "D",
    "Glenview": "D",
    "Golf": "D",
    "Morton Grove": "C",
    "Edgebrook": "C",
    "Forest Glen": "C",
    "Mayfair": "B",
    "Grayland": "B",
    "Healy": "B",
    "Western Ave": "A",
    "Ravinia Park": "E",
    "Indian Hill": "D",
    "Kenosha": "J",
    "Harvard": "J",
    "Woodstock": "J",
    "Crystal Lake": "I",
    "McHenry": "J",
    "Cary": "H",
    "Fox River Grove": "H",
    "Barrington": "G",
    "Palatine": "F",
    "Arlington Park": "E",
    "Arlington Heights": "E",
    "Mt. Prospect": "D",
    "Cumberland": "D",
    "Des Plaines": "D",
    "Dee Road": "C",
    "Park Ridge": "C",
    "Irving Park": "B",
    "Big Timber": "H",
    "Elgin": "H",
    "National St": "H",
    "Hanover Park": "F",
    "Schaumburg": "F",
    "Roselle": "E",
    "Medinah": "E",
    "Itasca": "E",
    "Wood Dale": "D",
    "Bensenville": "D",
    "Mannheim": "C",
    "Franklin Park": "C",
    "Mont Clare": "B",
    "Mars": "B",
    "Galewood": "B",
    "Hanson Park": "B",
    "Grand/Cicero": "B",
    "O'Hare Transfer": "D",
    "Prospect Hts": "E",
    "Wheeling": "F",
    "Buffalo Grove": "F",
    "Prairie View": "G",
    "Vernon Hills": "G",
    "Mundelein": "H",
    "Prairie Crossing.": "H",
    "Round Lake Beach": "J",
    "Lake Villa": "J",
    "Antioch": "J",
    "New Lenox": "G",
    "Mokena": "F",
    "Hickory Creek": "F",
    "Tinley-80th": "E",
    "Tinley Park": "E",
    "Oak Forest": "E",
    "Midlothian": "D",
    "Robbins": "D",
    "Kensington": "C",
    "59th St. (U. of Chicago)": "B",
    "University Park": "G",
    "Richton Park": "F",
    "Matteson": "F",
    "211th St.": "F",
    "Olympia Fields": "F",
    "Flossmoor": "E",
    "Homewood": "E",
    "Calumet": "E",
    "Edison Park": "C",
    "Norwood Park": "C",
    "Gladstone Park": "B",
    "Jefferson Park": "B",
    "Bartlett": "F",
    "47th St. (Kenwood)": "B",
    "51st/53rd St. (Hyde Park)": "B",
    "55th - 56th - 57th St.": "B",
    "63rd St.": "B",
    "Prairie Crossing": "H",
    "River Grove": "C",
    "Elmwood Park": "C",
    "Riverdale": "D",
    "Ivanhoe": "D",
    "147th St.": "D",
    "Harvey": "D",
    "Hazel Crest": "E",
    "Millennium Station": "A",
    "Van Buren St.": "A",
    "Museum Campus/11th St.": "A",
    "18th St.": "A",
    "McCormick Place": "A",
    "27th St.": "A",
    "75th St. (Grand Crossing)": "B",
    "79th St. (Chatham)": "B",
    "83rd St. (Avalon Park)": "B",
    "87th St. (Woodruff)": "B",
    "91st St.": "C",
    "95th St.": "C",
    "103rd St. (Rosemoor)": "C",
    "107th St.": "C",
    "111th St. (Pullman)": "C",
    "Stony Island": "B",
    "Bryn Mawr": "B",
    "South Shore": "B",
    "Windsor Park": "B",
    "Cheltenham (79th St.)": "B",
    "83rd St.": "B",
    "87th St.": "B",
    "South Chicago (93rd)": "B",
    "LaSalle Street": "A",
    "Gresham": "B",
    "Blue Island-Vermont": "D",
    "95th St.-Longwood": "C",
    "103rd St.-Washington Hts.": "C",
    "Brainerd": "C",
    "91st St. - Beverly Hills": "C",
    "Prairie St.": "D",
    "123rd St.": "C",
    "119th St.": "C",
    "115th St. - Morgan Park": "C",
    "111th St. - Morgan Park": "C",
    "107th St. - Beverly Hills": "C",
    "103rd St. - Beverly Hills": "C",
    "99th St. - Beverly Hills": "C",
    "95th St. - Beverly Hills": "C",
    "Blue Island": "D",
    "Burr Oak": "D",
    "Ashland": "C",
    "Racine": "C",
    "West Pullman": "C",
    "Stewart Ridge": "C",
    "State St.": "C",
    "Schiller Park": "C",
    "Palos Heights": "D",
    "Pingree Road": "I",
    "Chicago Union Station": "A",
    "Chicago OTC": "A",
    "Laraway Road": "H",
    "Manhattan": "I",
    "Washington St (Grayslake)": "I",
    "Rosemont": "D",
    "Franklin Pk": "C",
    "La Fox": "I",
    "Elburn": "I",
    "35th St. - Lou Jones": "A",
    "Romeoville": "F"}


