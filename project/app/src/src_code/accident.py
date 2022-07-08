import pandas as pd
import geopandas as gpd

from src_code.locator import Locator
from src_code.postgresql import PostgreSQL
from src_code.mapquest import MapQuest
from src_code.google_maps import GoogleMaps

# Instance the class
locator = Locator()
google_maps = GoogleMaps()
psql = PostgreSQL()
map_quest = MapQuest()


def accident(address: str):
    """
    The main method receives:
    address -> Address where accident happened
    """
    # Validate location 
    accident_location = google_maps.place(address)

    # Generate accident point
    accident_point = google_maps.make_point(accident_location)
    return accident_point


def real_agents(quantity=50):
    query = f'select * from uvw_agents limit {quantity}'
    agents = psql.read_sql(query)
    agents = gpd.GeoDataFrame(agents, geometry=gpd.points_from_xy(agents.longitude, agents.latitude))
    return agents


def search_nearest_agent(accident_point, agents):
    radius = 1000
    nearest_agent = pd.DataFrame()

    while nearest_agent.empty:
        buffer = locator.make_buffer(accident_point, radius)
        nearest_agent = locator.potential_agents(agents, buffer)
        radius += 1000

    return nearest_agent


def find_best_agent(accident_point, agents):
    for idx, agent_idx, localidad, latitude, longitude, geometry in agents.itertuples():
        directions = (map_quest.route(
            f'{geometry.y},{geometry.x}',
            f'{accident_point.geometry[0].y},{accident_point.geometry[0].x}'))
        time_sec, time, distance = map_quest.get_route_info(directions)

        agents.loc[idx, 'time'] = time
        agents.loc[idx, 'time_sec'] = time_sec
        agents.loc[idx, 'distance'] = distance

    # Exclude agents with zero time 
    agents = agents.drop(agents[agents.time_sec < 1].index).reset_index().sort_values(by=['time_sec'])

    # Get agent with minimum time
    agents = agents.iloc[[agents['time_sec'].idxmin()]]
    return agents


def main(address):
    # The address received is searched using Nominatim to get the exact location (geocoding)
    accident_point = accident(address)

    # Only proceed in case the address was properly normalized to an accident point
    if not accident_point.empty:
        agents = real_agents()

        # Get the nearest agents to the accident point
        nearest_agents = search_nearest_agent(accident_point, agents)

        # Find the closest and fastest agent to the accident point
        best_agent = find_best_agent(accident_point, nearest_agents)

        return accident_point, nearest_agents, best_agent

    return None, None, None


if __name__ == '__main__':
    main('parque de la 93')
