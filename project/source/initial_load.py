
"""
Initial load into mysql database


date        author              changelog
2022-06-23  hrodriguezgi        creation
"""
import os

import pandas as pd

from mysql import MySQL

my_cnx = MySQL()

# Agents load
def agents_load():
    path = '../0_datasets/raw/agents'
    for file in os.listdir(path):
        agents = pd.read_csv(os.path.join(path, file))
        my_cnx.insert_sql(agents, 'agents')


def incidents_categories():
    path = '../0_datasets/raw/incidents'
    incidents_categories = pd.read_csv(os.path.join(path, 'incidents_categories.csv'))
    my_cnx.insert_sql(incidents_categories, 'incidents_categories')


def incidents_implicated():
    path = '../0_datasets/raw/incidents'
    incidents_implicated = pd.read_csv(os.path.join(path, 'incidents_implicated.csv'))
    my_cnx.insert_sql(incidents_implicated, 'incidents_implicated')


def main():
    # Agents Load
    agents_load()
    incidents_categories()
    incidents_implicated()


if __name__ == '__main__':
    main()
