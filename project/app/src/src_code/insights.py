import pandas as pd
import geopandas as gpd
import plotly.express as px
from src_code import postgresql


class Insights:
    def __init__(self):
        self.incidents = None
        self.incidents_implicated = None
        self.claims = None

        self._load_datasets()
        self._init_datasets()
        self._process_datasets()
        self._load_polygons()

    def _load_datasets(self):
        # Do not delete, useful for local tests
        # self.incidents = pd.read_csv("assets/incidents.csv.gz", parse_dates=["incident_time"])
        # self.incidents_implicated = pd.read_csv("assets/incidents_implicated.csv.gz")

        psql = postgresql.PostgreSQL()

        self.incidents = psql.read_sql("select * from incidents_processed")
        self.incidents["incident_time"] = pd.to_datetime(self.incidents["incident_time"])
        self.incidents_implicated = psql.read_sql("select * from incidents_implicated_processed")

    def _init_datasets(self):
        self.claims = self.incidents[self.incidents["class"] == "Siniestro"]
        self.claims = self.claims.merge(
            self.incidents_implicated,
            how="left",
            left_on="id",
            right_on="incident_id"
        ).drop(columns=["id_y", "incident_id"])\
            .rename(columns={"id_x": "id"})\
            .drop_duplicates(subset="id") \
            .sort_values("incident_time")

    def _load_polygons(self):
        self.pol = gpd.read_file("assets/poligonos_bog.geojson")

    def _process_datasets(self):
        self.claims["incident_day"] = self.claims.loc[:, "incident_time"].dt.to_period("d").dt.to_timestamp()
        self.claims["hour"] = self.claims["incident_time"].dt.hour

    def biggest_accidents_per_type(self):
        """
        1. The amount of accidents per type
        """
        data = self.claims["type"].value_counts()
        insight_results = [
            "The incident type with the most amount of cases is " + str(data.index[0]) + " with a total of " + str(
                data[0])]

        graphic = px.bar(data, x=data.index, y=data, title="Biggest incident types",
                         labels={'index': 'Incident type', 'y': 'Value'})
        return data, graphic, insight_results

    def biggest_accidents_per_location(self):
        """
        2. The amount of accidents per location
        """
        data = self.claims["location"].value_counts().reset_index().rename(
            columns={"index": "localidad", "location": "num_claims"}).drop(19)
        pol_copy = self.pol
        data_chlo = pol_copy.merge(data, how="left", on="localidad").set_index("localidad")

        graphic = px.choropleth_mapbox(data_chlo,
                                       geojson=data_chlo.geometry,
                                       locations=data_chlo.index,
                                       color="num_claims",
                                       center={'lat': 4.601981275958889, 'lon': -74.0767720598354},
                                       mapbox_style="open-street-map",
                                       color_continuous_scale=["green", "red"],
                                       zoom=10,
                                       title="Accidents per locality"
                                       )

        insight_results = [
            "The location with more accidents is " + str(data.iloc[0][0]) + " with a total amount of " + str(
                data.iloc[0][1]) + " cases, followed by " + str(data.iloc[1][0]) + " and " + str(
                data.iloc[2][0]) + " with " + str(data.iloc[1][1]) + " and " + str(
                data.iloc[2][1]) + " cases respectively"]
        return data, graphic, insight_results

    def deaths_per_accident(self):
        """
        3. Amount of deaths per accident
        """
        data_death = self.claims["dead_count"].value_counts().to_frame()
        data_death["tipo"], data_death["total"] = "Muertos", data_death["dead_count"]
        data = data_death
        del data["dead_count"]
        data.reset_index(inplace=True)
        data = data[(data["index"] > 0)]
        insight_results = [str(data["total"].sum()) + " people died because of the accidents"]
        graphic = px.bar(data, x="index", y="total", color="tipo", title="Deaths per accident",
                         labels={'index': '# of deaths', 'total': 'Value', 'tipo': 'Category'})
        return data, graphic, insight_results

    def injuries_per_accident(self):
        """
        4. Amount of injuries per accident
        """
        data_heridos = self.claims["injured_count"].value_counts().to_frame()
        data_heridos["tipo"], data_heridos["total"] = "Heridos", data_heridos["injured_count"]
        data = data_heridos
        del data["injured_count"]
        data.reset_index(inplace=True)
        data = data[(data["index"] > 0)]
        insight_results = [str(data["total"].sum()) + " people got injuries as result of the accidents"]
        graphic = px.bar(data, x="index", y="total", color="tipo", title="Injuries per accident",
                         labels={'index': '# of injuries', 'total': 'Value', 'tipo': 'Category'})

        return data, graphic, insight_results

    def accidents_per_vehicle_type(self):
        """
        5. Amount of accidents per vehicle type
        """
        data = self.claims["implicated_type"].value_counts()
        insight_results = [
            "The type of vehicle with the most amount of accidents is " + str(data.index[0]) + ", followed by " + str(
                data.index[1]) + " and " + str(data.index[2]) + ", with a total amount of " + str(
                data.values[0]) + ", " + str(data.values[1]) + " and " + str(data.values[2]) + " cases respectively."]
        graphic = px.bar(data, x=data.index, y=data, labels={'index': 'Type of vehicle', 'y': 'Amount'},
                         title="Accidents per vehicle type")

        return data, graphic, insight_results

    def accidents_per_location(self):
        """
        6. Amount of accidents per location    
        """
        data = self.claims[["type", "location"]].value_counts().reset_index().rename(
            columns={"index": "localidad", "location": "localidad", "0": "total"})
        data = data[data["localidad"] != "LOCATION MISSING"]
        data["total_accidentes"] = data[0]
        del data[0]

        data_final = pd.DataFrame(columns=["localidad"])
        data.sort_values(by=['total_accidentes'], ascending=False, inplace=True)
        for location in data["localidad"].value_counts().index:
            data_final = pd.concat([data_final, data[data["localidad"] == location].iloc[[0]]])

        pol_copy = self.pol
        data_chlo = pol_copy.merge(data_final, how="left", on="localidad").set_index("localidad")

        graphic = px.choropleth_mapbox(data_chlo,
                                       geojson=data_chlo.geometry,
                                       locations=data_chlo.index,
                                       color="total_accidentes",
                                       center={'lat': 4.601981275958889, 'lon': -74.0767720598354},
                                       mapbox_style="open-street-map",
                                       hover_data=["type"],
                                       color_continuous_scale=["green", "red"],
                                       zoom=10,
                                       title="Accidents per locality"
                                       )
        insight_results = [
            "The location with more accidents is " + str(data_final.iloc[0][0]) + " with a total amount of " + str(
                data_final.iloc[0][2]) + " cases of type " + str(data_final.iloc[0][1]) + ", followed by " + str(
                data_final.iloc[1][0]) + " with " + str(data_final.iloc[1][2]) + " cases of type " + str(
                data_final.iloc[1][1]),
            "The location with less accidents is " + str(data_final.iloc[-1][0]) + " with a total amount of " + str(
                data_final.iloc[-1][2]) + " cases of type " + str(data_final.iloc[-1][1])]
        return data_final, graphic, insight_results

    def accidents_per_zone_and_hour(self, hour):
        """
        7. Amount of accidents per zone and hour       
        """
        data = self.claims[["location", "hour"]].value_counts().reset_index().rename(
            columns={"index": "localidad", "location": "localidad", "0": "total"})
        data = data[data["localidad"] != "LOCATION MISSING"]
        data["total_accidentes"] = data[0]
        data = data[data["hour"] == hour]
        data.reset_index(inplace=True)
        del data[0], data["hour"], data["index"]

        pol_copy = self.pol
        data_chlo = pol_copy.merge(data, how="left", on="localidad").set_index("localidad")

        graphic = px.choropleth_mapbox(data_chlo,
                                       geojson=data_chlo.geometry,
                                       locations=data_chlo.index,
                                       color="total_accidentes",
                                       center={'lat': 4.601981275958889, 'lon': -74.0767720598354},
                                       mapbox_style="open-street-map",
                                       color_continuous_scale=["green", "red"],
                                       zoom=10,
                                       title="Accidents per zone and hour"
                                       )

        hour_in_text = ("0" + str(hour) if hour < 10 else str(hour)) + ":00"

        insight_results = [
            f"The location with more accidents at {hour_in_text} is " + str(data.iloc[0][0])
            + " with a total amount of " + str(data.iloc[0][1]) + " cases",
            f"The location with less accidents at {hour_in_text} is " + str(data.iloc[-1][0])
            + " with a total amount of " + str(data.iloc[-1][1]) + " cases"]
        return data, graphic, insight_results

    def accidents_per_priority(self):
        """
        8. Accidents per priority type
        """
        data = self.claims["priority"].value_counts()
        insight_results = ["The most frequent priority for accidents is " + str(data.index[0]) + ", followed by " + str(
            data.index[1]) + ", with an amount of " + str(data.values[0]) + " and " + str(
            data.values[1]) + " cases each."]
        graphic = px.bar(data, x=data.index, y=data, labels={'index': 'Priority', 'y': 'Amount'},
                         title="Accidents per priority")

        return data, graphic, insight_results

    def accidents_per_hour(self, hour):
        """
        9. Accidents per hour
        """
        data = self.claims[["hour", "type"]].value_counts().sort_values().sort_index(kind='mergesort')
        data = data.unstack(level=0).reset_index()[["type", hour]].fillna(0)
        data = pd.merge(data["type"], data[hour], right_index=True, left_index=True)
        data.rename(columns={hour: "Cantidad"}, inplace=True)
        data.sort_values(by="Cantidad", ascending=False, inplace=True)

        hour_in_text = ("0" + str(hour) if hour < 10 else str(hour)) + ":00"

        insight_results = [
            "At " + hour_in_text + " hours, the most frequent accidents are " + str(data.iloc[0][0]) + " and " + str(
                data.iloc[1][0]) + ", with a total amount of " + str(data.iloc[0][1]) + " and " + str(
                data.iloc[1][1]) + " cases."]

        graphic = px.bar(data, x=data["type"], y=data["Cantidad"],
                         labels={'type': 'Accident type', 'Cantidad': 'Amount'},
                         title="Accident distribution at " + hour_in_text + " hours")

        return data, graphic, insight_results


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

if __name__ == '__main__':
    insights = Insights()

    _, fig, _ = insights.biggest_accidents_per_type()
    fig.show()

