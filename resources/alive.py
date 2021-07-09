"""
Author: Resul Emre AYGAN
"""

from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()
parser.add_argument('alive_port', type=int, required=True)


class Alive(Resource):
    """
        Flask-RestFull request handler
        Handles: GET-POST http requests and directs them to concerned modules.
    """

    @staticmethod
    def get():
        params = parser.parse_args()

        if isinstance(params['alive_port'], int):
            return {"message": "I'm alive!"}, 200
        else:
            return {"message": "Wrong port!"}, 404

    @staticmethod
    def post():
        params = parser.parse_args()

        if isinstance(params['alive_port'], int):
            return {"message": "I'm alive!"}, 200
        else:
            return {"message": "Wrong port!"}, 404
