"""
Author: Resul Emre AYGAN
"""

import json
import os.path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import squarify
from matplotlib import cm
from matplotlib.colors import Normalize
from mlxtend.frequent_patterns import apriori, association_rules, fpgrowth
from mlxtend.preprocessing import TransactionEncoder


class Operations:
    def __init__(self):
        pass

    @staticmethod
    def read_data(file_path):
        """
        json reader

        :param file_path: json file path, type str
        :return: data as json format
        """
        print("Reading json file: {}".format(file_path))
        with open(file_path) as data_file:
            data = json.load(data_file)

        return data

    @staticmethod
    def prepare_data(event_json, meta_json):
        """
        makes the data ready for analysis

        :param event_json: event data as json format
        :param meta_json: meta data as json format
        :return: dataset generated from meta json and event json, type df
        """
        print("Preparing data..")

        print("Normalizing event json..")
        event_df = pd.json_normalize(event_json['events'])
        print("Normalizing meta json..")
        meta_df = pd.json_normalize(meta_json['meta'])

        print("Merging event and meta dataframes..")
        merged_df = pd.merge(event_df, meta_df, how='left', on=['productid'])

        print("Preparing the dataframe..")
        # grouped_df = merged_df.groupby('sessionid')['productid'].apply(
        # lambda x: list(set(x.values.tolist()))).to_dict()
        grouped_df = merged_df.groupby('sessionid')['productid'].apply(lambda x: x.values.tolist()).to_dict()

        listed_df = list(map(lambda x: list(filter(None, x)), list(grouped_df.values())))

        encode_ = TransactionEncoder()
        encode_arr = encode_.fit_transform(listed_df)

        encode_df = pd.DataFrame(encode_arr, columns=encode_.columns_)

        data = pd.DataFrame(encode_df, columns=encode_.columns_, dtype=int)

        print("Checking nan data in data frame..")
        if 'nan' in data.columns is not False:
            data.drop('nan', axis=1, inplace=True)

        print("Data prepared!")
        return data

    @staticmethod
    def apriori_algorithm(data, min_support=0.001, use_colnames=True):
        """
        apriori algorithm

        :param data: dataset, type df
        :param min_support: minimum support, type float
        :param use_colnames: dataframe column name, type boolean
        :return: data frequency information, type df
        """
        print("Running the Apriori algorithm..")
        return apriori(data, min_support=min_support, use_colnames=use_colnames)

    @staticmethod
    def fp_growth_algorithm(data, min_support=0.003, use_colnames=True):
        """
        fp growth algorithm

        :param data: dataset, type df
        :param min_support: minimum support, type float
        :param use_colnames: dataframe column name, type boolean
        :return: data frequency information, type df
        """
        print("Running the FP-Growth algorithm..")
        return fpgrowth(data, min_support=min_support, use_colnames=use_colnames)

    @staticmethod
    def generate_association_rules(freq_items, metric, min_threshold=1):
        """
        It generates rules according to the frequency information of the items

        :param freq_items: item frequencies in the dataset, type df
        :param metric: required metric for association rules, type str
        :param min_threshold: the threshold of the association rules metric, type float
        :return: the rule set resulting from the selected algorithm, type df
        """
        print("Generating association rules..")
        return association_rules(freq_items, metric=metric, min_threshold=min_threshold)

    @staticmethod
    def most_add2cart(data, count=20):
        """
        It produces the graph of the most added product information to the cart and the tree map graph of these products

        :param data: dataset, type df
        :param count: number of items to be displayed on the chart, type int
        :return: None
        """
        print("Analyzing the products added to the cart the most..")

        sum_data = data.sum(axis=0).sort_values(ascending=False)[:count]

        plt.figure(figsize=(20, 15))

        s = sns.barplot(x=sum_data.index, y=sum_data.values)
        s.set_xticklabels(s.get_xticklabels(), rotation=90)
        plt.savefig(os.path.join("data", "most_add2cart.png"))

        norm = Normalize(vmin=min(sum_data.values), vmax=max(sum_data.values))
        colors = [cm.Blues(norm(value)) for value in sum_data.values]

        plt.figure(figsize=(13, 13))
        squarify.plot(sizes=sum_data.values, label=sum_data.index, alpha=.7, color=colors)
        plt.title("Tree map of top 20 items")
        plt.axis('off')
        plt.savefig(os.path.join("data", "treemap_add2cart.png"))

    @staticmethod
    def total_rules(rules):
        """
        Generates the total rule infographic
        :param rules: the rule set resulting from the selected algorithm, type df
        :return: None
        """
        rules.plot.scatter("support", "confidence", alpha=0.5, marker="*")
        plt.xlabel("Support")
        plt.ylabel("Confidence")
        plt.title("Association Rules")
        plt.savefig(os.path.join("data", "total_rules.png"))
