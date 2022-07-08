"""
Priority main

date        author              changelog
2022-07-03  hrodriguezgi        creation
2022-07-05  hrodriguezgi        removed agents with zero time
"""

import pandas as pd
import geopandas as gpd
import haversine as hs

from src_code.google_maps import GoogleMaps
from src_code.locator import Locator
from src_code.postgresql import PostgreSQL
from src_code.mapquest import MapQuest

# Instance the classes
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


def real_agents(quantity=100):
    """
    This method is used to query the agents that are available to attend
    an incident.
    quantity -> Defines the maximum amount of agents to return.
    """
    # Definition of the query
    query = f'select * from uvw_agents order by 1 limit {quantity}'

    # Execute the specified query
    agents = psql.read_sql(query)

    # Loads query's result into a Geopandas Dataframe
    agents = gpd.GeoDataFrame(agents, geometry=gpd.points_from_xy(
        agents.longitude, agents.latitude))
    return agents


def search_nearest_agent(accident_point, agents):
    """
    This method searches for the nearest agent, from a list, to a certain accident_point.
    accident_point -> Coordinates of the accident
    agents -> list of agents available to help
    """
    # Search radius from the accident point
    radius = 1000

    # Definition of the dataframe which will contain the information from nearest agent to the accident point
    nearest_agent = pd.DataFrame()

    # This cycle searches for agents that are ready to attend an emegerncy.
    # In each iteration, if it doesn't find any agent, then expands the radius.
    while nearest_agent.empty:
        buffer = locator.make_buffer(accident_point, radius)
        nearest_agent = locator.potential_agents(agents, buffer)
        radius += 1000

    # Returns information for the nearest agent to the accident point
    return nearest_agent


def find_best_agent(accident_point, agents):
    """
    Searches for the best agent to attend an accident, from a given list.
    accident_point -> Coordinates of the accident
    agents -> list of agents available to help
    """
    # Extracts some fields from the agents and uses them to evaluate the time and distance that will take
    # an agent to reach the accident point
    for idx, agent_idx, localidad, latitude, longitude, geometry in agents.itertuples():
        # Generates the routes that an agent must follow to reach as soon as possible the accident point
        directions = (map_quest.route(
            f'{geometry.y},{geometry.x}',
            f'{accident_point.geometry[0].y},{accident_point.geometry[0].x}'))
        time_sec, time, distance = map_quest.get_route_info(directions)

        # Here the calculated parameters are saved in a column to said agent
        agents.loc[idx, 'time'] = time
        agents.loc[idx, 'time_sec'] = time_sec
        agents.loc[idx, 'distance'] = distance

    # Exclude agents with zero time 
    agents = agents \
        .drop(agents[agents.time_sec < 1].index) \
        .reset_index(drop=True) \
        .sort_values(by=['time_sec']) \
        .reset_index(drop=True)

    # Get agent with minimum time
    best_agent = agents.iloc[[agents['time_sec'].idxmin()]]
    return best_agent, agents


def measure_distance(accident_point1, accident_point2):
    """
    Calculates the distance between two accidents
    accident_point1->coordinates of accident #1
    accident_point2->coordinates of accident #2
    """
    # Extracts the components (x,y) of each accident and computes them to get the distance between them
    distance = hs.haversine((accident_point1.geometry[0].y,
                             accident_point1.geometry[0].x),
                            (accident_point2.geometry[0].y,
                             accident_point2.geometry[0].x),
                            unit=hs.Unit.METERS)
    return distance


def far_accidents(accident_point1, accident_point2, agents):
    """
    Search the best agents for the accidents points
    accident_point1->accident point #1
    accident_point2->accident point #2
    agents->list filled with agents information
    """
    # Get the nearest agents to each accident point
    nearest_agents1 = search_nearest_agent(accident_point1, agents)
    nearest_agents2 = search_nearest_agent(accident_point2, agents)

    # Find the closest and fastest agent to the accident point
    best_agent1, nearest_agents1 = find_best_agent(accident_point1, nearest_agents1)
    best_agent2, nearest_agents2 = find_best_agent(accident_point2, nearest_agents2)

    return nearest_agents1, best_agent1, nearest_agents2, best_agent2


