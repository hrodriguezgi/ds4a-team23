import pandas as pd
import geopandas as gpd
import plotly.express as px

from math import radians
from sklearn.cluster import DBSCAN
import statsmodels.formula.api as sm


class Insights:

    def __init__(self, language='EN'):
        """
        Constructor of the class Insights.
        It loads the info of the datasets and then makes it available to further analysis in the insights
        public methods. For example, the data is loaded into claims, and then used in biggest_accidents_per_type.
        language->Defines the language that will be used in the insights and maps.
        """

        # Initialize variables
        self.language = None
        self.incidents = None
        self.incidents_implicated = None
        self.claims = None
        self.tmp_claims = None
        self.translation_dictionary = dict()

        # Loads and process the datasets
        self._load_datasets()
        self._init_datasets()
        self._process_datasets()

        # Loads the figures needed to plot the choropleth maps
        self._load_polygons()

        # Sets the language used in the insights and maps
        self.change_language(language)

    def change_language(self, language):
        """
        Defines the language that will be used in the insights and maps, and load the associated dictionary that
        contains the translation data.
        language->Defines the language that will be used in the insights and maps.
        """
        self.language = language
        self._load_translation_dictionary()

    def _load_translation_dictionary(self):
        """
        If the language is EN, then proceeds to load the Spanish-English dictionary.
        """
        if self.language == "EN":
            # Loads the EN dictionary into the current translation dictionary
            self.translation_dictionary["EN"] = {}

            # This is to extract the lines in the file en_data.txt; which contains the translation for every word
            with open('assets/en_data.txt') as f:

                # Saves every word from the file into the dictionary, using a split by '='
                for word in [line.rstrip().split("=") for line in f]:
                    self.translation_dictionary["EN"][word[0]] = word[1]

    def _apply_translation(self, word):
        """
        Searches for the word in the current translation dictionary, if it isn't spanish, then locates the word, else
        returns the same word (because the datasets are in spanish by default).
        """
        if self.language != "ES":
            # If the word is in the dictionary, translates it, else, returns the word as it arrived.
            return self.translation_dictionary["EN"][word] if word in self.translation_dictionary["EN"] else word
        else:
            return word

    def _load_datasets(self):
        """
        Loads the data from the processed zips and saves it into de dataframes
        """
        # Do not delete, useful for local tests
        self.incidents = pd.read_csv("assets/incidents.csv.gz", parse_dates=["incident_time"])
        self.incidents_implicated = pd.read_csv("assets/incidents_implicated.csv.gz")

        # Parse the incident_time to datetime type
        self.incidents["incident_time"] = pd.to_datetime(self.incidents["incident_time"])

    def _init_datasets(self):
        """
        Joins the datasets into a dataframe called claims, which will be used in all the insights.
        """
        # Extracts only the incidents which are of class 'Siniestro' (which means claims in English)
        self.claims = self.incidents[self.incidents["class"] == "Siniestro"]

        # Merges the incidents and incidents_implicated dataframe to create de claims dataset,
        # then drops the columns id and id_x and sort the data by the time of the incident
        self.claims = self.claims.merge(
            self.incidents_implicated,
            how="left",
            left_on="id",
            right_on="incident_id"
        ).drop(columns=["id_y", "incident_id"]) \
            .rename(columns={"id_x": "id"}) \
            .drop_duplicates(subset="id") \
            .sort_values("incident_time")

    def _load_polygons(self):
        # Loads the information about the polygons
        self.pol = gpd.read_file("assets/poligonos_bog.geojson")

    def _process_datasets(self):
        # Create new fields to process the claims dataframe
        self.claims["incident_day"] = self.claims.loc[:, "incident_time"].dt.to_period("d").dt.to_timestamp()
        self.claims["hour"] = self.claims["incident_time"].dt.hour
        self.claims["month"] = self.claims["incident_time"].dt.month

    def biggest_accidents_per_type(self):
        """
        First Insight: The amount of accidents per type
        """

        # Extracts the total amount of claims per type
        data = self.claims["type"].value_counts()

        # Splits a series to apply a translation to the type of incident
        x, y = [self._apply_translation(x) for x in data.index], [val for val in data]

        # Creates a new series using the x and y components from the old series
        data = pd.Series(y, index=x)

        # Generates the insight for this method, using the data generated before
        insight_results = [
            "The incident type with the most amount of cases is " + str(data.index[0]) + " with a total of " + str(
                data[0])]

        # Creates the bar plot for the front
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

        # Generates the insight for this method, using the data generated before
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
        data_death["tipo"], data_death["total"] = "Deaths", data_death["dead_count"]
        data = data_death
        del data["dead_count"]
        data.reset_index(inplace=True)
        data = data[(data["index"] > 0)]

        # Generates the insight for this method, using the data generated before
        insight_results = [str(data["total"].sum()) + " people died because of the accidents"]

        # Creates the bar plot for the front
        graphic = px.bar(data, x="index", y="total", color="tipo", title="Deaths per accident",
                         labels={'index': '# of deaths', 'total': 'Value', 'tipo': 'Category'})
        return data, graphic, insight_results

    def injuries_per_accident(self):
        """
        4. Amount of injuries per accident
        """
        data_heridos = self.claims["injured_count"].value_counts().to_frame()
        data_heridos["tipo"], data_heridos["total"] = "Injuries", data_heridos["injured_count"]
        data = data_heridos
        del data["injured_count"]
        data.reset_index(inplace=True)
        data = data[(data["index"] > 0)]

        # Generates the insight for this method, using the data generated before
        insight_results = [str(data["total"].sum()) + " people got injuries as result of the accidents"]

        # Creates the bar plot for the front
        graphic = px.bar(data, x="index", y="total", color="tipo", title="Injuries per accident",
                         labels={'index': '# of injuries', 'total': 'Value', 'tipo': 'Category'})

        return data, graphic, insight_results

    def accidents_per_vehicle_type(self):
        """
        5. Amount of accidents per vehicle type
        """
        data = self.claims["implicated_type"].value_counts()
        x, y = [self._apply_translation(x) for x in data.index], [val for val in data]
        data = pd.Series(y, index=x)

        # Generates the insight for this method, using the data generated before
        insight_results = [
            "The type of vehicle with the most amount of accidents is " + str(data.index[0]) +
            ", followed by " + str(data.index[1]) + " and " + str(data.index[2]) +
            ", with a total amount of " + str(data.values[0]) + ", " + str(data.values[1]) +
            " and " + str(data.values[2]) + " cases respectively."]

        # Creates the bar plot for the front
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
        data["type"] = [self._apply_translation(x) for x in data["type"]]
        for location in data["localidad"].value_counts().index:
            data_final = pd.concat([data_final, data[data["localidad"] == location].iloc[[0]]])
        data_final["localidad"] = [x.capitalize() for x in data_final["localidad"]]
        pol_copy = self.pol
        pol_copy["localidad"] = [x.capitalize() for x in pol_copy["localidad"]]

        data_chlo = pol_copy.merge(data_final, how="left", on="localidad").set_index("localidad")

        data_final = data_final.rename(columns={"localidad": "Location", "total_accidentes": "Total Accidents"})
        data_chlo = data_chlo.rename(columns={"localidad": "Location", "total_accidentes": "Total Accidents"})

        graphic = px.choropleth_mapbox(data_chlo,
                                       geojson=data_chlo.geometry,
                                       locations=data_chlo.index,
                                       color="Total Accidents",
                                       center={'lat': 4.601981275958889, 'lon': -74.0767720598354},
                                       mapbox_style="open-street-map",
                                       hover_data=["type"],
                                       color_continuous_scale=["green", "red"],
                                       zoom=10,
                                       title="Accidents per locality"
                                       )
        # Generates the insight for this method, using the data generated before
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
        data["localidad"] = [x.capitalize() for x in data["localidad"]]
        pol_copy["localidad"] = [x.capitalize() for x in pol_copy["localidad"]]

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

        # Generates the insight for this method, using the data generated before
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

        # Generates the insight for this method, using the data generated before
        insight_results = ["The most frequent priority for accidents is " + str(data.index[0]) + ", followed by " + str(
            data.index[1]) + ", with an amount of " + str(data.values[0]) + " and " + str(
            data.values[1]) + " cases each."]

        # Creates the bar plot for the front
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
        data.rename(columns={hour: "Amount"}, inplace=True)
        data.sort_values(by="Amount", ascending=False, inplace=True)

        hour_in_text = ("0" + str(hour) if hour < 10 else str(hour)) + ":00"

        data["type"] = [self._apply_translation(x) for x in data["type"]]

        # Generates the insight for this method, using the data generated before
        insight_results = [
            "At " + hour_in_text + " hours, the most frequent accidents are " + str(data.iloc[0][0]) + " and " + str(
                data.iloc[1][0]) + ", with a total amount of " + str(data.iloc[0][1]) + " and " + str(
                data.iloc[1][1]) + " cases."]

        # Creates the bar plot for the front
        graphic = px.bar(data, x=data["type"], y=data["Amount"],
                         labels={'type': 'Accident type'},
                         title="Accident distribution at " + hour_in_text + " hours")

        return data, graphic, insight_results

    def sinisters_per_day(self):
        data = self.claims["incident_day"].value_counts().sort_index(ascending=False).reset_index().rename(
            columns={"index": "Fecha", "incident_day": "Numero de siniestros"})

        fig = px.line(data, x="Fecha", y="Numero de siniestros")

        return data, fig, []

    def cluster_points_dbscan(self, data):
        """
        Code section used for implement the map's clusters

        Receives the distance 'eps' in meters in which it is considered as a neighbour of another,
        and the minimum number of samples which create a cluster. Returns the dataframe with two news
        columns: 'cluster' and 'cluster_size'.
        """
        eps = 50
        min_samples = 3

        locs = data.loc[:, ["latitude", "longitude"]].apply(lambda x: x.map(radians), axis=1)  # lat y long a radians

        # fit dbscan clustering
        dbc = DBSCAN(
            eps=eps / 6371000,
            min_samples=min_samples,
            metric="haversine",
            n_jobs=-1
        ).fit(locs)

        data["cluster"] = dbc.labels_.astype(pd.Categorical)  # cluster labels
        cluster_sizes = data["cluster"].value_counts()
        data["cluster_size"] = data["cluster"].map(cluster_sizes)

        return data

    def _load_clusters_db(self):
        self.tmp_claims = pd.read_csv("assets/siniestros.csv.gz", parse_dates=["incident_time"])

    def draw_incidents_map(self):
        if self.tmp_claims is None:
            self._load_clusters_db()

        fig = px.scatter_mapbox(
            self.tmp_claims.sort_values("hour"),
            lat='latitude',
            lon='longitude',
            zoom=10,
            animation_frame="hour",
            mapbox_style='open-street-map',
            hover_name="incident_time",
            hover_data=['type', 'gravity', 'class'],
        )

        return self.tmp_claims, fig, []

    def draw_incidents_clusters_map(self):
        if self.tmp_claims is None:
            self._load_clusters_db()

        fig = px.scatter_mapbox(
            (self.tmp_claims.loc[self.tmp_claims["cluster"] != -1, :]).sort_values("hour"),
            lat='latitude',
            lon='longitude',
            opacity=0.7,
            size='cluster_size',
            zoom=10,
            animation_frame="hour",
            mapbox_style='open-street-map',
            hover_name="incident_time",
            hover_data=['class', 'type', 'gravity'],
        )

        return self.tmp_claims, fig, []

    def _train_model(self, nom_localidad):
        print(nom_localidad)

    def _create_linear_regression_model(self, localidad):
        subdf = self.claims[self.claims["location"] == localidad]
        subdf = subdf[subdf["month"] < 12]
        data = subdf["month"].value_counts().sort_index(ascending=True).to_frame().reset_index().rename(
            columns={'index': 'month', 'month': 'accidents_amount'})
        print(data)

        formula = 'accidents_amount ~ month'
        linear_model = sm.ols(formula=formula, data=data)
        linear_model_fit = linear_model.fit()
        print(linear_model_fit.summary())


"""
Insights
1. biggest_accidents_per_type()
2. biggest_accidents_per_location()
3. deaths_per_accident()
4. injuries_per_accident()
5. accidents_per_vehicle_type()
6. accidents_per_location()
7. accidents_per_zone_and_hour(hour);  (int)hour:0,1,2,...,23
8. accidents_per_priority()
9. accidents_per_hour(hour);  (int)hour:0,1,2,...,23

Cluster maps
10. draw_incidents_map()
11. draw_incidents_clusters_map()
"""

if __name__ == '__main__':
    insights = Insights("EN")

    data, fig, insights = insights.draw_incidents_clusters_map()
    fig.show()
