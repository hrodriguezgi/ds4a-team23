
"""
google maps api


date        author              changelog
2022-06-30  hrodriguezgi        creation
2022-07-03  hrodriguezgi        new df to return in make_point method
"""

import requests
import json

import pandas as pd
import geopandas as gpd
from decouple import config


class GoogleMaps:
    def __init__(self) -> None:
        self.key = config('GOOGLE_API_KEY')

    def place(self, place):
        place = place + ' Bogota Colombia'
        url_place = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={place}&inputtype=textquery&fields=formatted_address%2Cgeometry&key={self.key}"

        place = requests.get(url=url_place)
        place = json.loads(place.text)
        place = pd.json_normalize(place['candidates'])
        return place.iloc[[0]]


    def make_point(self, df_place):
        df_place = df_place[['formatted_address', 'geometry.location.lat', 'geometry.location.lng']]
        df_place2 = df_place.rename(columns={'formatted_address':'address', 'geometry.location.lat':'latitude', 'geometry.location.lng':'longitude'})
        df_place2 = gpd.GeoDataFrame(df_place2,
                                    geometry=gpd.points_from_xy(df_place2.longitude, df_place2.latitude),
                                    crs="EPSG:4326")
        return df_place2
