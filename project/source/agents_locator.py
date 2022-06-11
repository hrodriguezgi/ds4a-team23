from geopy.geocoders import Nominatim
import geopandas as gpd
import pandas as pd


class Locator:
    def __init__(self) -> None:
        pass


    def get_location(self, address):
        address = address
        geocoder = Nominatim(user_agent='accident_locator')
        location = geocoder.geocode(address)
        return location


    def make_accident_point(self, address):
        accident_point = pd.DataFrame([{'address': address}])
        accident_point = gpd.tools.geocode(
            accident_point['address'],
            Nominatim,
            user_agent='accident_locator')
        return accident_point


    def make_buffer(self, accident_point, radius):
        buffer = accident_point.to_crs(epsg=7855).buffer(radius).to_crs(epsg=4326)
        return buffer
