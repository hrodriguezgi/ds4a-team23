
"""
locator class


date        author              changelog
2022-06-10  hrodriguezgi        creation
"""

from geopy.geocoders import Nominatim
import geopandas as gpd
import pandas as pd
import random

class Locator:
    def __init__(self) -> None:
        self.bounding_box = '4.433731,-74.214899,4.839060,-74.005499'


    def get_location(self, address):
        geocoder = Nominatim(user_agent='accident_locator')
        location = geocoder.geocode(address)
        return location


    def get_reverse_location(self, latitude, longitude):
        geocoder = Nominatim(user_agent='agent_locator')
        location = geocoder.reverse(f'{latitude}, {longitude}')
        return location


    def make_point(self, address):
        accident_point = pd.DataFrame([{'address': address}])
        accident_point = gpd.tools.geocode(
            accident_point['address'],
            Nominatim,
            user_agent='accident_locator')
        return accident_point


    def make_buffer(self, accident_point, radius):
        buffer = accident_point.to_crs(epsg=7855).buffer(radius).to_crs(epsg=4326)
        return buffer


    def make_random_agent(self):
        min_lat, min_lon, max_lat, max_lon = self.bounding_box.split(',')
        rand_lat = round(random.uniform(float(min_lat), float(max_lat)), 7)
        rand_lon = round(random.uniform(float(min_lon), float(max_lon)), 7)
        rev_loc = self.get_reverse_location(rand_lat, rand_lon)
        return self.make_point(rev_loc.address)
