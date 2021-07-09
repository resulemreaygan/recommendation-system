"""
Author: Resul Emre AYGAN
"""

from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from waitress import serve

from operations import Operations
from resources.alive import Alive
from resources.recommendation import Recommendation
from utilities.all_constants import AllConstants

app = Flask(__name__)
cors = CORS(app)
api = Api(app)

url_is_alive = r'/alive'
url_is_recomm = r'/recommendation'

if __name__ == '__main__':
    const = AllConstants()
    ops = Operations()

    meta_json = ops.read_data(file_path=const.meta_path)
    event_json = ops.read_data(file_path=const.event_path)

    data = ops.prepare_data(event_json=event_json, meta_json=meta_json)

    ops.most_add2cart(data=data)

    freq_items = ops.fp_growth_algorithm(data=data)
    rule_set = ops.generate_association_rules(freq_items=freq_items, metric="lift")

    ops.total_rules(rule_set)
    print("Generated association rules!")

    api.add_resource(Alive, url_is_alive)
    api.add_resource(Recommendation, url_is_recomm, resource_class_kwargs={
        'data': data, 'freq_items': freq_items, 'rule_set': rule_set})

    serve(app, host='0.0.0.0', port=const.flask_port)
