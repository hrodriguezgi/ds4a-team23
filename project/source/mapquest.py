
"""
mapquest api


date        author              changelog
2022-06-10  hrodriguezgi        creation
"""

import requests 
import json

import pandas as pd


class MapQuest():
    def __init__(self) -> None:
        self.key = 'PHKj4K2YezeVChykh0blAAAZRapB6OpO'


    def route(self, location1, location2):
        url_directions = f'http://www.mapquestapi.com/directions/v2/route?key={self.key}&from={location1}&to={location2}'
        directions = requests.get(url=url_directions)
        directions_json = json.loads(directions.text)
        directions = pd.DataFrame(directions_json)
        return directions


    def get_route_info(self, directions):
        time = directions.loc['formattedTime']['route']
        distance = directions.loc['distance']['route']
        return time, distance


    def get_route_steps(self, directions):
        steps = pd.DataFrame(pd.DataFrame(directions.loc['legs']['route']).iloc[0]['maneuvers'])
        steps = steps[['distance', 'streets', 'formattedTime', 'narrative']]
        return steps
