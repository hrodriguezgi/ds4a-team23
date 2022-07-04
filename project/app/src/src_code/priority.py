"""
Priority main

date        author              changelog
2022-07-03  hrodriguezgi        creation
"""

import pandas as pd
import geopandas as gpd
import haversine as hs

from src_code import locator, postgresql, mapquest, google_maps

# Instance the class
l = locator.Locator()
gm = google_maps.GoogleMaps()
psql = postgresql.PostgreSQL()
mq = mapquest.MapQuest()


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


def real_agents(quantity=50):
    query = f'select * from uvw_agents limit {quantity}'
    agents = psql.read_sql(query)
    agents = gpd.GeoDataFrame(agents, geometry=gpd.points_from_xy(
        agents.longitude, agents.latitude))
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
    for idx, agent_idx, localidad, latitude, longitude, geometry in agents.itertuples():
        directions = (mq.route(
            f'{geometry.y},{geometry.x}',
            f'{accident_point.geometry[0].y},{accident_point.geometry[0].x}'))
        time_sec, time, distance = mq.get_route_info(directions)

        agents.loc[idx, 'time'] = time
        agents.loc[idx, 'time_sec'] = time_sec
        agents.loc[idx, 'distance'] = distance

    # Get agent with minimun time
    agents = agents.iloc[[agents['time_sec'].idxmin()]]
    return agents


def measure_distance(accident_point1, accident_point2):
    distance = hs.haversine((accident_point1.geometry[0].y,
                             accident_point1.geometry[0].x),
                            (accident_point2.geometry[0].y,
                             accident_point2.geometry[0].x),
                            unit=hs.Unit.METERS)
    return distance


def far_accidents(accident_point1, accident_point2, agents):
    # Get the nearest agents to each accident point
    nearest_agents1 = search_nearest_agent(accident_point1, agents)
    nearest_agents2 = search_nearest_agent(accident_point2, agents)
    # Find the closest and fastest agent to the accident point
    best_agent1 = find_best_agent(accident_point1, nearest_agents1)
    best_agent2 = find_best_agent(accident_point2, nearest_agents2)

    return nearest_agents1, best_agent1, nearest_agents2, best_agent2


def closer_accidents(accident_point1, priority1, accident_point2, priority2, agents):
    if priority1 == priority2 == 3:
        nearest_agents1 = search_nearest_agent(accident_point1, agents)
        nearest_agents2 = search_nearest_agent(accident_point2, agents)
        # Validate if there are agents in both DFs
        commons = nearest_agents1.merge(
            nearest_agents2, left_on='id', right_on='id', suffixes=['', '_ag1'])
        if commons.empty:
            best_agent1 = find_best_agent(accident_point1, nearest_agents1)
            best_agent2 = find_best_agent(accident_point2, nearest_agents2)
        else:
            nearest_agents1 = nearest_agents1[nearest_agents1.id ==
                                              commons['id'][0]]
            nearest_agents2 = nearest_agents2[nearest_agents2.id ==
                                              commons['id'][0]]
            best_agent1 = find_best_agent(accident_point1, nearest_agents1)
            best_agent2 = find_best_agent(accident_point2, nearest_agents2)

            if best_agent1.time[0] >= best_agent2.time[0]:
                nearest_agents1 = search_nearest_agent(
                    accident_point1, agents[agents['id'] != best_agent2['id'][0]])
                best_agent1 = find_best_agent(accident_point1, nearest_agents1)
            else:
                nearest_agents2 = search_nearest_agent(
                    accident_point2, agents[agents['id'] != best_agent1['id'][0]])
                best_agent2 = find_best_agent(accident_point2, nearest_agents2)
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

        print(f'{accident_point1.address[0]}:\n'
              f'The agent {best_agent1.id[0]} located at '
              f'({best_agent1.latitude[0]}, {best_agent1.longitude[0]}) '
              f'will take {best_agent1.time[0]} in get to the accident.\n')
        print(f'{accident_point2.address[0]}:\n'
              f'The agent {best_agent2.id[0]} located at '
              f'({best_agent2.latitude[0]}, {best_agent2.longitude[0]}) '
              f'will take {best_agent2.time[0]} in get to the accident.')

        return (accident_point1, nearest_agents1, best_agent1, priority1), \
               (accident_point2, nearest_agents2, best_agent2, priority2)

    return None, None, None, None, None, None, None, None


if __name__ == '__main__':
    main('Calle 152 No 12c', 3, 'Calle 140 No 12c', 3)
