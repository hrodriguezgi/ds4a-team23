
"""
Accident main


date        author              changelog
2022-06-10  hrodriguezgi        creation
2022-06-30  hrodriguezgi        use of Google Maps API
"""

import pandas as pd
import geopandas as gpd

from src_code import locator, postgresql, mapquest, google_maps

# Instance the class
l = locator.Locator()
gm = google_maps.GoogleMaps()
psql = postgresql.PostgreSQL()
mq = mapquest.MapQuest()

# Flag to identify if we has the agent info
real_agents = False

"""
priority -> 0: false alarm 
                1: minor crash
                2: deads
                3: injuries
"""


def accident(address: str):
    """
    The main method receives:
    address -> Address where accident happened
    """
    # Validate location 
    accident_location = gm.place(address)
    # Generate accident point
    accident_point = gm.make_point(accident_location)
    return accident_point


def dummy_agents(quantity=50):
    """
    Method to create random agents in Bogota
    """
    agents = l.make_agents(quantity)
    return agents


def real_agents(quantity=50):
    query = f'select * from uvw_agents limit {quantity}'
    agents = psql.read_sql(query)
    agents = gpd.GeoDataFrame(agents, geometry=gpd.points_from_xy(agents.longitude, agents.latitude))
    return agents


def search_nearest_agent(accident_point, agents):
    radius = 1000
    nearest_agent = pd.DataFrame()

    while nearest_agent.empty:
        buffer = l.make_buffer(accident_point, radius)
        nearest_agent = l.potential_agents(agents, buffer)
        radius += 1000

    return nearest_agent


def find_best_agent(accident_point, agents):
    agents_directions = {}
    for idx, agent_idx, localidad, latitude, longitude, geometry in agents.itertuples():
        directions = (mq.route(
            f'{geometry.y},{geometry.x}',
            f'{accident_point.geometry[0].y},{accident_point.geometry[0].x}'))
        time_sec, time, distance = mq.get_route_info(directions)

        agents.loc[idx, 'time'] = time
        agents.loc[idx, 'time_sec'] = time_sec
        agents.loc[idx, 'distance'] = distance

        agents_directions[agent_idx] = directions
    # Get agent with minimun time
    agents = agents.iloc[[agents['time_sec'].idxmin()]]
    #steps = mq.get_route_steps(agents_directions[agents['agent_idx'][0]])
    return agents


def main(address, real_agent=False):
    # The address received is searched using Nominatim to get the exact location (geocoding)
    accident_point = accident(address)

    # Only proceed in case the address was properly normalized to an accident point
    if not accident_point.empty:
        if real_agent:
            agents = real_agents()
        else:
            agents = dummy_agents()

        # Get the nearest agents to the accident point
        nearest_agents = search_nearest_agent(accident_point, agents)

        # Find the closest and fastest agent to the accident point
        best_agent = find_best_agent(accident_point, nearest_agents)

        return accident_point, nearest_agents, best_agent

    return None, None, None


if __name__ == '__main__':
    main('parque de la 93', real_agent=True)
