"""
Author: Resul Emre AYGAN
"""

import json

from flask_restful import Resource, reqparse

from operations import Operations

parser = reqparse.RequestParser()
parser.add_argument('product_ids', type=str, action='append', location='json', required=True)
parser.add_argument('algorithm', type=str, required=False, default='fpgrowth')
parser.add_argument('min_support', type=float, required=False, default=0.003)
parser.add_argument('metric', type=str, required=False, default='lift')
parser.add_argument('metric_threshold', type=float, required=False, default=1.0)
parser.add_argument('product_number', type=int, required=False, default=10)


class Recommendation(Resource):
    """
        Flask-RestFull request handler
        Handles: GET-POST http requests and directs them to concerned modules.
    """

    def __init__(self, data, freq_items, rule_set):
        """
        :param data: dataset generated from meta json and event json, type df
        :param freq_items: item frequencies in the dataset, type df
        :param rule_set: the rule set resulting from the selected algorithm, type df
        """
        self.data = data
        self.ops = Operations()
        self.freq_items = freq_items
        self.rule_set = rule_set

    def check_calculate(self, algorithm, min_support, metric, metric_threshold):
        """
        :param algorithm: algorithm to be used for association rules, type str
        :param min_support: minimum support value for the selected algorithm, type float
        :param metric: required metric for association rules, type str
        :param metric_threshold: the threshold of the association rules metric, type float
        :return: None, freq_items and rule_set are prepared
        """
        generate_assoc = False

        if algorithm == 'apriori':
            self.freq_items = None
            generate_assoc = True
            self.freq_items = self.ops.apriori_algorithm(data=self.data, min_support=min_support)

        if algorithm == 'fpgrowth':
            if min_support != 0.003:
                self.freq_items = None
                generate_assoc = True
                self.freq_items = self.ops.fp_growth_algorithm(data=self.data, min_support=min_support)

        if metric != 'lift' or metric_threshold != 1.0:
            generate_assoc = True

        if generate_assoc:
            self.rule_set = None
            self.rule_set = self.ops.generate_association_rules(freq_items=self.freq_items, metric=metric,
                                                                min_threshold=metric_threshold)
            print("Generated association rules!")

    def post(self):
        params = parser.parse_args()

        self.check_calculate(algorithm=params['algorithm'], min_support=params['min_support'],
                             metric=params['metric'], metric_threshold=params['metric_threshold'])

        temp_df = self.rule_set[self.rule_set['antecedents'] == frozenset(params['product_ids'])].sort_values(
            by="lift", ascending=False)

        if len(params['product_ids']) > 1:
            for index, value in enumerate(params['product_ids']):
                if temp_df.empty:
                    temp_df = self.rule_set[self.rule_set['antecedents'] == frozenset({value})].sort_values(
                        by="lift", ascending=False)
                else:
                    temp_df.append(self.rule_set[self.rule_set['antecedents'] == frozenset({value})].sort_values(
                        by="lift", ascending=False))

        if params['product_number'] > len(temp_df):
            params['product_number'] = len(temp_df)

        return json.dumps(json.loads(temp_df[:params['product_number']].to_json(orient="records")), indent=4), 200
