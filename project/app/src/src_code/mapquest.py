
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
        directions = json.loads(directions.text)
        return directions['route']


    def get_route_info(self, directions):
        directions = pd.DataFrame([directions])
        time_sec = directions['time'][0]
        time = directions['formattedTime'][0]
        distance = directions['distance'][0]
        return time_sec, time, distance


    def get_route_steps(self, directions):
        directions = pd.DataFrame([directions])
        steps = pd.DataFrame(pd.DataFrame(directions['legs'].iloc[0]).iloc[0]['maneuvers'])
        steps = steps[['distance', 'streets', 'formattedTime', 'narrative']]
        return steps