def closer_accidents(accident_point1, priority1, accident_point2, priority2, agents):
    """
    Calculates the best agent that can attend the emergency #1 and #2, and also calculates the nearest agent to
    the accident.

    accident_point1->accident point #1
    priority1->priority of accident #1
    accident_point2->accident point #2
    priority2->priority of accident #2
    agents->list filled with agents information
    """
    # If both accidents have the same priority, and it's 3
    if priority1 == priority2 == 3:
        nearest_agents1 = search_nearest_agent(accident_point1, agents)
        best_agent1, nearest_agents1 = find_best_agent(accident_point1, nearest_agents1)

        nearest_agents2 = search_nearest_agent(accident_point2, agents)
        best_agent2, nearest_agents2 = find_best_agent(accident_point2, nearest_agents2)

        # Validate if there are agents in both DFs
        if best_agent1.id.iloc[0] == best_agent2.id.iloc[0]:

            # If Agent is nearest to the accident 2:
            if best_agent1.time_sec.iloc[0] > best_agent2.time_sec.iloc[0]:

                # If the nearest_agents1 DF has more agents take the second one
                best_agent1 = nearest_agents1.iloc[[1]]
            else:

                # If the nearest_agents2 DF has more agents take the second one
                best_agent2 = nearest_agents2.iloc[[1]]

    # Highest priority for accident1
    elif priority1 == 3:
        # Get the best agent to the priority accident
        nearest_agents1 = search_nearest_agent(accident_point1, agents)
        best_agent1 = find_best_agent(accident_point1, nearest_agents1)

        # Get the best agent to the other accident excluding the previous agent
        nearest_agents2 = search_nearest_agent(
            accident_point2, agents[agents['id'] != best_agent1['id'][0]])
        best_agent2 = find_best_agent(accident_point2, nearest_agents2)

    # Highest priority for accident2
    elif priority2 == 3:
        # Get the best agent to the priority accident
        nearest_agents2 = search_nearest_agent(accident_point2, agents)
        best_agent2 = find_best_agent(accident_point2, nearest_agents2)

        # Get the best agent to the other accident excluding the previous agent
        nearest_agents1 = search_nearest_agent(
            accident_point1, agents[agents['id'] != best_agent2['id'][0]])
        best_agent1 = find_best_agent(accident_point1, nearest_agents1)

    # Any other scenario
    else:
        nearest_agents1 = search_nearest_agent(accident_point1, agents)
        best_agent1 = find_best_agent(accident_point1, nearest_agents1)

        nearest_agents2 = search_nearest_agent(
            accident_point2, agents[agents['id'] != best_agent1['id'][0]])
        best_agent2 = find_best_agent(accident_point2, nearest_agents2)

    return nearest_agents1, best_agent1, nearest_agents2, best_agent2


def main(address1, priority1, address2, priority2):
    """
    Initialices the script, trying to find the best attention (regarding the nearest and best agent for said adress).
    address1->Adress of the first accident.
    priority1->Priority of the first accident.
    address2->Adress of the first accident.
    priority2->Priority of the first accident.
    """
    # The addresses received are searched using Google Maps API
    accident_point1 = accident(address1)
    accident_point2 = accident(address2)

    # Load the agents location
    agents = real_agents()

    # Only proceed in case the address was properly normalized to an accident point
    if not accident_point1.empty and not accident_point2.empty:
        distance = measure_distance(accident_point1, accident_point2)

        # Determine if the accidents are near to each other (<1.5km or <1500m)
        # Accidents are too far
        if distance > 1500:
            nearest_agents1, best_agent1, nearest_agents2, best_agent2 = far_accidents(
                accident_point1, accident_point2, agents)

        # Accidents are closer
        else:
            nearest_agents1, best_agent1, nearest_agents2, best_agent2 = closer_accidents(
                accident_point1, priority1, accident_point2, priority2, agents)

        print(f'{accident_point1.address.iloc[0]}:\n'
              f'The agent {best_agent1.id.iloc[0]} located at '
              f'({best_agent1.latitude.iloc[0]}, {best_agent1.longitude.iloc[0]}) '
              f'will take {best_agent1.time.iloc[0]} to get to the accident.\n')

        print(f'{accident_point2.address.iloc[0]}:\n'
              f'The agent {best_agent2.id.iloc[0]} located at '
              f'({best_agent2.latitude.iloc[0]}, {best_agent2.longitude.iloc[0]}) '
              f'will take {best_agent2.time.iloc[0]} to get to the accident.')

        return (accident_point1, nearest_agents1, best_agent1, priority1), \
               (accident_point2, nearest_agents2, best_agent2, priority2)

    return (None, None, None, None), (None, None, None, None)


if __name__ == '__main__':
    main('unicentro', 3, 'country', 3)
