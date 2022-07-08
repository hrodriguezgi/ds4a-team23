import requests 
import json

import pandas as pd
from decouple import config


class MapQuest:
    def __init__(self) -> None:
        """
        Loads the key to use the Mapquest API.
        """
        self.key = config('MAPQUEST_KEY')

    def route(self, location1, location2):
        """
        Generates a route between location1 and location2
        location1->Starting Address
        location2->Ending Address
        """
        url_directions = \
            f'http://www.mapquestapi.com/directions/v2/route?key={self.key}&from={location1}&to={location2}'

        directions = requests.get(url=url_directions)
        directions = json.loads(directions.text)

        return directions['route']

    def get_route_info(self, directions):
        """
        Gets information about the route to follow regarding the first direction
        directions->list of directions (but usually brings 1)
        """
        directions = pd.DataFrame([directions])
        time_sec = directions['time'][0]
        time = directions['formattedTime'][0]
        distance = directions['distance'][0]
        return time_sec, time, distance

    def get_route_steps(self, directions):
        """
        Gets the amount of steps in the directions
        directions->list of directions (but usually brings 1)
        """
        directions = pd.DataFrame([directions])
        steps = pd.DataFrame(pd.DataFrame(directions['legs'].iloc[0]).iloc[0]['maneuvers'])
        steps = steps[['distance', 'streets', 'formattedTime', 'narrative']]
        return steps
