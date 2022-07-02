import pandas as pd
import geopandas as gpd
import plotly.express as px
from sklearn.cluster import DBSCAN 
from math import radians
import postgresql

class Insights:

    def __init__(self):
        self.incidents = None
        self.incidents_implicated = None
        self.sinisters = None
        self.gdf = None
        self.psql = postgresql.PostgreSQL()
        
        self._loadDatasets()
        self._initDatasets()
        self._processDatasets()
        self._loadPolygons()

    def _loadDatasets(self):
        #self.incidents = pd.read_csv("../../../0_datasets/processed/incidents.csv.gz", parse_dates=["incident_time"])
        #self.incidents_implicated = pd.read_csv("../../../0_datasets/processed/incidents_implicated.csv.gz")
        self.incidents = self.psql.read_sql("select * from incidents_processed")
        self.incidents["incident_time"] = pd.to_datetime(self.incidents["incident_time"])
        self.incidents_implicated = self.psql.read_sql("select * from incidents_implicated_processed")
        
    def _initDatasets(self):
        self.sinisters = self.incidents[self.incidents["class"] == "Siniestro"]        
        self.sinisters= self.sinisters.merge(self.incidents_implicated,
                                            how="left", left_on="id",
                                            right_on="incident_id").drop(columns=["id_y", "incident_id"])\
                                                                   .rename(columns={"id_x":"id"})\
                                                                   .drop_duplicates(subset="id")\
                                                                   .sort_values("incident_time")
    def _loadPolygons(self):
        self.pol = gpd.read_file("../../../0_datasets/processed/poligonos_bog.geojson")
        
    
    def _processDatasets(self):
        self.sinisters["incident_day"] = self.sinisters.loc[:, "incident_time"].dt.to_period("d").dt.to_timestamp()
        self.sinisters["hour"] = self.sinisters["incident_time"].dt.hour
                
    def biggest_accidents_per_type(self):
        """
        1. The amount of accidents per type
        """
        data = self.sinisters["type"].value_counts()    
        insights = []

        insights.append("The incident type with the most amount of cases is "+str(data.index[0])+" with a total of "+str(data[0]))        
        graphic = px.bar(data, x=data.index, y=data, title="Biggest incident types",labels={'index':'Incident type','y':'Value'})
        return data, graphic, insights
    
    def biggest_accidents_per_location(self): 
        """
        2. The amount of accidents per location
        """
        data = self.sinisters["location"].value_counts().reset_index().rename(columns={"index":"localidad", "location": "num_sinisters"}).drop(19)
        pol_copy = self.pol
        data_chlo = pol_copy.merge(data,how="left", on="localidad").set_index("localidad")

        graphic = px.choropleth_mapbox(data_chlo,
                                geojson=data_chlo.geometry,
                                locations=data_chlo.index,
                                color="num_sinisters",
                                    center={'lat': 4.601981275958889, 'lon': -74.0767720598354},
                                mapbox_style="open-street-map",
                                color_continuous_scale=["green","red"],
                                zoom=10,
                                height=800
                                )

        insights=[]    
        insights.append("The location with more accidents is "+str(data.iloc[0][0])+" with a total amount of "+str(data.iloc[0][1])+" cases, followed by "+str(data.iloc[1][0])+" and "+str(data.iloc[2][0])+" with "+str(data.iloc[1][1])+" and "+str(data.iloc[2][1])+" cases respectively")            
        return data, graphic, insights

    def deaths_per_accident(self):
        """
        3. Amount of deaths per accident
        """
        data_death = self.sinisters["dead_count"].value_counts().to_frame()
        data_death["tipo"],data_death["total"] = "Muertos",data_death["dead_count"]
        data = data_death
        del data["dead_count"]
        data.reset_index(inplace=True)    
        data = data[(data["index"] > 0)]
        insights=[]
        insights.append(str(data["total"].sum())+" people died because of the accidents")    
        graphic = px.bar(data, x="index", y="total", color="tipo", title="Deaths per accident",labels={'index':'# of deaths','total':'Value','tipo':'Category'})    
        return data, graphic, insights
    
    def injuries_per_accident(self):
        """
        4. Amount of injuries per accident
        """
        data_heridos = self.sinisters["injured_count"].value_counts().to_frame()
        data_heridos["tipo"],data_heridos["total"] = "Heridos",data_heridos["injured_count"]
        data = data_heridos
        del data["injured_count"]
        data.reset_index(inplace=True)    
        data = data[(data["index"] > 0)]
        insights=[]
        insights.append(str(data["total"].sum())+" people got injuries as result of the accidents")    
        graphic = px.bar(data, x="index", y="total", color="tipo", title="Injuries per accident",labels={'index':'# of injuries','total':'Value','tipo':'Category'})    

        return data, graphic, insights
    
    def accidents_per_vehicle_type(self):
        """
        5. Amount of accidents per vehicle type
        """
        data = self.sinisters["implicated_type"].value_counts()
        insights=[]    
        insights.append("The type of vehicle with the most amount of accidents is "+str(data.index[0])+", followed by "+str(data.index[1])+" and "+str(data.index[2])+", with a total amount of "+str(data.values[0])+", "+str(data.values[1])+" and "+str(data.values[2])+" cases respectively.")
        graphic = px.bar(data, x=data.index, y=data,labels={'index':'Type of vehicle','y':'Amount'}, title="Accidents per vehicle type")

        return data, graphic, insights
    
    def accidents_per_location(self):    
        """
        6. Amount of accidents per location    
        """
        data = self.sinisters[["type","location"]].value_counts().reset_index().rename(columns={"index":"localidad", "location": "localidad","0":"total"})    
        data = data[data["localidad"] != "LOCATION MISSING"]
        data["total_accidentes"]=data[0]
        del data[0]

        data_final = pd.DataFrame(columns = ["localidad"])
        data.sort_values(by=['total_accidentes'],ascending=False,inplace=True)
        for location in data["localidad"].value_counts().index:        
            data_final = pd.concat([data_final,data[data["localidad"] == location].iloc[[0]]])

        pol_copy = self.pol
        data_chlo = pol_copy.merge(data_final,how="left", on="localidad").set_index("localidad")

        hover = [x for x in data_chlo["type"].value_counts().index]

        graphic = px.choropleth_mapbox(data_chlo,
                                geojson=data_chlo.geometry,
                                locations=data_chlo.index,
                                color="total_accidentes",
                                    center={'lat': 4.601981275958889, 'lon': -74.0767720598354},
                                mapbox_style="open-street-map",
                                hover_data=["type"],
                                color_continuous_scale=["green","red"],
                                zoom=10,
                                height=800
                                )
        insights=[]    
        insights.append("The location with more accidents is "+str(data_final.iloc[0][0])+" with a total amount of "+str(data_final.iloc[0][2])+" cases of type "+str(data_final.iloc[0][1])+", followed by "+str(data_final.iloc[1][0])+" with "+str(data_final.iloc[1][2])+" cases of type "+str(data_final.iloc[1][1]))    
        insights.append("The location with less accidents is "+str(data_final.iloc[-1][0])+" with a total amount of "+str(data_final.iloc[-1][2])+" cases of type "+str(data_final.iloc[-1][1]))    
        return data_final, graphic, insights
    
    def accidents_per_zone_and_hour(self,hour):  
        """
        7. Amount of accidents per zone and hour       
        """
        data = self.sinisters[["location","hour"]].value_counts().reset_index().rename(columns={"index":"localidad", "location": "localidad","0":"total"})    
        data = data[data["localidad"] != "LOCATION MISSING"]
        data["total_accidentes"]=data[0]
        data = data[data["hour"] == hour]
        data.reset_index(inplace=True)
        del data[0],data["hour"],data["index"]

        pol_copy = self.pol
        data_chlo = pol_copy.merge(data,how="left", on="localidad").set_index("localidad")

        graphic = px.choropleth_mapbox(data_chlo,
                                geojson=data_chlo.geometry,
                                locations=data_chlo.index,
                                color="total_accidentes",
                                    center={'lat': 4.601981275958889, 'lon': -74.0767720598354},
                                mapbox_style="open-street-map",   
                                color_continuous_scale=["green","red"],                         
                                zoom=10,
                                height=800
                                )
        insights=[]    
        insights.append("The location with more accidents at * is "+str(data.iloc[0][0])+" with a total amount of "+str(data.iloc[0][1])+" cases")    
        insights.append("The location with less accidents at * is "+str(data.iloc[-1][0])+" with a total amount of "+str(data.iloc[-1][1])+" cases")    
        return data, graphic, insights
    
    def accidents_per_priority(self):
        """
        8. Accidents per priority type
        """
        data = self.sinisters["priority"].value_counts()
        insights=[]   
        insights.append( "The most frequent priority for accidents is "+str(data.index[0])+", followed by "+str(data.index[1])+", with an amount of "+str(data.values[0])+" and "+str(data.values[1])+" cases each.")
        graphic = px.bar(data, x=data.index, y=data,labels={'index':'Priority','y':'Amount'}, title="Accidents per priority")

        return data, graphic, insights
    
    def accidents_per_hour(self,hour):
        """
        9. Accidents per hour
        """
        data = self.sinisters[["hour","type"]].value_counts().sort_values().sort_index(kind='mergesort')
        data = data.unstack(level=0).reset_index()[["type",hour]].fillna(0)    
        data = pd.merge(data["type"], data[hour], right_index = True,left_index = True)
        data.rename(columns={hora: "Cantidad"},inplace=True)
        data.sort_values(by="Cantidad",ascending=False,inplace=True)

        hourInText = ("0"+str(hora) if hora < 10 else str(hora))+":00"
        insights=[]

        insights.append("At "+hourInText+" hours, the most frequent accidents are "+str(data.iloc[0][0])+" and "+str(data.iloc[1][0])+", with a total amout of "+str(data.iloc[0][1])+" and "+str(data.iloc[1][1])+" cases.")
        graphic = px.bar(data, x=data["type"], y=data["Cantidad"],labels={'type':'Accident type','Cantidad':'Amount'}, title="Accident distribution at "+hourInText+" hours")

        return data, graphic, insights
        

insights = Insights()

"""
1. biggest_accidents_per_type()
2. biggest_accidents_per_location()
3. deaths_per_accident()
4. injuries_per_accident()
5. accidents_per_vehicle_type()
6. accidents_per_location()
7. accidents_per_zone_and_hour(hour);  (int)hour:0,1,2,...,23
8. accidents_per_priority()
9. accidents_per_hour(hour);  (int)hour:0,1,2,...,23
"""