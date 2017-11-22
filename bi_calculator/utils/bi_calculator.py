"""
Belonging index calculator

This class have all the methods required to calculate the belonging index
from a distance matrix or from a profile file.

It also has the methods to create the visualization of results.

Inherits from DistanceCalculator class

"""

# Import packages

import pandas as pd
import plotly as py
import plotly.graph_objs as go
from plotly.graph_objs import *
import numpy as np
from utils.distance_calculator import DistanceCalculator



class BiCalculator(DistanceCalculator):

    def __init__(self):
        self.class_df_data = []
        self.matrix_df_data = []
        self.current_vector = []
        self.classification_counts = []
        self.bis_class = {"bis": {}, "class": {}}
        self.bi_series = []
        self.bi_means_by_class = {}

    # Loads the distance matrix file into a pandas dataframe
    def load_matrix_file(self, distance_matrix_path):
        df_data = pd.read_csv(distance_matrix_path, sep="\t")
        df_data.set_index('ID', inplace=True)
        self.matrix_df_data = df_data

        return df_data

    # Loads the classification file into a pandas dataframe
    def load_classification_file(self, classification_path):
        df_data = pd.read_csv(classification_path, sep="\t")
        df_data.columns = ["ID", "Classification"]
        df_data.set_index('ID', inplace=True)
        self.class_df_data = df_data

        return df_data

    # Get one row of the distance matrix according to the given index
    def get_distance_vector(self, id):
        self.current_vector = self.matrix_df_data.loc[id]

    # Sort a pandas Series in an ascending way
    def sort_vector(self):
        return self.current_vector.sort_values(ascending=True)

    # Counts the number of isolates that have a given classifier
    def count_n_classifier(self):
        self.classification_counts = self.class_df_data["Classification"]\
            .value_counts()

    # Get the column names of a pandas dataframe
    def get_headers(self):
        self.headers = self.matrix_df_data.columns.values

    @staticmethod
    def object_to_series(ob):
        return pd.Series(ob)

    # Calculates the Bi directly from the distance matrix
    def calculate_bi_from_matrix(self, id):
        self.get_distance_vector(id)
        sorted_vector = self.sort_vector()
        count_same_class = 0
        count_diff_class = 0
        count_passed = 0
        class_of_query = self.class_df_data.loc[id]["Classification"]
        n_on_class = self.classification_counts[class_of_query] - 1 or 1

        for index, value in sorted_vector.iteritems():
            class_of_sub = self.class_df_data.loc[index]["Classification"]

            if index != id:
                if class_of_sub == class_of_query:
                    count_same_class += 1
                else:
                    count_diff_class += 1

                count_passed += 1

            if count_passed == n_on_class:
                break

        bi = float(count_same_class) / float(n_on_class)

        self.bis_class["bis"][id] = bi
        self.bis_class["class"][id] = class_of_query

    # Calculates the Belonging Index from the profiles file
    # Uses fast-mlst results to compute the closest ones
    def calculate_bi_from_profiles(self, p_name, f_mlst_rs):
        class_of_query = self.class_df_data.loc[p_name]["Classification"]
        n_on_class = self.classification_counts[class_of_query] - 1 or 1
        count_passed = 0
        count_same_class = 0
        count_diff_class = 0

        for entry in f_mlst_rs:
            id1 = entry.split("\t")[0]
            if id1 == "FILE":
                continue
            class_of_sub = self.class_df_data.loc[id1]["Classification"]

            #if id1 != p_name:
            if class_of_sub == class_of_query:
                count_same_class += 1
            else:
                count_diff_class += 1

            count_passed += 1

            if count_passed == n_on_class:
                break

        # 0 if only the query is on the results for the closest profiles
        # or all the results have a different classification
        bi = float(count_same_class) / float(n_on_class)

        self.bis_class["bis"][p_name] = bi
        self.bis_class["class"][p_name] = class_of_query

    # Calculates the average Belonging index by classification
    def average_bi_per_class(self):
        object_of_class = {}

        for index, value in self.bis_class["bis"].items():
            cls = self.bis_class["class"][index]
            if cls not in object_of_class:
                object_of_class[cls] = []
            object_of_class[cls].append(value)

        for index, value in object_of_class.items():
            self.bi_means_by_class[index] = np.mean(object_of_class[index])

    # Defines the Histogram plot to be visualized
    def trace_bi_histogram(self, ob):
        pd_series = self.object_to_series(ob)
        data = go.Histogram(
            x=pd_series,
            autobinx=False,
            xbins=XBins(
                start=min(pd_series),
                end=2,
                size=0.05
            )
        )
        return data

    # Defines the Bar plot to be visualized
    def trace_bi_bar(self, ob, prefix):
        pd_series = self.object_to_series(ob)
        keys = list(map(lambda x: prefix+str(x), pd_series.index.values))
        data = go.Bar(
            x=keys,
            y=pd_series.values,
            text=pd_series.values,
            opacity=0.6

        )
        return data

    # Plot the data according to a given layout
    @staticmethod
    def plot_data(titles, *args):
        fig = py.tools.make_subplots(rows=len(args[0]), cols=len(args),
                                     subplot_titles=titles)

        for i, col in enumerate(list(args)):
            for j, trace in enumerate(col):
                fig.append_trace(trace, j+1, i+1)

        py.offline.plot(fig)
