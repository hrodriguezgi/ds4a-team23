import pandas as pd
import locator

# Instance the class
l = locator.Locator()

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
    accident_location = l.get_location(address + ', Bogotá Colombia')
    # Generate accident point
    if accident_location:
        accident_point = l.make_accident_point(accident_location)
    return accident_point


def dummy_agents(quantity=50):
    """
    Method to create random agents in Bogota
    """
    agents = l.make_agents(quantity)
    return agents


def search_nearest_agent(accident_point, agents):
    radius = 1000
    nearest_agent = pd.DataFrame()

    while nearest_agent.empty:
        buffer = l.make_buffer(accident_point, radius)
        nearest_agent = l.potential_agents(agents, buffer)
        radius += 1000

    return nearest_agent


def main(address):
    # The address received is searched using Nominatin
    accident_point = accident(address)

    if real_agents:
        # agents = real_agents info
        pass
    else:
        agents = dummy_agents()

    # Get the nearest agents
    nearest_agents = search_nearest_agent(accident_point, agents)
    print(nearest_agents)


if __name__ == '__main__':
    main('Parque de la 93')