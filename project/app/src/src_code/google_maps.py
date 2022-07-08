import requests
import json

import pandas as pd
import geopandas as gpd
from decouple import config


class GoogleMaps:
    def __init__(self) -> None:
        self.key = config('GOOGLE_API_KEY')

    def place(self, place):
        """
        Determines the exact location based on the place passed as parameter.
        """

        # Add Bogota Colombia as a suffix, to try to guarantee only get locations from Bogota
        place = place + ' Bogota Colombia'

        # Create the URL for the endpoint
        url_place = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?" \
                    f"input={place}&" \
                    f"inputtype=textquery&" \
                    f"fields=formatted_address%2Cgeometry&" \
                    f"key={self.key}"

        # Call the endpoint to get the place
        place = requests.get(url=url_place)
        place = json.loads(place.text)

        # Get the possible ordered candidates
        place = pd.json_normalize(place['candidates'])

        # Only return the most relevant place
        return place.iloc[[0]]

    def make_point(self, df_place):
        """
        Generates the exact location of the place passed to the function
        """
        df_place = df_place[['formatted_address', 'geometry.location.lat', 'geometry.location.lng']]
        df_place2 = df_place.rename(columns={'formatted_address': 'address', 'geometry.location.lat': 'latitude',
                                             'geometry.location.lng': 'longitude'})

        # Convert to GeoDataFrame to manage the location in a better way
        df_place2 = gpd.GeoDataFrame(df_place2,
                                     geometry=gpd.points_from_xy(df_place2.longitude, df_place2.latitude),
                                     crs="EPSG:4326")
        return df_place2
