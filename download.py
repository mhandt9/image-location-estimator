import os
import json
import time
import streetview
from tqdm import tqdm
from dotenv import load_dotenv
from geopy.geocoders import GoogleV3

def download_panoramas(metadata_path:str, api_key:str, city_name:str, naming:str=['lat_long', 'address', 'lat-long_adress']):
    
    with open(metadata_path, 'r') as f:
        meta_data = json.load(f)

    print(f"Running this will download \033[31m{len(meta_data)}\033[0m panoramas. Be aware of your \033[31musage of the Google Geocoding API and Street View Static API\033[0m.")
    decision = input('Do you wish to continue? (\033[32mY\033[0m/\033[31mN\033[0m) ')

    if (decision == "Y") or (decision == "y"):
        print("Continuing with download.")

        if naming != 'lat_long':
            geolocator = GoogleV3(api_key=api_key)


        for pano in tqdm(meta_data, desc="Progress downloading panoramas"):
            
            time.sleep(.2)

            img = streetview.get_streetview(pano_id=pano['panoid'], api_key=api_key)

            # img.show()

            if naming == 'lat_long':

                img.save("data/scraped/panoramas/"+str(pano['lat'])+'_'+str(pano['lon'])+".png")

            elif naming == 'address':

                location = geolocator.reverse((pano['lat'], pano['lon']))

                img.save("data/scraped/panoramas/"+str(location).replace(',', '').replace(' ', '_')+".png")

            elif naming == 'lat-long_address':
                
                location = geolocator.reverse((pano['lat'], pano['lon']))

                img.save("data/scraped/panoramas/"+str(pano['lat'])+"-"+str(pano['lon'])+"_"+str(location).split(',')[0].replace(' ', '_')+"_"+city_name+".png")

    else:
        print("Download stopped.")


if __name__=="__main__":

    load_dotenv()

    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    METADATA_PATH = 'data/scraped/metadata/panoids_barcelona_eixample.json'

    NAMING = 'lat-long_address'

    CITY_NAME = 'barcelona'

    download_panoramas(metadata_path=METADATA_PATH, api_key=GOOGLE_MAPS_API_KEY, city_name=CITY_NAME, naming=NAMING)