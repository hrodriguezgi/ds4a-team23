
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


    def make_accident_point(self, accident):
        accident_tmp = gpd.tools.geocode(
            accident['address'][0],
            Nominatim,
            user_agent='accident_locator')
        accident['geometry'] = accident_tmp['geometry']
        accident['address'] = accident_tmp['address']
        return accident


    def make_agent_point(self, address):
        agent_point = pd.DataFrame([{'address': address}])
        agent_point = gpd.tools.geocode(
            agent_point['address'],
            Nominatim,
            user_agent='agent_locator')
        return agent_point


    def make_buffer(self, accident):
        return accident.to_crs(epsg=7855).buffer(accident['radius'][0]).to_crs(epsg=4326)


    def generate_coordinates(self):
        min_lat, min_lon, max_lat, max_lon = self.bounding_box.split(',')
        rand_lat = round(random.uniform(float(min_lat), float(max_lat)), 7)
        rand_lon = round(random.uniform(float(min_lon), float(max_lon)), 7)
        return rand_lat, rand_lon


    def make_random_agent(self, idx):
        invalid = True
        while invalid:
            latitude, longitude = self.generate_coordinates()
            rev_loc = self.get_reverse_location(latitude, longitude)
            agent_point = self.make_agent_point(rev_loc.address)
            if not agent_point.address.isnull().any():
                invalid = False
        agent_point['agent_idx'] = idx
        return agent_point


    def make_agents(self, quantity):
        agents = pd.DataFrame()
        for i in range(quantity):
            agents = pd.concat([agents, self.make_random_agent(i)], ignore_index=True)
        return agents


    def potential_agents(self, agents, buffer):
        potential_agents = pd.DataFrame()
        for idx in agents.index:
            if buffer.intersects(agents.geometry[idx])[0]:
                potential_agents = pd.concat([potential_agents, agents.iloc[[idx]]], ignore_index=True)
        return(potential_agents)
