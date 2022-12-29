import os
import requests

API_KEY = os.environ.get("MAPQUEST_API_KEY")

def get_map_url(address, city, state):
    """Get MapQuest URL for a static map for this location."""

    base = f"https://www.mapquestapi.com/staticmap/v5/map?key={API_KEY}"
    where = f"{address},{city},{state}"
    return f"{base}&center={where}&defaultMarker=marker-red-sm&size=250,200@2x&zoom=15&locations={where}"


def save_map(id, address, city, state):
    """Get static map and save in static/maps directory of this app."""

    path = os.path.abspath(os.path.dirname(__file__))
    file_name = f"{id}.jpg"

    # get URL for map, download it, and save it with a path
    # like "PATH/static/maps/1.jpg"
    map_url = get_map_url(address, city, state)
    resp = requests.get(map_url, stream=True)

    if resp.ok:
        with open(os.path.join(path+"/static/images/maps/", file_name), 'wb') as fp:
            fp.write(resp.content)
    else:
        print("Download not allowed")

    return resp.url

# this works too
#import urllib.request
#urllib.request.urlretrieve(url, filename)
