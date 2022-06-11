import alphashape
from descartes import PolygonPatch
import folium
import geopandas as gpd
from geopy.geocoders import Nominatim
from ipywidgets import interact, fixed, widgets
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import osmnx as ox
import pandas as pd
from shapely import geometry

address = 'Parque el virrey, Bogotá'
geocoder = Nominatim(user_agent='Isochrone calculator')
location = geocoder.geocode(address)
location