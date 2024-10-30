import json
import math
import itertools
import folium
import streetview
from tqdm import tqdm
import webbrowser

def distance(p1, p2):
    """ Haversine formula: returns distance for latitude and longitude coordinates """
    
    R = 6373
    lat1 = math.radians(p1[0])
    lat2 = math.radians(p2[0])
    lon1 = math.radians(p1[1])
    lon2 = math.radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def get_metadata(center:tuple, radius:float, resolution:int, map_name:str, open_map:bool):
    """Gets the panorama id, latitude, longitude and date of streetview panoramas in a circle around a location."""

    # creates a path name as well
    if map_name.endswith('.html') == False:
        map_name_path = map_name+'.html'
    else:
        map_name_path = map_name


    top_left = (center[0] - radius / 70, center[1] + radius / 70)
    bottom_right = (center[0] + radius / 70, center[1] - radius / 70)
    lat_diff = top_left[0] - bottom_right[0]
    lon_diff = top_left[1] - bottom_right[1]

    # gets test latitudes and longitudes to try to get panoramas from
    test_points = list(itertools.product(range(resolution + 1), range(resolution + 1)))
    test_points = [(bottom_right[0] + x * lat_diff / resolution, bottom_right[1] + y * lon_diff / resolution) for (x, y) in test_points]
    test_points = [p for p in test_points if distance(p, center) <= radius]

    # initializes folium map with the circle in which the panoramas will be found
    M = folium.Map(location=center, tiles='OpenStreetMap', zoom_start=12)
    folium.Circle(location=center, radius=radius * 1000, color='#FF000099', fill=True).add_to(M)

    # gets params of panoramas
    all_panoids = []
    for point in tqdm(test_points):
        try:
            panoid_data = streetview.search_panoramas(point[0], point[1])
            for pano in panoid_data:
                pano_data = {
                    'panoid': pano.pano_id,
                    'lat': pano.lat,
                    'lon': pano.lon,
                    'date': pano.date
                }
                all_panoids.append(pano_data)
        except IndexError:
            continue
    
    # keeps only unique
    unique_panoids = {pano['panoid']: pano for pano in all_panoids}

    # adds found panoramas to the map
    for pan in unique_panoids.values():
        folium.CircleMarker([pan['lat'], pan['lon']], popup=pan['panoid'], radius=1, color='blue', fill=True).add_to(M)

    with open(f'data/scraped/metadata/panoids_{map_name}.json', 'w') as f:
        json.dump(list(unique_panoids.values()), f, indent=2)


    M.save(map_name_path)

    print(f"Map saved to {map_name_path}")

    if open_map:
        webbrowser.open(map_name_path)




if __name__=="__main__":

    # Calls metadata function with example parameters.

    MAP_NAME = 'barcelona_eixample'
    # bamberg: (49.89166413599252, 10.887278258554572)
    CENTER = (41.39186385759671, 2.1650052283024124)
    RADIUS = 1
    RESOLUTION = 50
    OPEN_MAP = True

    get_metadata(center=CENTER, radius=RADIUS, resolution=RESOLUTION, map_name=MAP_NAME, open_map=OPEN_MAP)
